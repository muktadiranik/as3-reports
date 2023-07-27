from django.urls import path, include
from as3.core.api.views.company import *
from as3.core.api.views.reports import GlobalReportAPIViewExport

urlpatterns = [
    
    path("filters/values", FilterValueSets.as_view(), name = "filter_values"),
    path("expired_certificates", ExpiredCertificatesListView.as_view(), name = "expired_certificates"),
    
    path("averages", StudentsAverageViewAPI.as_view(), name = "averages"),
    path("students", StudentPerformancesViewAPI.as_view(), name = "student_list"),
    path("performances", PerformanceViewAPI.as_view(), name = "performance_list"),

    path("vehicles", VehicleListView.as_view(), name = "vehicles"),
    
    path("global_report/download", GlobalReportAPIViewExport.as_view(), name = "global_company_report"),
    
    path("courses", CoursesAPIView.as_view(), name = "courses_getapi"),
    path("courses/<int:course_id>/", include("as3.core.api.urls.course"), name = "company_course_api"),
]