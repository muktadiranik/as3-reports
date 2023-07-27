from django.urls import path, include
from as3.core.api.views.admin import *

app_name = "admin_api"

urlpatterns = [
    path("users", UsersListAPIView.as_view(), name = "user_list_api"),
    path("user/<int:pk>/", UserAPIView.as_view(), name = "user_api"),
    path("user/<int:pk>/send-welcome-email", UserSendWelcomeEmail.as_view(), name = "user_api"),
    
   
    path("vehicles/", VehcilesAdminListCreateAPIView.as_view(), name = "vehicles_list_api"),
    path("vehicle/<int:pk>", VehcilesAdminAPIView.as_view(), name = "vehicle_api"),
    
    path("course_uploads/", CourseUploadListAPIView.as_view(), name = "course_uploads_list"),
    path("course_uploads/<int:pk>/", CourseUploadAPIView.as_view(), name = "course_upload"),
    
    path("courses/<int:course_id>/", include('as3.core.api.urls.course')),
    
    path("companies", CompanyReportListAPIView.as_view(), name = "company_report_list_api"),
    path("company/<int:company_id>/", include("as3.core.api.urls.company"), name = "admin_company"),
    path("company/<int:company_id>/", include("as3.core.api.urls.reports"), name = "admin_report"),
]