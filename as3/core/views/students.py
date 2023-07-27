
from django.views.generic import View
from .mixins import LoginRequiredMixinV2
from django.shortcuts import render, get_object_or_404
from as3.core.models import *
from django.http import Http404

COMPANY_PROFILE = 2

class CompanyStudentView(LoginRequiredMixinV2, View):
    login_url = '/accounts/login/'
    redirect_field_name = '/'
    template_name = "core/company/students.html"
    
    def get(self, request, company_id = None, *ar, **kw):
        if company_id:
            company_instance = get_object_or_404(Companies, id = company_id)
        else:
            company_userinstance = get_object_or_404(CompanyUsers, idUser = request.user)
            company_instance = company_userinstance.idCompany
        
        context = {
            "user_type": request.session["user-type"],
            "page_type": "course",
            "company": company_instance,
            "performance_url": reverse("core:api:student_report"),
        }
        return render(request, self.template_name, context)