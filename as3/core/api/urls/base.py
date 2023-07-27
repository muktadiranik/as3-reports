from django.urls import path, include
from as3.core.api.views.base import *

urlpatterns = [
    path("language-change", LanguageChangeView.as_view(), name = "language_change"),
    
    path("programs", ProgramsAPIView.as_view(), name = "programs"),
    path("venues", VenuesAPIView.as_view(), name = "venues"),
    path("companies", CompanyAPIView.as_view(), name = "companies"),
    
]