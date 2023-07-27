from django.urls import path, include
from as3.core.views import *

urlpatterns = [
    path("", DashboardCompanyIndexView.as_view(), name = "index"),
    path("feedback", FeedbackView.as_view(), name = "feedback"),
]