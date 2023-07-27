from django.urls import path, include
app_name = 'core'

urlpatterns = [

    path("core/v1/api/", include('as3.core.api.urls')),
    path("course/", include('as3.core.urls.courses')),
    path("student/", include('as3.core.urls.students')),
    path("admin/", include('as3.core.urls.admin')),
    
    path("", include('as3.core.urls.company')),

    # path("dataFEPc/", DataFinalPcView.as_view()),
    # path("dataEPc/", DataExercisePCView.as_view()),
    # path("personalReport/", GetPersonalReport.as_view()),
]