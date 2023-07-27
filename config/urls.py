"""as3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth.views import PasswordResetCompleteView 
from django.conf import settings
from django.conf.urls.static import static
from as3.core.views.template import *

handler404 = 'as3.core.views.template.handler404'
handler500 = 'as3.core.views.template.handler500'
handler403 = 'as3.core.views.template.handler403'
handler400 = 'as3.core.views.template.handler400'

urlpatterns = [
    path('superadmin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('', include('as3.core.urls')),
    path('accounts/', include('as3.accounts.urls', namespace='company-accounts')),
    path('admin/accounts/', include('as3.accounts.urls', namespace='admin-accounts')),
    path('password_reset/complete/', PasswordResetCompleteView.as_view(template_name='accounts/password/password_reset_complete.html'), name='password_reset_complete'),  
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
