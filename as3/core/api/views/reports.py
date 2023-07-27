from datetime import datetime
import os
import time

from as3.core.models.base import Companies, Courses, Participations, Students
from as3.core.utils.reports.global_report import GlobalCompanyReport
from as3.core.utils.s3_broker import S3Broker
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from django.utils.text import slugify
import shortuuid
from .company import (PerformanceViewAPI, StudentPerformancesViewAPI,
                   StudentsAverageViewAPI, VehicleListView)
from .mixins import BaseApiViewMixin

import shutil

class GlobalReportAPIViewExport(
    StudentPerformancesViewAPI, 
    StudentsAverageViewAPI, 
    PerformanceViewAPI, 
    VehicleListView, 
    BaseApiViewMixin
):
    all_images = []
    
    def get_toc_story(self, request, company_id, course_id, report, story):
        story[0], img_paths = report.toc()
        self.all_images.extend(img_paths)
    
    def get_introduction_story(self, request, company_id, course_id, report, story):
        averages_json = self.get_student_averages(request, company_id, course_id)
        story[1], img_paths = report.introduction_section(averages_json)
        self.all_images.extend(img_paths)
        
    def get_vehicles_story(self, request, company_id, course_id, report, story):
        vehicles_json = self.get_vehicles(request, company_id, course_id)
        story[2], img_paths = report.vehicles_section(vehicles_json)
        self.all_images.extend(img_paths)
    #here
    def get_performers_story(self, request, company_id, course_id, report, story):
        performers = self.get_student_performers(request, company_id, course_id)
        story[3], img_paths = report.performers_section(performers)
        self.all_images.extend(img_paths)
    
    def get_excercise_story(self, request, company_id, course_id, report, story):
        performances = self.get_performaces(request, company_id, course_id)
        story[4], img_paths = report.excercise_section(performances)
        self.all_images.extend(img_paths)
    #here
    def get_performance_control_story(self, request, company_id, course_id, report, story):
        performace_control_json = self.get_student_performers(request, company_id, course_id)
        story[5], img_paths = report.final_excercise_section(performace_control_json)
        self.all_images.extend(img_paths)
        
    def get_conclusion_story(self, request, company_id, course_id, report, story):
        story[6], img_paths = report.conclusion_section()
        self.all_images.extend(img_paths)
    
    def build_story(self, request, company_id, course_id, report):
        story = {}
        self.get_toc_story(request, company_id, course_id, report,story)
        self.get_introduction_story(request, company_id, course_id, report,story)
        self.get_vehicles_story(request, company_id, course_id, report,story)
        self.get_performers_story(request, company_id, course_id, report,story)
        self.get_excercise_story(request, company_id, course_id, report,story)
        self.get_performance_control_story(request, company_id, course_id, report,story)
        self.get_conclusion_story(request, company_id, course_id, report,story)

        # manager = multiprocessing.Manager()
        # story = manager.dict()
        # process = [
        #     multiprocessing.Process(target=self.get_toc_story, args=(request, company_id, course_id, report,story)),
        #     multiprocessing.Process(target=self.get_introduction_story, args=(request, company_id, course_id, report,story)),
        #     multiprocessing.Process(target=self.get_vehicles_story, args=(request, company_id, course_id,report,story)),
        #     multiprocessing.Process(target=self.get_performers_story, args=(request, company_id, course_id,report,story)),
        #     multiprocessing.Process(target=self.get_excercise_story, args=(request, company_id, course_id,report,story)),
        #     multiprocessing.Process(target=self.get_performance_control_story, args=(request, company_id, course_id,report,story)),
        #     multiprocessing.Process(target=self.get_conclusion_story, args=(request, company_id, course_id,report,story)),
        # ]
        # for p in process:   p.start()
        # for p in process:   p.join()    
        
        return story
    
    def get(self, request, company_id = None, course_id = None, *a, **k):
        # try:
        extra_params = self.get_extra_req_params(request)
        t = time.time()
        company_id = self.is_valid_user(
            request, 
            company_id = company_id, 
            course_id = course_id
        )
        try:
            company_instance = Companies.objects.get(id = company_id)
        except Companies.DoesNotExist:
            return Response(data = {"status": "error", "error": "Company does not exists"}, status = 400)
        
        language = request.query_params.get('language', "EN")
        
        event_date_start = extra_params.get("event_date_start", None)
        event_date_end = extra_params.get("event_date_end", None)
        
        if event_date_start and event_date_end:
            event_date_start = datetime.utcfromtimestamp(int(event_date_start))
            event_date_end = datetime.utcfromtimestamp(int(event_date_end))
            reportDateRange = f"{event_date_start.strftime('%d %b, %Y')} to {event_date_end.strftime('%d %b, %Y')}"
        else:
            reportDateRange = "Custom"
            
        report = GlobalCompanyReport(
            language = language, company = company_instance.name, reportDateRange = reportDateRange)
        
        story_dict = self.build_story(request, company_id, course_id, report)
        story = []
        for i in range(7):  story.extend(story_dict[i])

        fname = report.generate_pdf(story)
        tt = time.time()   
        print(tt- t)
        
        pdf_file = open(fname, 'rb')
        response = HttpResponse(pdf_file, content_type='application/pdf')
        pdf_file_name = slugify(f"AS3_Report_{company_instance.name}_{language}")
        response['Content-Disposition'] = f"attachment; filename={pdf_file_name}"
        response["filename"] = pdf_file_name
        try:
            os.remove(fname)
        except FileNotFoundError:
            pass
        for img in self.all_images:
            try:    os.remove(img)
            except FileNotFoundError:   pass
        return response
        # except Exception as e:
        #     print(e)
        #     return Response(data = {"status": "error", "error": f"Something went wrong. {str(e)}"}, status = 500)
            
class StudentReportDownload(BaseApiViewMixin):
    def get(self, request, course_id, student_code, *ar, **kw):
        language = request.GET.get("language")
        if not language:
            language = "en"
        language = language.lower()
        if language not in ["en", "es"]:
            return Response(
                data = {"status": "error", "error": "Language does not supported. Only en, es supported"}, 
                status = 400)
        broker = S3Broker(
            settings.S3_ACCESS_KEY, 
            settings.S3_SECRET_KEY,
            settings.S3_BUCKET
        )
        
        url = broker.download_file_url(course_id, student_code, language)
        if url is None:
            return Response(
                data = {"status": "error", "error": "Client error in fetching the pdf"}, status = 400)
        course = Courses.objects.get(id = course_id)
        student = Students.objects.get(studentId = student_code)
        first_name = student.firstName.replace(' ', '')
        last_name = student.lastName.replace(' ', '')
        
        fname = f"AS3_Driver_Report_{first_name}_{last_name}_{course.eventDate}_[{language}].pdf"
        return Response(data = {"status": "success", "url": url, "fname": fname}, status = 200)


class StudentMultipleReportDownload(BaseApiViewMixin):
    @staticmethod
    def download_reports(student_ids, language):
        broker = S3Broker(
            settings.S3_ACCESS_KEY, 
            settings.S3_SECRET_KEY,
            settings.S3_BUCKET
        )
        report_dir = os.path.join(settings.MEDIA_ROOT, "reports/")
        fpath = os.path.join(
            report_dir, f"report-{shortuuid.uuid()}"
        )
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        course_id = ""
        for student_id, course_id in student_ids:
            try:
                student = Participations.objects.get(
                    idStudent__id = student_id, idCourse__id = course_id)
            except Participations.DoesNotExist as e:
                print("Particpant not found")
                raise e
            fname = f"[{language}]AS3_Driver_Report_{student.idStudent.firstName}_{student.idStudent.lastName}.pdf"
            file_path = os.path.join(fpath, fname)
            broker.download_file(course_id, student.idStudent.studentId, file_path, language)

        return report_dir, fpath
    
    @staticmethod
    def make_zip(report_dir, fpath, language):
        filename = f"AS3_Driver_Report_multiple_[{language}]-{shortuuid.uuid()}"
        zip_path = os.path.join(report_dir, filename)
        shutil.make_archive(zip_path, 'zip', fpath)
        shutil.rmtree(fpath)
        zip_path = zip_path + ".zip"
        return filename, zip_path
    
    def get(self, request, *ar, **kw):
        language = request.GET.get("language")
        if not language:
            language = "en"
        language = language.lower()
        if language not in ["en", "es"]:
            return Response(
                data = {"status": "error", "error": "Language does not supported. Only en, es supported"}, 
                status = 400)
        
        student_ids = dict(request.GET).get("student_ids", [])
        if not student_ids:
            return Response(data = {"status": "error", "error": "Student id not found"}, status = 400)
        
        student_ids = [tuple(_id.split("-")) for _id in student_ids[0].split(",")]
        try:
            report_dir, fpath = self.download_reports(student_ids, language)
        except Exception as e:
            return Response(data = {"status": "error", "error": str(e)}, status = 400)
        try:
            filename, zip_path = self.make_zip(report_dir, fpath, language)
        except Exception as e:
            return Response(data = {"status": "error", "error": str(e)}, status = 400)
        
        pdf_file = open(zip_path, 'rb')
        response = HttpResponse(pdf_file, content_type='application/x-zip-compressed')
        zip_file_name = f"{filename}.zip"
        response['Content-Disposition'] = f"attachment; filename={zip_file_name}"
        response["filename"] = zip_file_name
        
        try:
            os.remove(zip_path)
        except OSError:
            pass
        
        return response