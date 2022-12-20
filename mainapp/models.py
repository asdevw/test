import datetime
import pytz as pytz
from django.db import models
from django.utils import timezone



class DatesModelMixin(models.Model):
    class Meta:
        abstract = True

    created = models.DateTimeField(verbose_name="date of creation")
    updated = models.DateTimeField(verbose_name="Last update date")

    def save(self, *args, **kwargs):
        if not self.id:  # When an object is first created, it doesn't have an id yet.
            self.created = timezone.now()  # enter the date of creation
        self.updated = timezone.now()  # set update date
        return super().save(*args, **kwargs)


MOBILE_OPERATORS = (
    (900, 900),
    (901, 901),
    (902, 902),
    (903, 903),
    (904, 904),
    (905, 905),
    (906, 906),
    (908, 908),
    (909, 909),
    (910, 910),
    (911, 911),
    (912, 912),
    (913, 913),
    (914, 914),
    (915, 915),
    (916, 916),
    (917, 917),
    (918, 918),
    (919, 919),
    (920, 920),
    (921, 921),
    (922, 922),
    (923, 923),
    (924, 924),
    (925, 925),
    (926, 926),
    (927, 927),
    (928, 928),
    (929, 929),
    (930, 930),
    (931, 931),
    (932, 932),
    (933, 933),
    (934, 934),
    (936, 936),
    (937, 937),
    (938, 938),
    (939, 939),
    (941, 941),
    (950, 950),
    (951, 951),
    (952, 952),
    (953, 953),
    (954, 954),
    (955, 955),
    (956, 956),
    (958, 958),
    (960, 960),
    (961, 961),
    (962, 962),
    (963, 963),
    (964, 964),
    (965, 965),
    (966, 966),
    (967, 967),
    (968, 968),
    (969, 969),
    (970, 970),
    (971, 971),
    (977, 977),
    (978, 978),
    (980, 980),
    (981, 981),
    (982, 982),
    (983, 983),
    (984, 984),
    (985, 985),
    (986, 986),
    (987, 987),
    (988, 988),
    (989, 989),
    (991, 991),
    (992, 992),
    (993, 993),
    (994, 994),
    (995, 995),
    (996, 996),
    (997, 997),
    (998, 998),
    (999, 999),
)


class MobileOperatorChoices(models.Model):
    code = models.IntegerField(verbose_name="Mobile operator codes", primary_key=True)

    def __str__(self):
        return f"({self.code})"







# MALING

class Mailing(DatesModelMixin):


    start = models.DateTimeField(verbose_name="Date and time the mailing was launched")
    end = models.DateTimeField(verbose_name="Date and time of the end of the mailing")
    message_text = models.TextField(verbose_name="Message text to be delivered to the client", null=False)
    operator_filter = models.ManyToManyField(MobileOperatorChoices, verbose_name="Client filter by operator code",null=True, blank=True, default=None)
    tag_filter = models.CharField(verbose_name="Filter customers by tag", max_length=100, null=True, blank=True,default=None)
    time_interval_start = models.TimeField(verbose_name="Time interval start", default=datetime.time(00, 00))
    time_interval_end = models.TimeField(verbose_name="End of timeslot", default=datetime.time(23, 59, 59))


    class Meta:
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"




class Client(DatesModelMixin):


    TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
    phone = models.BigIntegerField(max_length=13, verbose_name="Phone number", unique=True, null=False)
    mobile_operator = models.IntegerField(verbose_name="Mobile operator code", choices=MOBILE_OPERATORS)
    tag = models.CharField(verbose_name="Tag (arbitrary label)", max_length=30)
    timezone = models.CharField(max_length=32, choices=TIMEZONES, default='UTC')


    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return self.phone

class Message(models.Model):


    class Status(models.IntegerChoices):
        not_sent = 0, "Not sent"
        sent = 1, "Sent"
    message_sent_date = models.DateTimeField(verbose_name="Date and time the message was sent")
    status = models.PositiveSmallIntegerField(verbose_name="Shipping status", choices=Status.choices, default=Status.not_sent)
    mailing = models.ForeignKey(Mailing,verbose_name="Newslatter",on_delete=models.PROTECT,related_name="messages")
    client = models.ForeignKey(Client,verbose_name="Client",on_delete=models.PROTECT,related_name="messages")
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"


    def __str__(self):
        return self.client
