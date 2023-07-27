import os

import boto3
from botocore.client import ClientError, Config


class S3Broker:
    SIGNED_URL_TIMEOUT = 3600
    def __init__(self, key, secret, bucket:str):
        self.bucket = bucket
        self.s3 = self.__get_session(key, secret)
        
    def __get_session(self, key, secret):
        try:
            s3 = boto3.resource(
                's3',
                aws_access_key_id=key,
                aws_secret_access_key=secret,
                region_name="eu-central-1",
                config=Config(signature_version='s3v4')
            )
        except Exception as e:
            print(f"Error in creating boto3 session: {str(e)}")
            raise e

        try:
            s3.meta.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            print("Bucket does not exists. Creating one")

        return s3

    def upload_file(self, f_path, cid, sid):
        try:
            self.s3.meta.client.upload_file(
                Filename=f_path, 
                Bucket=self.bucket, 
                Key=f"course-{cid}/student-{sid}"
            )
        except Exception as e:
            print(f"Error in uploading file {f_path}, {sid}: {str(e)}")
            raise e
        
    def download_file_url(self, course_id, student_code, language = "en"):
        key = f"course-{course_id}/student-[{language}]{student_code}.pdf"
        try:
            res = self.s3.meta.client.generate_presigned_url(
                'get_object',
                Params = {'Bucket': self.bucket, 'Key': key},
                ExpiresIn = self.SIGNED_URL_TIMEOUT,
                HttpMethod="GET"
            )
        except ClientError:
            return None
        return res
    
    def download_file(self, course_id, student_code, file_path, language = "en"):
        key = f"course-{course_id}/student-[{language}]{student_code}.pdf"
        try:
            res = self.s3.meta.client.download_file(
              Bucket=self.bucket,
              Key=key, 
              Filename=file_path
            )
        except ClientError as e:
            print(e, "error")
            return None
        return res

    def delete_course(self, course_id):
        key = f"course-{course_id}/"
        try:
            bucket = self.s3.Bucket(self.bucket)
            res = bucket.objects.filter(Prefix=key).delete()
            # res = self.s3.delete_object(self.bucket, key)
            print("course key Deleted successfully")
            return True
        except ClientError as e:
            print(f"Deletetion failed with {str(e)}")
            return False
