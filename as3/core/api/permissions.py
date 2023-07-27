from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from as3.core.models import CompanyUsers, Users

class CompanyOrAdminOnlyPermission(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        
        # always return True for admin or superadmin
        if user.is_superadmin_or_admin:
            return True
        
        # if company user
        if user.is_company_profile:
            if CompanyUsers.objects.filter(idUser = user).exists():
                return True
                
        return False

class AdminOnlyPermission(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        if user.is_authenticated:
            if user.is_superuser:
                return True
            if not user.is_superadmin_or_admin:
                self.message = 'Not viewable other than Admin'
                return False
            return True
        return False