from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("", views.PaycomView.as_view(), name="paycom"),
]
