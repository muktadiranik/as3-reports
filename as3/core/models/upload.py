import ast
import os
import re
import shutil
import tarfile
import zipfile
from hashlib import sha1

import py7zr
from as3.core.db_utils.db_populate import CourseDataUploader
from as3.core.utils.s3_broker import S3Broker
from config.celery import celery_app
from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .base import *
from .records import *


class CourseDataUpload(models.Model):
    """
    Holds information of the user and admin who uploaded the excel sheet
    """
    idUser = models.ForeignKey(Users, on_delete=models.PROTECT, blank = True, db_column='idUser', db_index = True)
    idCourse = models.ForeignKey(Courses, on_delete=models.PROTECT, blank = True, null = True, db_column='idCourse', db_index = True)
    timestamp = models.DateTimeField(_('timestamp'), auto_now_add=True)
    comment = models.TextField(null = True, blank = True)
    file = models.FileField(upload_to=f"course_zip/%Y-%m")
    exception = models.TextField(null = True, blank = True)
    
    class Meta:
        db_table = 'api_basic_course_data_upload'
        verbose_name = _('CourseDataUpload')
        verbose_name_plural = _('CourseDataUploads')
    
    
    def get_extract_dir(self):
        file_path = self.file.path
        filepath_hash = sha1(file_path.encode()).hexdigest()[0:6]
        extract_path = os.path.join(os.path.dirname(file_path), filepath_hash)
        return extract_path

    def delete_zip_file(self, fpath, *ar, **kw):
        if os.path.isfile(fpath):
            try:
                os.remove(fpath)
            except OSError as e:
                print(f"Not able to delete zip file {str(e)}")

    def delete_zip_extraction_dir(self, extract_path, *ar, **kw):
        if os.path.isdir(extract_path):
            try:
                shutil.rmtree(extract_path)
            except OSError as e:
                print(f"Not able to delete extracted path {str(e)}")

    def populate_course_db(self, course_dir, course_params):
        print("Uploading Courses")
        course_instance = self.post_course(
            course_dir=course_dir, course_params = course_params)
        # self.post_others.delay(course_id=course_instance.id, course_dir=course_dir)
        self._post_others(
            course_id=course_instance.id, course_dir=course_dir, course_params=course_params)
        return course_instance

    def upload_student_reports(self, report_dir):
        broker = S3Broker(
            settings.S3_ACCESS_KEY, 
            settings.S3_SECRET_KEY,
            settings.S3_BUCKET
        )
        
        def upload_all():
            for report_path in os.listdir(report_dir):
                if not re.search("\.pdf$", report_path):
                    continue
                s_code = report_path.split("/")[-1]
                broker.upload_file(
                    os.path.join(report_dir, report_path),
                    self.idCourse.id,
                    s_code,
                )
            
        if not os.path.exists(report_dir):
            raise OSError("No report path exists")
        if not self.idCourse:
            raise Exception("No course id is assoiated with this upload")
        
        upload_all()
        
        try:
            shutil.rmtree(report_dir)
        except OSError as e:
            print(f"Not able to delete students reports path {str(e)}")

    @staticmethod
    def post_course(course_dir, course_params):
        try:
            upload_instance = CourseDataUploader(course_dir, course_params)
            # create country
            # country = upload_instance.get_country()
            # country_instance, _ = Countries.objects.get(
            #     name = country["country"],
            # )
            # create venue
            venue = upload_instance.get_venue()
            try:
                venue_instance = Venues.objects.get(
                    name = venue["name"]
                )
            except Venues.DoesNotExist:
                raise Exception("Venue does not exists.")
            # create program
            program = upload_instance.get_program()
            try:
                program_instance = Programs.objects.get(
                    name = program["name"],
                )
            except Programs.DoesNotExist:
                raise Exception("Programs does not exists.")
            
            # create course
            course = upload_instance.get_course()
            print(course)
            if Courses.objects.filter(idVenue = venue_instance,
                idProgram = program_instance, eventDate = course["eventDate"]).exists():
                raise Exception("Course already exists.")
            
            course_instance, course_created = Courses.objects.get_or_create(
                idVenue = venue_instance,
                idProgram = program_instance,
                eventDate = course["eventDate"],
                idealTime = course["idealTime"],
                conePenalty = course["conePenalty"],
                gatePenalty = course["gatePenalty"],
                isOpenEnrollment = course["is_open"] if course["is_open"] != None else False
            )
        except Exception as e:
            raise Exception(f"Error in saving Course. {str(e)}") from e
        if not course_created:
            raise Exception("Course already exists.")
        
        return course_instance
    
    @staticmethod
    def _post_others(course_id, course_dir, course_params):
        upload_instance = CourseDataUploader(course_dir, course_params)
        course_instance = Courses.objects.get(id = course_id)
        
        ######### Students #######################
        def _post_students():
            participation_instances = {}
            students = upload_instance.get_students()
            try:
                for student in students:
                    company_instance, _  = Companies.objects.get_or_create(
                        name = student["company"])
                    student_instance, _ = Students.objects.get_or_create(
                        studentId = student["studentId"],
                        firstName = student["firstName"],
                        lastName = student["lastName"],
                        birthday = student["birthday"],
                        gender = student["gender"],
                    )
                    participation_instance, _ = Participations.objects.get_or_create(
                        idCourse = course_instance, 
                        idStudent = student_instance,
                        idCompany = company_instance,
                    )
                    participation_instances.update({student["studentId"]: participation_instance})
            except Exception as e:
                raise Exception(f"Error in saving Students. {str(e)}")
            return participation_instances

        participation_instances = _post_students()

        ######### Vehicles #######################
        def _post_vehicles():
            vehicles = upload_instance.get_vehicles()
            vehicle_instances = {}
            try:
                for vehicle in vehicles:
                    instance, _ = Vehicles.objects.get_or_create(
                        name = vehicle["name"],
                        latAcc = vehicle["latacc"],
                    )
                    car_id = int(vehicle['car_id'])
                    vehicle_instances.update({str(car_id): instance})
            except Exception as e:
                raise Exception(f"Error in saving Vehicle. {str(e)}")
            return vehicle_instances

        vehicle_instances = _post_vehicles()

        ######### Excercises #######################
        def _post_excercises():
            excercise_instances = {}
            print("Uploading excercies")
            for excercise in upload_instance.get_exercises():
                instance, _ = Exercises.objects.get_or_create(
                    name = excercise["exercise"],
                )
                excercise_instances.update({excercise["exercise"]: instance})

            print("Uploading excercies selected")
            excercises_selected_instances = {}
            for excercise in upload_instance.get_exercises_selected():
                eid = excercise_instances[excercise["exercise"]]
                instance, _ = ExercisesSelected.objects.get_or_create(
                    chord = excercise["chord"],
                    mo = excercise["mo"],
                    idCourse = course_instance,
                    idExercise = eid
                )
                excercises_selected_instances.update({f'{eid}_{course_instance.id}': instance})

            print("Uploading DataExercises")
            dataexercise_objs = []
            for excercise in upload_instance.get_data_exercises():
                eid = excercise_instances[excercise['exercise']]
                ex_selected = excercises_selected_instances[f"{eid}_{course_instance.id}"]
                car_id = int(excercise['vehicle'])
                obj = DataExercises(
                    idParticipation = participation_instances[excercise["studentId"]],
                    idExerciseSelected = ex_selected,
                    idVehicle = vehicle_instances[str(car_id)],
                    speedReq = excercise["speedReq"],
                    v1 = excercise["v1"],
                    v2 = excercise["v2"],
                    v3 = excercise["v3"],
                    penalties = 0, ## excercise["penalties"], # TODO: Changes, currently 0
                    pExercise = excercise["pExercise"],
                    pVehicle = excercise["pVehicle"]
                )
                dataexercise_objs.append(obj)
            DataExercises.objects.bulk_create(dataexercise_objs)
            
            print("Uploading DataFinalExercise")
            datafinalexercise_objs = []
            for excercise in upload_instance.get_data_final_exercise():
                obj = DataFinalExercise(
                    idParticipation = participation_instances[excercise["studentId"]],
                    idVehicle = vehicle_instances[f"{excercise['vehicle']}"],
                    stressLevel = excercise["stress"],
                    revSlalom = excercise["revSlalom"],
                    slalom = excercise["slalom"],
                    laneChange = excercise["laneChange"],
                    cones = excercise["cones"],
                    gates = excercise["gates"],
                    time = excercise["time"],
                )
                datafinalexercise_objs.append(obj)
            DataFinalExercise.objects.bulk_create(datafinalexercise_objs)
            
            print("Uploading DataFinalExerciseComputed")
            dfecomputed_objs = []
            for excercise in upload_instance.get_data_final_exercise_computed():
                obj = DataFinalExerciseComputed(
                    idParticipation = participation_instances[excercise["studentId"]],
                    stress = excercise["stress"],
                    revSlalom = excercise["revSlalom"],
                    idVehicle = vehicle_instances[f"{excercise['vehicle']}"],
                    slalom = excercise["slalom"],
                    laneChange = excercise["laneChange"],
                    penalty = excercise["penalty"],
                    finalTime = excercise["finalTime"],
                    finalResult = excercise["finalResult"]
                )
                dfecomputed_objs.append(obj)
            DataFinalExerciseComputed.objects.bulk_create(dfecomputed_objs)
        
        _post_excercises()

        ######### Comments #######################
        def _post_comments():
            comments = upload_instance.get_comments()
            comment_objs = []
            try:
                for comment in comments:
                    comment_objs.append(Comments(
                        idParticipation = participation_instances[comment["studentId"]],
                        comment = comment["comment"]
                    ))
                Comments.objects.bulk_create(comment_objs)
            except Exception as e:
                raise Exception(f"Error in saving Comments. {str(e)}")

        _post_comments()
        
        
def extract_course_zip(file_path):
    try:
        filepath_hash = sha1(file_path.encode()).hexdigest()[0:6]
        extract_path = os.path.join(os.path.dirname(file_path), filepath_hash)
        if os.path.isdir(extract_path):
            return
        
        os.mkdir(extract_path)
        
        if file_path.endswith('.zip'):
            opener, mode = zipfile.ZipFile, 'r'
        elif file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            opener, mode = tarfile.open, 'r:gz'
        elif file_path.endswith('.tar.bz2') or file_path.endswith('.tbz'):
            opener, mode = tarfile.open, 'r:bz2'
        elif file_path.endswith('.7z'):
            opener, mode = py7zr.SevenZipFile, "r"
        else:
            raise ValueError(f"Could not extract {file_path} as no appropriate extractor is found")

        cwd = os.getcwd()
        os.chdir(extract_path)
        try:
            file = opener(file_path, mode)
            try: file.extractall()
            finally: file.close()
        finally:
            os.chdir(cwd)
    except OSError as e:
        print(e)
        raise OSError(f"OS Error while reading/extracting zip file.")
    
    except Exception as e:
        print(e)
        raise OSError(f"Error while reading/extracting zip file.")
    
@celery_app.task(serializer = "json")
def delete_assets_before_course_delete(instance_id, course_id):
    instance = CourseDataUpload.objects.get(id = instance_id)
    instance.delete_zip_file(instance.file.path)
    extract_path = instance.get_extract_dir()
    instance.delete_zip_extraction_dir(extract_path)
    broker = S3Broker(
        settings.S3_ACCESS_KEY, 
        settings.S3_SECRET_KEY,
        settings.S3_BUCKET
    )
    broker.delete_course(course_id)

@receiver(models.signals.post_save, sender=CourseDataUpload)
def course_upload_post_save(sender, instance, **kwargs):
    extract_course_zip(instance.file.path)

@receiver(models.signals.pre_delete, sender=CourseDataUpload)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `CourseDataUpload` object is deleted.
    """
    if instance.file and instance.idCourse:
        course_id = instance.idCourse.id
        delete_assets_before_course_delete.delay(instance.id, course_id)
