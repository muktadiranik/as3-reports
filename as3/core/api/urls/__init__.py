from django.urls import path, include
app_name = 'api'

urlpatterns = [
    path("reports/", include('as3.core.api.urls.reports')),
    path("company/", include('as3.core.api.urls.company')),
    path("admin/", include('as3.core.api.urls.admin')),
    path("", include('as3.core.api.urls.base')),
]