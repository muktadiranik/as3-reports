
from django.views.generic import View
from .mixins import LoginRequiredMixinV2
from django.shortcuts import render, get_object_or_404
from as3.core.models import *
from django.http import Http404
import math

class CourseDetailView(LoginRequiredMixinV2, View):
    login_url = '/accounts/login/'
    redirect_field_name = '/'
    template_name = "core/company/course.html"

    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        context = {}
        company_instance = None
        if request.user.is_superadmin_or_admin:
            if company_id and course_id: #admin want to see company's course
                company_instance = get_object_or_404(Companies, id = company_id)
            request.session["user-type"] = "admin"
        else:
            company_userinstance = get_object_or_404(CompanyUsers, idUser = request.user)
            company_instance = company_userinstance.idCompany
            request.session["user-type"] = "company"
        
        course_instance = get_object_or_404(Courses, pk = course_id)
        course_students = Participations.objects.filter(idCourse = course_instance).values_list("idStudent")

        if company_instance:
            context.update({
                "company": company_instance,
                "page_type": "course"
            })
        else:
            context.update({
                "page_type": "course-only"
            })
            
        context.update({
            "user_type": request.session["user-type"],
            "course": course_instance,
            "vehicles": self.get_vehicles(company_instance, course_instance),
            "course_students": course_students,
        })
        return render(request, self.template_name, context)
    
    
    def get_vehicles(self, company_instance, course_instance):
        if company_instance:
            if course_instance: # 1 1
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCompany = company_instance, 
                    idParticipation__idCourse = course_instance
                )
            else: # 1 0
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCompany = company_instance)
        else:
            if course_instance: # 0 1
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCourse = course_instance)
            else:   
                data_ex = None

        if not data_ex:
            return []
        
        vehicleLookUp = data_ex.select_related(
            "idVehicle", 
            "idExerciseSelected", "idExerciseSelected__idExercise"
            ).values_list(
                "idVehicle__id", 
                "idVehicle__name", 
                "idVehicle__latAcc",
                "idExerciseSelected__chord",
                "idExerciseSelected__mo",
                "idExerciseSelected__idExercise__name",
                "idVehicle__image"
            ).order_by("idExerciseSelected__idExercise__name").distinct()
        vehicles_dict = {}
        for vehicle in vehicleLookUp:
            if vehicle[1] in vehicles_dict.keys():
                vehicles_dict[vehicle[1]].append(vehicle)
            else:
                vehicles_dict.update({vehicle[1]: [vehicle,]})
        vehicles = []
        for vehicle in vehicles_dict.values():
            if len(vehicle) == 2:
                slalom = 1
                lc = 0
                rd_slalom = (vehicle[slalom][3]**2) / (8*vehicle[slalom][4]) + (vehicle[slalom][4]/2)
                top_speed_slalom = math.sqrt(rd_slalom*15*vehicle[slalom][2])
                rd_lnch = (vehicle[lc][3]**2) / (8*vehicle[lc][4]) + (vehicle[lc][4]/2)
                top_speed_lnch = math.sqrt(rd_lnch*15*vehicle[lc][2])
                vehicle = (
                    vehicle[0][0], vehicle[0][1], 
                    vehicle[0][2], int(top_speed_slalom), 
                    int(top_speed_lnch),
                    f"/media/{vehicle[0][6]}" if vehicle[0][6] else "" 
                )
                vehicles.append(vehicle)
        return vehicles
        