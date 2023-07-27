from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views 
from .views import (
    LoginView,
    logout_view,
    profile_view,
    password_reset_request
)

app_name = 'account'

urlpatterns = [
    path("login/", LoginView.as_view(), name = "login"),
    path("logout/", logout_view, name = "logout"),
    path("profile/", profile_view, name = "profile"),
    
    path("password_reset", password_reset_request, name="password_reset"),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password/password_reset_done.html'), 
         name='password_reset_done'
    ),
    path(
        'password_reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password/password_reset_confirm.html"), 
        name='password_reset_confirm', 
    ),
    # path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password/password_reset_complete.html'), name='password_reset_complete'),  
]