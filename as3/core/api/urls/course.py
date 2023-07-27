from django.urls import path
from as3.core.api.views import *

urlpatterns = [
    path("performances", PerformanceViewAPI.as_view(), name = "course_performance_list"),
    path("students", StudentPerformancesViewAPI.as_view(), name = "course_student_list"),
    path("averages", StudentsAverageViewAPI.as_view(), name = "course_averages"),
    path("vehicles", VehicleListView.as_view(), name = "course_vehicles"),
    path("comments", CommentsListApiView.as_view(), name = "comments_list"),
    
    path("global_report/download", 
         GlobalReportAPIViewExport.as_view(), name = "global_course_report"),
]