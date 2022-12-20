from django.urls import path
from .views import ClientCreateView,ClientView,MailingListView,MailingDetailView,MailingCreateView

urlpatterns = [
    path("",ClientCreateView.as_view()),
    path("client/<pk>", ClientView.as_view()),
    path("create", MailingCreateView.as_view()),
    path("stat", MailingListView.as_view()),
    path("stat/<pk>",MailingDetailView.as_view(),)
]
