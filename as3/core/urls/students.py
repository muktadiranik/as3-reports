from django.urls import path
from as3.core.views.students import *


urlpatterns = [
    path("", CompanyStudentView.as_view(), name = "students"),
]