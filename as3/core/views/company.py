from django.views.generic import View
from django.shortcuts import render, get_object_or_404
import json

from .mixins import LoginRequiredMixinV2
from as3.core.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect
from as3.core.models import Companies
from django.contrib import messages #import messages


COMPANY_PROFILE = 2
class DashboardCompanyIndexView(LoginRequiredMixinV2, View):
    login_url = '/accounts/login/'
    redirect_field_name = '/'
    template_name = "core/company/index.html"
    
    def get(self, request, company_id = None, *ar, **kw):
        context = {}
        if company_id:
            company_instance = get_object_or_404(Companies, id = company_id)
        else:
            company_userinstance = get_object_or_404(CompanyUsers, idUser = request.user)
            company_instance = company_userinstance.idCompany
            
        if not request.session.get("user-type", None):
            request.session["user-type"] = "company"
            
        students_count = Participations.objects.filter(idCompany = company_instance).count()
        top_students = DataFinalExerciseComputed.objects.select_related("idParticipation").filter(
            idParticipation__idCompany = company_instance).order_by(
                "-finalResult", "idParticipation__idStudent__firstName").values_list(
                    "idParticipation__idStudent__firstName", 
                    "idParticipation__idStudent__lastName", "finalResult")[:5]
        
        context.update({
            "user_type": request.session["user-type"],
            "page_type": "company",
            "company": company_instance,
            "total_students": students_count,
            "top_students": top_students,
        })
        return render(request, self.template_name, context)

class FeedbackView(View):
    template_name = "pages/feedback.html"

    def is_valid_user(self, request):
        cuser = CompanyUsers.objects.filter(idUser = request.user)
        if not cuser.exists():
            raise Http404
        company_instance = get_object_or_404(Companies, id = cuser[0].id)
        return company_instance
        
    def get(self, request, *a, **k):
        if request.session and request.session["user-type"] == "admin":
            raise Http404
        context = {
            "company": self.is_valid_user(request),
        }
        return render(request, self.template_name, context)
        
    def post(self, request, *a, **k):
        try:
            data = dict(request.POST)
            name = ""
            rating = 0
            if "fullName" in data.keys():
                name = data["fullName"][0] 
            if "rating" in data.keys():
                rating = data["rating"][0]
            feedback = Feedback(
                idUser = request.user,
                idCompany = self.is_valid_user(request),
                name = name, 
                likeMost = data["likeMost"][0],
                didntLike = data["didntLike"][0],
                futureSuggestion = data["futureSuggestion"][0],
                overallFeedback = data["overallFeedback"][0],
                rating = rating,
            )
            feedback.save()
        except Exception as e:
            messages.error(request, f"Unable to save feedback, {str(e)}" )
            return render(request, self.template_name, {})
        
        return HttpResponseRedirect("/")