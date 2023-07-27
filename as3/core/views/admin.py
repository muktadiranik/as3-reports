
from django.views.generic import View
from .mixins import AdminLoginRequiredMixinV2
from django.shortcuts import render, get_object_or_404
from as3.core.models import *


class AdminDashboardView(AdminLoginRequiredMixinV2, View):
    login_url = '/admin/accounts/login/'
    redirect_field_name = 'admin'
    template_name = "core/admin/index.html"
    
    def get(self, request, *ar, **kw):
        request.session["user-type"] = "admin"
        all_companies = Companies.objects.all().order_by("name")
        all_countries = Countries.objects.all().order_by("name")
        feedbacks = Feedback.objects.all()
        
        profile = request.user.profile
            
        context = {
            "user_type": request.session["user-type"],
            "profile": profile,
            "companies": all_companies,
            "countries": all_countries,
            "feedbacks": feedbacks
        }
        
        return render(request, self.template_name, context)
