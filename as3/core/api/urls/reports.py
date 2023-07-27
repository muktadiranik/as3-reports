from django.urls import path
from as3.core.api.views.reports import *

urlpatterns = [
    # path("download/company/report", GlobalReportViewExport.as_view(), name = "global_report_export"),
    path(
        "course/<int:course_id>/student/<str:student_code>/download", 
        StudentReportDownload.as_view(), name = "student_report"
    ),
    path("student_report/multiple/download", 
        StudentMultipleReportDownload.as_view(), name = "student_report_multiple"),
]