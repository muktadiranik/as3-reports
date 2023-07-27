import math

from as3.core.api.views.mixins import BaseApiViewMixin
from as3.core.api.views.queries import *
from as3.core.models import *
from as3.core.models.base import Participations
from as3.core.models.records import DataExercises
from django.db.models import Avg, Count, Max, Q
from django.urls import reverse
from rest_framework.response import Response

class StudentPerformancesViewAPI(BaseApiViewMixin):
    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        try:
            data = self.get_student_performers(request, company_id, course_id)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)

        return Response(data = data, status = 200)

    def get_student_performers(self, request, company_id, course_id):
        serialized_out = self.get_queryset(request, company_id, course_id)
        data = {
            "items": serialized_out,
        }
        return data
    
    def get_queryset(self, request, company_id, course_id):
        company_id = self.is_valid_user(request, company_id, course_id)
        query = get_student_performers_query(company_id, course_id, self.get_extra_req_params(request))
        items = self.execute_raw_query(query, self.get_perforer_serialized_data)
        return items
    
    def get_perforer_serialized_data(self, row):
        return {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "code": row[3],
            "company": {
                "id": row[23],
                "name": row[24]
            },
            "group": {
                "id": row[4],
                "name": row[5],
            },
            "team": {
                "id": row[6],
                "name": row[7],
            },
            "course": {
                "id": row[8],
                "eventDate": row[9],  
                "venue": {
                    "id": row[10],
                    "name": row[11],
                    "country": {
                        "name": row[12],
                        "units": row[13]
                    },
                },
                "program":{
                    "id": row[14],
                    "name": row[15],   
                },
            },
            "final_result": round(row[16]) if row[16] else 0,
            "slalom": round(row[17]) if row[16] else 0,
            "lane_change": round(row[18]) if row[18] else 0,
            "reverse": round(row[19]) if row[19] else 0,
            "stress": "High" if row[20] == 1 else "Low",
            "penalties": row[21],
            "final_time": round(row[22]) if row[22] else 0,
            "report": reverse(
                "core:api:student_report", 
                kwargs={"course_id":row[8],"student_code":row[3]})
        }

class PerformanceViewAPI(BaseApiViewMixin):
    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        try:
            data = self.get_performaces(request, company_id, course_id)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
        return Response(data = data, status = 200)

    @staticmethod
    def get_performers_serialized_data(items, pv_avg):
        pvehicles = []
        tries = []
        pv_above_avg = 0
        
        for item in items:
            if item[1] > pv_avg:
                pv_above_avg += 1
                
            pvehicles.append({
                "participant": item[0],
                "value": round(item[1]) if item[1] else 0
            })
            tries.append({
                "participant": item[0],
                "value": round(item[2]) if item[2] else 0
            })
        return pvehicles, pv_above_avg, len(items) - pv_above_avg, tries

    def get_performaces(self, request, company_id, course_id):
        other_params = self.get_extra_req_params(request)
        company_id = self.is_valid_user(request, company_id, course_id)
        
        slalom_avg = get_performamces_avg_query(company_id, course_id, other_params, "Slalom")
        items = self.execute_raw_query(slalom_avg, None)
        avg_slalom_pvehicles, avg_slalom_tries = items[0][0], items[0][1]

        slalom = get_performances_query(company_id, course_id, other_params, "Slalom")
        items = self.execute_raw_query(slalom, None)
        sl_res  = self.get_performers_serialized_data(items, avg_slalom_pvehicles)
        slalom_pvehciles, slalom_pvehciles_aa, slalom_pvehciles_ba, slalom_tries = sl_res
        
        lane_change_avg = get_performamces_avg_query(company_id, course_id, other_params, "Lane Change")
        items = self.execute_raw_query(lane_change_avg, None)
        avg_pvehicles, avg_lc_tries = items[0][0], items[0][1]

        lane_change = get_performances_query(company_id, course_id, other_params, "Lane Change")
        items = self.execute_raw_query(lane_change, None)
        lc_res = self.get_performers_serialized_data(items, avg_pvehicles)
        lc_pvehicles, lc_pvehicles_aa, lc_pvehicles_ba, lc_tries = lc_res
        
        gp_met_std_lcq = get_performances_gp_met_std_query(company_id, course_id, other_params, "Lane Change")
        gp_met_std_lcr = self.execute_raw_query(gp_met_std_lcq, None)
        gp_met_std_lc = gp_met_std_lcr[0][0]
        
        gp_met_std_slalomq = get_performances_gp_met_std_query(company_id, course_id, other_params, "Slalom")
        gp_met_std_slalomr = self.execute_raw_query(gp_met_std_slalomq, None)
        gp_met_std_slalom = gp_met_std_slalomr[0][0]
        
        context = {
            "items":{
                "lane_change": {
                    "pvehicles": lc_pvehicles,
                    "tries": lc_tries,
                    "gp_met_std": round(gp_met_std_lc) if gp_met_std_lc else 0,
                    "avg_tries": round(avg_lc_tries) if avg_lc_tries else 0,
                    "avg_pvehicles": round(avg_pvehicles) if avg_pvehicles else 0,
                    "pvehicles_above_avg": lc_pvehicles_aa,
                    "pvehicles_below_avg": lc_pvehicles_ba,
                },
                "slalom": {
                    "pvehicles": slalom_pvehciles,
                    "tries": slalom_tries,
                    "gp_met_std": round(gp_met_std_slalom) if gp_met_std_slalom else 0,
                    "avg_tries": round(avg_slalom_tries) if avg_slalom_tries else 0,
                    "avg_pvehicles": round(avg_slalom_pvehicles) if avg_slalom_pvehicles else 0,
                    "pvehicles_above_avg": slalom_pvehciles_aa,
                    "pvehicles_below_avg": slalom_pvehciles_ba,
                }
            },
        }
        return context
    
class StudentsAverageViewAPI(BaseApiViewMixin):
    def get_max_performer(self, company_id, course_id, performer_max):
        if company_id:
            max_performer = DataFinalExerciseComputed.objects.select_related(
                "idParticipation").filter(idParticipation__idCompany__id = company_id)
        else:
            max_performer = DataFinalExerciseComputed.objects.select_related(
                "idParticipation").all()
            
        if course_id:
            max_performer = max_performer.filter(idParticipation__idCourse__id = course_id)
            
        max_performer = max_performer.filter(finalResult = performer_max).order_by("idParticipation__idStudent__firstName")
        max_performer_name = ""
        if max_performer.exists():
            max_performer_name = max_performer[0].idParticipation.idStudent.fullName()
            
        return max_performer_name
        
    def get_q_strss_avg(self, company_id, course_id, optional_params):
        performer_stress_avg_q = get_performers_stress_avg_query(company_id, course_id, optional_params)
        performer_stress_avg = self.execute_raw_query(performer_stress_avg_q, None)
        qs_hs,qs_ls = 0, 0
        for qs_stress_avg in list(performer_stress_avg):
            if qs_stress_avg[0] == 0:
                qs_ls = round(qs_stress_avg[1], 2)
            if qs_stress_avg[0] == 1:
                qs_hs = round(qs_stress_avg[1], 2) 
                
        return qs_ls, qs_hs

    def get_global_strss_avg(self):
        global_stress_avg = DataFinalExerciseComputed.objects.all().values("stress").annotate(stress_avg=Avg('finalResult'))
        global_hs,global_ls = 0, 0
        for gstress_avg in global_stress_avg:
            if gstress_avg["stress"] == 0:
                global_ls = round(gstress_avg["stress_avg"], 2)
            if gstress_avg["stress"] == 1:
                global_hs = round(gstress_avg["stress_avg"], 2)
                
        return global_hs,global_ls

    def get_student_averages(self, request, company_id, course_id):
        optional_params = self.get_extra_req_params(request)
        company_id = self.is_valid_user(request, company_id, course_id)
        
        performer_avg_q = get_performers_average_query(company_id, course_id, optional_params)
        performer_avg, performer_max, total_performers, total_courses  = self.execute_raw_query(performer_avg_q, None)[0]

        max_performer_name = self.get_max_performer(company_id, course_id, performer_max)
            
        performer_passcount_q = get_performers_passcount_query(company_id, course_id, optional_params)
        performer_passcount = self.execute_raw_query(performer_passcount_q, None)[0][0]
        
        global_avg = DataFinalExerciseComputed.objects.all().aggregate(
            global_avg = Avg("finalResult")
        )
        
        global_hs,global_ls = self.get_global_strss_avg()

        qs_ls, qs_hs =  self.get_q_strss_avg(company_id, course_id, optional_params)     
        context = {
            "qs": {
                "avg": performer_avg,
                "ls": qs_ls,
                "hs": qs_hs,
                "max": performer_max,
                "pass_count": performer_passcount,
                "total_students": total_performers,
                "top_student": max_performer_name,
                "total_courses": total_courses
            },
            "global": {
                "avg": global_avg.get("global_avg"),
                "hs": global_hs,
                "ls": global_ls,
            },
        }
        return context
    
    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        try:
            data = self.get_student_averages(request, company_id, course_id)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
        return Response(data = data, status = 200)
        
class CoursesAPIView(BaseApiViewMixin):
    @staticmethod
    def get_serialized_data(item, company_id, is_admin):
        cid = item[0]
        if is_admin:
            course_url = reverse("core:admin:course_detail", kwargs = {"company_id": company_id, "course_id": cid})
        else:
            course_url = reverse("core:course_detail", kwargs = {"course_id": cid})
        
        return {
            "id": cid,
            "event_date": item[1].strftime("%B %d, %Y"),
            "program": {
                "id": item[2],
                "name": item[3]
            },
            "venue": {
                "id": item[4],
                "name": item[5],
                "country": {
                    "id": item[7],
                    "name": item[7],
                    "units": item[8]
                }
            },
            "student_count": item[9],
            'detail_url': course_url
        }
    
    def get(self, request, company_id = None, *ar, **kw):
        try:
            is_admin = request.user.is_superadmin_or_admin
            other_params = self.get_extra_req_params(request)
            company_id = self.is_valid_user(request, company_id, None)

            query = get_courses_query(company_id, other_params)
            raw_items = self.execute_raw_query(query, None)
            items = []
            for ritem in raw_items:
                items.append(self.get_serialized_data(ritem, company_id, is_admin))
                
            return Response({"items": items}, status = 200)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
class FilterValueSets(BaseApiViewMixin):
    def get(self, request, company_id = None, *ar, **kw):
        try:
            company_id = self.is_valid_user(request, company_id, None)
            company_instance = Companies.objects.get(id = company_id)

            # groups = GroupStudents.objects.filter(idStudent__idCompany = company_instance).values_list("idGroup__id", "idGroup__name").distinct()
            # teams = TeamStudents.objects.filter(idStudent__idCompany = company_instance).values_list("idTeam__id", "idTeam__name").distinct()
            groups = []
            teams = []
            
            programs = Participations.objects\
                .filter(idCompany = company_instance)\
                    .select_related("idCourse__idProgram")\
                        .values_list("idCourse__idProgram__id", "idCourse__idProgram__name").distinct()
                        
            venues = Participations.objects\
                .filter(idCompany = company_instance)\
                    .select_related("idCourse__idVenue")\
                        .values_list("idCourse__idVenue__id", "idCourse__idVenue__name").distinct()
                        
            res = {
                "groups": groups,
                "teams": teams,
                "locations": venues,
                "programs": programs,
            }
            for key, values in res.items():
                new_values = []
                for val in values:
                    if val[0] == None:
                        break
                    obj = {
                        "key": val[0],
                        "value": val[1],
                    }
                    new_values.append(obj)
                res[key] = new_values
                
            return Response({"items": res}, status = 200)
        
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
class ExpiredCertificatesListView(BaseApiViewMixin):
    def get_perforer_serialized_data(self, row):
        return {
            "id": row[0],
            "name": row[1],
            "event_date": row[2].strftime("%B %d, %Y"),
        }
    
    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        try:
            other_params = self.get_extra_req_params(request)
            company_id = self.is_valid_user(request, company_id, course_id)
            query = get_expired_students_query(company_id, other_params)
            expired_certificates = self.execute_raw_query(query, self.get_perforer_serialized_data)

            query = get_to_be_expired_students_query(company_id, other_params)
            tobe_expired_certificates_list = self.execute_raw_query(query, self.get_perforer_serialized_data)

            context = {
                "last_18_months_students_count": len(expired_certificates),
                "expired_certificates": expired_certificates,
                "to_be_expired_certificates": tobe_expired_certificates_list,
            }
            return Response(data = context, status = 200)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
class VehicleListView(BaseApiViewMixin):
    def get(self, request, company_id = None, course_id = None, *ar, **kw):
        try:
            context = self.get_vehicles(request, company_id, course_id)
        except PermissionError as e:
            return Response(data = {"error": str(e)}, status = 403)
        except Exception as e:
            return Response(data = {"error": str(e)}, status = 500)
        
        return Response(data = context, status = 200)
        
    def get_vehicles(self, request, company_id, course_id):
        company_id = self.is_valid_user(request, company_id, course_id)

        data_ex = None
        if company_id:
            if course_id: # 1 1
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCompany__id = company_id, 
                    idParticipation__idCourse__id = course_id
                )
            else: # 1 0
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCompany__id = company_id)
        else:
            if course_id: # 0 1
                data_ex = DataExercises.objects.filter(
                    idParticipation__idCourse__id = course_id)
        if not data_ex:
            raise Exception("Data excercises not found")

        context = {
            "items": self.get_vehicle_queryset(data_ex),
        }
        return context

    def get_vehicle_queryset(self, data_ex):
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
                img_url = f"/media/{vehicle[0][6]}"
                if not vehicle[0][6]:
                    img_url = "/static/assets/images/car-img-404.jpg"
                vehicle = {
                    "id": vehicle[0][0], 
                    "name": vehicle[0][1], 
                    "lat_acc": vehicle[0][2], 
                    "top_speed_slalom": int(top_speed_slalom), 
                    "top_speed_lnch": int(top_speed_lnch),
                    "image": img_url,
                    "img_path": vehicle[0][6]
                }
                vehicles.append(vehicle)
        return vehicles
                
