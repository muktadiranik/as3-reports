from django.urls import path, include
from as3.core.views.admin import *
from as3.core.views.company import *
from as3.core.views.courses import CourseDetailView

app_name = "admin"

urlpatterns = [
    path('', AdminDashboardView.as_view(), name = "admin_index"),
    path("company/<int:company_id>/", include("as3.core.urls.company"), name = "admin_company"),
    path('company/<int:company_id>/course/', include("as3.core.urls.courses"), name = "admin_company_course"),
    path('company/<int:company_id>/students/', include("as3.core.urls.students"), name = "admin_company_students"),
    
    path("course/<int:course_id>/", CourseDetailView.as_view(), name = "admin_course_upload_view"),
    
]