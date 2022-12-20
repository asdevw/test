import datetime
from celery import states
from celery.worker.control import revoke
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from mainapp import tasks
from .models import Client, Mailing, Message
from .serializers import ClientCreateSerializer, ClientSerializer, MailingCreateSerializer,MailingListSerializer, MailingSerializer

@extend_schema_view(
    post=extend_schema(
        description="Creates a mailing client",
        summary="Creates a mailing client"))
class ClientCreateView(CreateAPIView):
    model = Client
    serializer_class = ClientCreateSerializer


@extend_schema_view(
    get=extend_schema(
        description="Gets information about the client (time zone, phone number, tag)",
        summary="Gets a client"),
    delete=extend_schema(
        description="Removes a client from the database",
        summary="Deletes a client"),
    put=extend_schema(
        description="Changes client settings (time zone, phone number, tag)",
        summary="Changes the client"))
class ClientView(RetrieveUpdateDestroyAPIView):
    model = Client
    serializer_class = ClientSerializer
    http_method_names = ["get", "put", "delete"]
    def get_queryset(self):
        return Client.objects.all()

class MailingCreateView(CreateAPIView):
    model = Mailing
    serializer_class = MailingCreateSerializer

    def perform_create(self, serializer):
        obj = serializer.save()
        return obj.id  # return id

    @extend_schema(
        description="Create a mailing list if the mailing list was created on a date that has not yet arrived, it will be produced when the date arrives, otherwise it will start immediately, after the expiration of the mailing period, it will be immediately terminated .",
        summary="Creating a mailing list")
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mailing_id = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        start = serializer.data.get("start")
        end = serializer.data.get("end")
        start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
        if start_date > end_date:
            try:
                raise ValidationError("Mistake! The start time of the mailing is later than the end time")
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        time_interval_start = datetime.datetime.strptime(serializer.data.get("time_interval_start"), "%H:%M:%S").time()
        time_interval_end = datetime.datetime.strptime(serializer.data.get("time_interval_end"), "%H:%M:%S").time()
        if time_interval_start > time_interval_end:
            try:
                raise ValidationError("Mistake! Incorrect broadcast time interval set")
            except ValidationError as e:
                return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        if start_date <= datetime.datetime.now():
            tasks.prepare_mailing.delay(serializer.data, end)
        else:
            tasks.prepare_mailing.apply_async(args=(serializer.data, end), eta=start_date, task_id=str(mailing_id))
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def get_queryset(self):
        return Mailing.objects.all()

class MailingListView(ListAPIView):
    model = Mailing
    serializer_class = MailingListSerializer

    @extend_schema(
        description="Mailing statistics, how many letters were delivered, how many were not delivered",
        summary="Mailing stats")
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = MailingListSerializer(queryset, many=True)
        response_list = serializer.data
        not_sent_count = Message.objects.filter(status=Message.Status.not_sent).count()
        sent_count = Message.objects.filter(status=Message.Status.sent).count()
        for response in response_list:
            response["not_sent_messages_count"] = not_sent_count
            response["sent_messages_count"] = sent_count
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return Mailing.objects.all()

class MailingDetailView(RetrieveUpdateDestroyAPIView):
    model = Mailing
    serializer_class = MailingSerializer
    http_method_names = ["get", "put", "delete"]

    @extend_schema(
        description="Single mailing statistics, information on each mailing message",
        summary="Single mailing statistics")
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        not_sent_count = Message.objects.filter(mailing_id=data["id"], status=Message.Status.not_sent).count()
        sent_count = Message.objects.filter(mailing_id=data["id"], status=Message.Status.sent).count()
        data["not_sent_messages_count"] = not_sent_count
        data["sent_messages_count"] = sent_count
        messages = Message.objects.filter(mailing_id=data["id"]).order_by('status').values()
        data["messages_statistic"] = messages
        return Response(data)

    @extend_schema(
        description="Changes the mailing list (text, dates, filters), if the mailing list has not yet been sent, cancels,task to the old mailing list and launches the modified one, as well as the creation of a new one",
        summary="Changes mailing list")
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        try:
            revoke(state=states.PENDING, task_id=str(serializer.data["id"]))
            start = serializer.data.get("start")
            end = serializer.data.get("end")
            start_date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
            end_date = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%SZ")
            if start_date > end_date:
                try:
                    raise ValidationError("Mistake! The start time of the mailing is later than the end time")
                except ValidationError as e:
                    return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
            if start_date <= datetime.datetime.now():
                tasks.prepare_mailing.delay(serializer.data, end)
            else:
                tasks.prepare_mailing.apply_async(args=(serializer.data, end), eta=start_date,task_id=serializer.data["id"])
            return Response(serializer.data)
        except TypeError as e:
            return Response("Mistake! Newsletter is already running or has not been created", status=status.HTTP_400_BAD_REQUEST)
    @extend_schema(
        description="Deletes the mailing list, but if the mailing list has already been sent, the task will not be canceled",
        summary="Deletes the newsletter")
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        try:
            revoke(state=states.PENDING, task_id=str(serializer.data["id"]))
            return Response(data="The newsletter has been deleted and will not be processed.", status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data="Newsletter deleted from the database, but messages have already been sent",status=status.HTTP_204_NO_CONTENT)
    def get_queryset(self):
        return Mailing.objects.all()
