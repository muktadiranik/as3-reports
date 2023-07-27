from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from as3.core.models import CompanyUsers

class LoginRequiredMixinV2(LoginRequiredMixin):
    def __init__(self) -> None:
        super().__init__()
        
    def dispatch(self, request, company_id = None, course_id = None, *args, **kwargs):
        
        """
        admin:
            - /admin/company/<company_id> 1 0
            - /admin/company/<company_id>/course/<course_id> 1 1
            - /admin/course/<course_id> 0 1
            - /admin 0 0
        company user:
         / 0 0
         /course/<course_id> 0 1
        Returns:
            _type_: _description_
        """
        
        usr = request.user
        if not usr.is_authenticated:
            return self.handle_no_permission()

        # admin viewing course and company dashboard
        if usr.is_superadmin_or_admin: 
            if company_id or course_id:
                return super().dispatch(request, company_id, course_id, *args, **kwargs)
            else:
                return redirect("core:admin:admin_index")
            
        if usr.is_company_profile:
            if CompanyUsers.objects.filter(idUser__id = usr.id).exists():
                return super().dispatch(request, company_id, course_id, *args, **kwargs)
            return self.handle_no_permission()
    
        return self.handle_no_permission()
    
    
class AdminLoginRequiredMixinV2(LoginRequiredMixin):
    def __init__(self) -> None:
        super().__init__()
        
    def dispatch(self, request, *args, **kwargs):
        usr = self.request.user
        
        if not usr.is_authenticated:
            return self.handle_no_permission()
        
        if usr.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        
        if not usr.is_superadmin_or_admin:
            return self.handle_no_permission()
        
        return super().dispatch(request, *args, **kwargs)