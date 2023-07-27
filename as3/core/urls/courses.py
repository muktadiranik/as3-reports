from django.urls import path
from as3.core.views.courses import *


urlpatterns = [
    # courses
    path("<int:course_id>", CourseDetailView.as_view(), name = "course_detail"),
]