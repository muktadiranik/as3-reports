import ast
import json
import logging
import sys
import traceback
import timeago
import shortuuid
from as3.core.api.permissions import AdminOnlyPermission
from as3.core.api.serializers import VehiclesSerializer
from as3.core.db_utils.db_populate import CourseDataUploader
from as3.core.models import *
from as3.core.api.views.utils import send_welcome_email
from config.celery import celery_app
from django.db import connection, transaction
from django.db.models import Q
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

# TODO  save user depending on the profile. Only partially company is done

class UserAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)
    
    def get(self, request, pk):
        if not Users.objects.filter(id = pk).exists():
            return Response(status = 404)
        user = Users.objects.get(id = pk)
        puser = Users.objects\
            .filter(active = True)

        if not puser.exists():
            return Response(status = 404)
            
        puser = puser.values_list(
            "profile", "username", "active", "name", "idCountry__name", "id")
        user = {
            "id": puser[0][5],
            "username": puser[0][1],
            "name": puser[0][3],
            "country": puser[0][4],
            "profile": [u[0] for u in puser]
        }
        return Response(data = user, status = 200)
    
    def delete(self, request, pk):
        try:
            user = Users.objects.get(id = pk)
            if request.user == user: # self record can't be deleted
                return Response(data = {"status": "error", "error": f"You don't have permission to delete this record" }, status = 400)
            # admin can't be delete superadmin profile
            if user.is_superadmin_profile and not request.user.is_superadmin_profile:
                return Response(data = {"status": "error", "error": f"You don't have permission to delete this record" }, status = 400)
            
            with transaction.atomic():
                CompanyUsers.objects.filter(idUser = user).delete()
                user.delete()
            
            return Response(data = {"status": "success"}, status = 200)
        except Users.DoesNotExist:
            return Response(data = {"status": "error", "error": "User does not exists"}, status = 500)
        except Exception as e:
            return Response(data = {"status": "error", "error": str(e)}, status = 500)
            
    def put(self, request, pk):
        data = dict(request.data)
        profile = data.get("profile", [])
        country = data.get("country", [])
        company_id = data.get("company", [])
        name = data.get("name", [])
        email = data.get("email", [])
        # todo
        if not profile or len(profile) != 1:
            return Response(data = {"status": "error", "error": "User should have a profile"}, status = 400)
        try:
            with transaction.atomic():
                user = Users.objects.get(id = pk)
                if user.is_superadmin_profile and not request.user.is_superadmin_profile:
                    return Response(
                        data = {"status": "error", 
                                "error": f"You don't have permission to edit this record" 
                        }, status = 400
                    )
                if user == request.user and not user.is_superadmin_profile:
                    return Response(
                        data = {"status": "error", 
                                "error": f"You don't have permission to edit this record" 
                        }, status = 400
                    )
                if email:   user.email = email[0]
                if name:    user.name = name[0]
                if country: user.idCountry = Countries.objects.get(name__icontains = country[0])
                if profile: user.profile = profile[0]
                try:
                    user.save()
                except Exception as e:
                    return Response(
                        data = {"status": "error", 
                                "error": f"Problem in updating user: Error code: 400. {str(e)}"
                            }, status = 400
                    )
                try:
                    # unlink the old user associated with company 
                    if CompanyUsers.objects.filter(idUser = user).exists():
                        CompanyUsers.objects.filter(idUser = user).delete()
                    
                    if company_id and Companies.objects.filter(id = company_id[0]).exists():
                        company = Companies.objects.get(id = company_id[0])
                        if not CompanyUsers.objects.filter(idUser = user, idCompany = company):
                            CompanyUsers.objects.create(idUser = user, idCompany = company)
                except Exception as e:
                    print(e)
                    return Response(
                        data = {"status": "error", 
                            "error": f"Problem in updating/deleting profile: Error code: 400. {str(e)}"
                        }, status = 400
                    )
            return Response(data = {"status": "success"}, status = 200)
        except Exception as e:
            print(str(e))
            return Response(data = {"status": "error", "error": str(e)}, status = 500)
        
class UsersListAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)

    def get(self, request):
        serialized_out = self.__get_queryset(request)
        data = {
            "items": serialized_out,
        }
        return Response(data = data, status = 200)            
    
    def post(self, request):
        try:
            data = dict(request.POST)
            profile = data.get("profile", [])
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            if not profile or len(profile) != 1:
                return Response(data = {"status": "error", "error": "User should have a profile"}, status = 400)
            if Users.objects.filter(Q(username = data.get("username")[0]) | Q(email = data.get("email")[0])).exists():
                return Response(data = {"status": "error", "error": "User with this username/email already exists."}, status = 400)
            if not username:
                return Response(data = {"status": "error", "error": "Please provide username"}, status = 400)
            if not email:
                return Response(data = {"status": "error", "error": "Please provide email"}, status = 400)
            if not password:
                return Response(data = {"status": "error", "error": "Please provide Password"}, status = 400)

            with transaction.atomic():
                user = Users(
                    username = username[0],
                    email = email[0],
                    name = data.get("name")[0],
                    idCountry = Countries.objects.get(name__icontains = data.get("country")[0]),
                    profile = profile[0]
                )
                user.set_password(password[0])
                user.save()
                company_id = data.get("company", None)
                if company_id and Companies.objects.filter(id = company_id[0]).exists():
                    company = Companies.objects.get(id = company_id[0])
                    if not CompanyUsers.objects.filter(idUser = user, idCompany = company):
                        CompanyUsers.objects.create(idUser = user, idCompany = company)
                send_welcome_email(user)    
            return Response(data = {"status": "success"}, status = 201)
        except Exception as e:
            print(e)
            return Response(data = {"status": "error", "error": str(e)}, status = 500)
    
    def __get_users(self, profile_users):
        users = []
        profile_users = profile_users.values_list(
            "id", "profile", "username", "active",
            "name", "idCountry__name", "email", "last_login"
        )
        for user in profile_users:
            last_login = None
            if user[7]:
                last_login = timeago.format(user[7].replace(tzinfo=None))
            user_related_obj = None
            if user[1] == "Company":
                comp = CompanyUsers.objects.filter(idUser = user[0])
                if comp.exists():   user_related_obj = comp[0].idCompany
            users.append({
                "id": user[0],
                "profile": user[1],
                "username": user[2],
                "active": user[3],
                "name": user[4],
                "country": user[5],
                "email": user[6],
                "company": {
                    "id": user_related_obj.id if user_related_obj else None,
                    "name": user_related_obj.name if user_related_obj else None,
                },
                "last_login": last_login
            })
        return users
    
    def __get_queryset(self, request):
        profile = request.query_params.get('profile', None)
        country = request.query_params.get('country', None)
        profile_users = Users.objects\
            .select_related("idCountry",)\
            .all()
        if country and not country == "all":
            try:
                country_obj = Countries.objects.get(name = country)
            except Countries.DoesNotExist:  return []
            profile_users = profile_users.filter(idCountry = country_obj)
        if profile and not profile == "all":
            profile_users = profile_users.filter(profile = profile)
                    
        profile_users = profile_users.order_by("-id")
        return self.__get_users(profile_users)
    
    
class UserSendWelcomeEmail(APIView):
    permission_classes = (AdminOnlyPermission,)
        
    def post(self, request, pk = None, *arg, **kw):
        if not pk:
            return Response(
                data = {"status": "error", 
                        "error": f"User id is not provided" 
                }, status = 400
            )
        try:
            user = Users.objects.get(id = pk)
        except Users.DoesNotExist:
            return Response(
                data = {"status": "error", 
                        "error": f"User does not exists with given user id" 
                }, status = 400
            )
        send_welcome_email(user)
        return Response(data = {}, status=200)
            
class CompanyReportListAPIView(ListAPIView, LimitOffsetPagination):
    permission_classes = (AdminOnlyPermission,)
    # pagination_class = StandardResultsSetPagination
    def get(self, request):
        serialized_out = self.get_queryset(request)
        data = {
            "items": serialized_out,
        }
        return Response(data = data, status = 200)
    
    @staticmethod
    def get_serialized_data(row, is_admin):
        if is_admin:
            report_url = reverse("core:api:admin_api:global_company_report", kwargs={"company_id": row[0]})
        else:
            report_url = reverse("core:api:api:global_company_report")
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "final_result": row[3],
            "report_url": report_url
        }

    def get_queryset(self, request):
        query =  f"""
            SELECT company.id, company.name, u.email, AVG(DFEC.finalResult) company_avg
            FROM {DataFinalExerciseComputed._meta.db_table} DFEC
            JOIN {Participations._meta.db_table} participation on participation.id = DFEC.idParticipation
            JOIN {Students._meta.db_table} s ON  participation.idStudent = s.id 
            JOIN {Companies._meta.db_table} company ON company.id = participation.idCompany
            LEFT JOIN {CompanyUsers._meta.db_table} company_user ON company_user.idCompany = participation.idCompany
            LEFT JOIN {Users._meta.db_table} u ON u.id = company_user.idUser
            GROUP BY company.id
            ORDER BY company.name ASC;
        """
        cursor = connection.cursor()
        cursor.execute(query.strip(" \n\t"))
        items = []
        is_admin = request.user.is_superadmin_or_admin
        for row in cursor:
            items.append(self.get_serialized_data(row, is_admin))
        return items

class VehcilesAdminListCreateAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)
    serializer_class = VehiclesSerializer
    # pagination_class = StandardResultsSetPagination

    def get(self, request, *ar, **kw):
        context = self.get_vehicles()
        return Response(data = context, status = 200)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_vehicles(self):
        vehicles = Vehicles.objects.filter(active = True).order_by("name")
        serialzed_vehicles = self.serializer_class(vehicles, many = True).data
        for vehicle in serialzed_vehicles:
            vehicle["url"] = reverse("core:api:admin_api:vehicle_api", kwargs={"pk":vehicle["id"]})
        context = {
            "items": serialzed_vehicles,
        }
        return context


class VehcilesAdminAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)
    serializer_class = VehiclesSerializer
    
    def get(self, request, pk, *ar, **kw):
        context = self.get_vehicle(pk)
        return Response(data = context, status = 200)
    
    def get_vehicle(self, pk):
        vehicle = Vehicles.objects.get(pk = pk)
        serialzed_vehicle = self.serializer_class(vehicle)
        context = {
            "items": serialzed_vehicle.data,
        } 
        return context

    def put(self, request, pk):
        try:
            instance = Vehicles.objects.get(pk = pk)
        except Vehicles.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        if not request.data["image"] and instance.image:
            request.data._mutable = True
            request.data["image"] = instance.image
                
        serializer = self.serializer_class(instance, data=request.data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseUploadAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)
    
    def get(self, request, pk, *arg, **kwarg):
        try:
            upload = CourseDataUpload.objects.get(id = pk)
        except CourseDataUpload.DoesNotExist:
            return Response(data = {"status": "error", "error": "Course doest not exists"}, status = 404)
        if not upload.file:
            file_url = None
        else:
            file_url = f"/media/{upload.file.url}"
        item = {
            "id": upload.id,
            "user": {
                "id": upload.idUser.id if upload.idUser else None,
                "username": upload.idUser.username if upload.idUser else None,
                "email": upload.idUser.email if upload.idUser else None,
                "profile": upload.idUser.profile if upload.idUser else None,
            },
            "course": {
                "event_date": upload.idCourse.eventDate if upload.idCourse else None,
                "program": upload.idCourse.idProgram.name if upload.idCourse else None,
                "venue": upload.idCourse.idVenue.name if upload.idCourse else None
            },
            "timestamp": upload.timestamp.strftime('%d, %b %Y, %H:%M:%S'),
            "comment": upload.comment,
            "file": file_url,
        }
        return Response(data = {"status": "success", "items": item}, status = 200)    

    def delete(self, request, pk, *arg, **kwargs):
        try:
            instance = CourseDataUpload.objects.get(id = pk)
        except CourseDataUpload.DoesNotExist as e:
            logger.error(str(e))
            return Response(data = {"status": "error", "error": "Course doest not exists"}, status = 404)
        
        if request.user != instance.idUser:
            if not request.user.is_superadmin_profile:
                return Response(data = {"status": "error", "error": f"You don't have permission to delete this record" }, status = 400)
            
        with transaction.atomic():
            try:
                if instance.idCourse:
                    DataFinalExerciseComputed.objects.filter(
                        idParticipation__idCourse = instance.idCourse).delete()
                    DataFinalExercise.objects.filter(
                        idParticipation__idCourse = instance.idCourse).delete()
                    DataExercises.objects.filter(idParticipation__idCourse = instance.idCourse).delete()
                    ExercisesSelected.objects.filter(idCourse = instance.idCourse).delete()
                    Comments.objects.filter(idParticipation__idCourse = instance.idCourse).delete()
                    Participations.objects.filter(idCourse = instance.idCourse).delete()
                    instance.delete()
                    Courses.objects.get(id = instance.idCourse.id).delete()
                else:
                    instance.delete()
            except Exception as e:
                logger.error(str(e))
                return Response(data = {"status": "error", "error": f"Error while deleting course. {str(e)}" }, status = 400)
        return Response(data = {"status": "success"}, status = 200)    
    

class CourseUploadListAPIView(APIView):
    permission_classes = (AdminOnlyPermission,)

    def get(self, request, *arg, **kwarg):
        # deleting dump courses uploaded by user 
        CourseDataUpload.objects.filter(idCourse = None, idUser = request.user).delete()
        uploads = CourseDataUpload.objects.all().select_related("idCourse", "idUser").values_list(
            "id", "idUser__username", "idUser__email", "idUser__profile",
            "idCourse__id", "idCourse__eventDate", "idCourse__idProgram__name", 
            "idCourse__idVenue__name", "idCourse__idVenue__idCountry__name",
            "timestamp", "comment", "file", "exception"
        ).order_by("-id")
        
        items = []
        for upload in uploads:
            if not upload[11]:
                file_url = None
            else:
                file_url = f"/media/{upload[11]}"
            items.append({
                "id": upload[0],
                "user": {
                    "username": upload[1],
                    "email": upload[2],
                    "profile": upload[3],
                },
                "course": {
                    "id": upload[4],
                    "url": reverse("core:admin:admin_course_upload_view", kwargs={"course_id": upload[4]}) if upload[4] else None,
                    "event_date": upload[5],
                    "program": upload[6],
                    "venue": upload[7],
                    "country": upload[8]
                },
                "timestamp": upload[9].strftime('%d, %b %Y, %H:%M:%S'),
                "comment": upload[10],
                "file": file_url,
                "instance_url": reverse("core:api:admin_api:course_upload", kwargs={"pk":upload[0]}),
                "exception": upload[12] if upload[12] else "",
            })
        return Response(data = {"status": "success", "items": items}, status = 200)    

    def instance_populate(self, instance_id, instance_comment, course_params):
        instance = CourseDataUpload.objects.get(id = instance_id)

        def populate_course():
            with transaction.atomic():
                course_instance = instance.populate_course_db(
                    instance.get_extract_dir(), course_params)
                instance.idCourse = course_instance
                instance.comment = instance_comment
                instance.save()  
        try:
            populate_course()
        except AssertionError as e:
            err = ast.literal_eval(str(e))
            _err = f"Got error with message `{err['message']}` while doing `{err['method']}`."
            _err += f"Potential error in row: ' {err['row']}" if err["row"] != -1 else ""
            print(_err)
            raise _err from e
        except Exception as e:
            print(traceback.format_exc())
            instance.delete()
            raise e
    
    @celery_app.task(bind = True, serializer = "json")
    def populate_student_report(self, instance_id, pdf_report_path, *ar, **kw):
        instance = CourseDataUpload.objects.get(id = instance_id)
        try:
            # upload_instance = CourseDataUploader(instance.get_extract_dir())
            logger.info("Populating student's report")
            # student_report_pdf_path = upload_instance.populate_course_students_report()
            # populate to s3
            instance.upload_student_reports(pdf_report_path)
            instance.delete_zip_extraction_dir(instance.get_extract_dir())
        except Exception as e:
            print(e)
            instance.exception = str(e)
            instance.save()
            
    def instance_save(self, request, course_params, language):
        zipfile = request.FILES["file"]
        if not zipfile:
            return Response(data = {"status": "error", "error": "Provide zipfile"}, status = 400)        
        try:
            instance = CourseDataUpload(idUser = request.user, file = zipfile)
            instance.save()
        except Exception as e:
            return Response(
                data = {
                    "status": "error", 
                    "error": f"Error while saving course upload detail. {str(e)}"
                }, status = 500
            )
        try:
            items = self.get_dataframe_glimpse(
                extract_path = instance.get_extract_dir(),
                course_params = course_params,
                language = language
            )
            return Response(
                data = {
                    "status": "success", 
                    "items": items,
                    "instance": {
                        "id": instance.id, 
                        "url": reverse("core:api:admin_api:course_upload", kwargs={"pk":instance.id})
                    }
                }, 
                status = 200
            )
        except AssertionError as e:
            err = ast.literal_eval(str(e))
            _err = f"Got error with message `{err.get('message', '')}` while doing `{err.get('method', '')}`."
            _err += f"Potential error in row: ' {err.get('row', '')}" if err.get('row', 0) != -1 else ""
            logger.error(_err)
            return Response(data = {"status": "error", "error": _err}, status = 400)
        except Exception as e:
            logger.error(str(e))
            instance.delete()
            return Response(
                data = {
                    "status": "error", 
                    "error": f"Error in processing the data, {str(e)}"
                }, 
                status = 500
            )
            
    def get_dataframe_glimpse(self, extract_path, course_params, language):
        report_dir = str(shortuuid.uuid())
        try:
            upload_instance = CourseDataUploader(extract_path, course_params)
            df_json = upload_instance.get_data_upload_glimpse()
            students_df, gloabl_vars = upload_instance.populate_course_students_report(report_dir)
            for d in df_json:
                d.update({"report_url": "/media/reports/" + report_dir + "/" + f"[{language}]" + d["studentId"] + ".pdf"})
            items = {
                "overall_df": json.dumps(df_json),
                "students_df": students_df,
                "gloabl_vars": gloabl_vars,
                "report_dir": "reports/" + report_dir
            }
            return json.dumps(items, default=str)
        except AssertionError as e:
            print(e)
            try:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT, report_dir))
            except OSError as e_:
                pass
            raise e
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            print(sys.exc_info()[2])
            try:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT, report_dir))
            except OSError as e_:
                pass
            raise Exception(f"Getting error while proccessing data. {str(e)}") from e
    
    def post(self, request, *arg, **kwargs):
        data = request.data
        post = data.get("post", None)
        language = request.session.get("language")
        if not language:
            language = "en"
        language = language.lower() 
        
        if not post or post not in ["0", "1"]:
            return Response(
                data = {"status": "error", "error": "Provide post flag as 0 or 1"}, 
                status = 400
            )
        try:
            course_params = {
                "program": data["program"],
                "client": data["company"],
                "location": data["venue"],
                "date": data["course_date"],
                "is_open": False
            }
        except KeyError as e:
            return Response(
                data = {"status": "error", "error": "Program, Venue, Country, course date is required"}, 
                status = 400
            )
        try:           
            course_params["program"] = Programs.objects.get(id=course_params["program"]).name
            course_params["client"] = Companies.objects.get(id=course_params["client"]).name
            course_params["location"] = Venues.objects.get(id=course_params["location"]).name
            if course_params["client"] == "Open Enrollment":
                course_params["is_open"] = True
        except Exception as e:
            return Response(
                data = {"status": "error", "error": "Program, Venue, Country, not found"}, 
                status = 400
            )
        if post == "1":
            try:
                instance_id = data.get("instance_id", None)
                pdf_report_path = data.get("reports_base_dir", None)
                report_path = os.path.join(settings.MEDIA_ROOT, pdf_report_path)
                instance_comment = data.get("comment", "")
                try:
                    instance = CourseDataUpload.objects.get(id = instance_id)
                except CourseDataUpload.DoesNotExist:
                    return Response(
                        data = {"status": "error", "error": "Instance not saved, or does not exists."}, 
                        status = 400
                    )
                try:
                    # db populate
                    self.instance_populate(
                        instance_id, instance_comment, course_params)
                    # self.populate_student_report(instance_id)
                except Exception as e:
                    return Response(
                        data = {"status": "error", "error": str(e)}, 
                        status = 400
                    )
                # student reports populate
                self.populate_student_report.delay(instance_id, report_path)
                
                return Response(
                    data = {
                        "status": "success", 
                        "instance": {
                            "id": instance.id, 
                            "url": reverse("core:api:admin_api:course_upload", kwargs={"pk":instance.id})
                        }
                    }, 
                    status = 200
                )
                
            except Exception as e:
                return Response(
                    data = {"status": "error", "error": str(e)}, 
                    status = 500
                )
        elif post == "0":
            try:
                return self.instance_save(request, course_params, language)
            except Exception as e:
                return Response(
                    data = {"status": "error", "error": str(e)}, 
                    status = 500
                )
                
        return Response(
            data = {"status": "error", "error": "Invalid body"}, 
            status = 500
        )
    
    