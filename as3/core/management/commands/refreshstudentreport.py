from django.core.management.base import BaseCommand, CommandError
from as3.core.db_utils.db_populate import CourseDataUploader
from as3.core.models import CourseDataUpload, extract_course_zip
import shortuuid
from django.conf import settings
import os
from multiprocessing import Pool

class Command(BaseCommand):
    help = 'Refresh the students report on S3'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
    
    @staticmethod
    def _process_course_upload(course_upload):
        if not course_upload.idCourse:
           return
        print("Started to upload student report for course: ", course_upload.idCourse.id)
        try:
            report_dir = str(shortuuid.uuid())
            report_path = os.path.join(settings.MEDIA_ROOT, f"reports/{report_dir}")
        
            extract_course_zip(course_upload.file.path)
            zippath = course_upload.get_extract_dir()
            
            upload_instance = CourseDataUploader(zippath, None)
            upload_instance.populate_course_students_report(report_dir)
            course_upload.upload_student_reports(report_path)
            
            course_upload.delete_zip_extraction_dir(zippath)
            print("Course: ", course_upload.idCourse.id, " is completed!")
        except Exception as e:
            print("-"*10)
            print("Course with id: ", course_upload.idCourse.id, " results in error, exception:")
            print(e)
            print("-"*10)
            
    def handle(self, *args, **options):
        course_uploads = CourseDataUpload.objects.all().order_by("-id")
        with Pool() as pool:
            pool.map(self._process_course_upload, course_uploads)
        # for upload in course_uploads:
        #     self._process_course_upload(upload)
