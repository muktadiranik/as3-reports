from datetime import datetime

from as3.core.api.permissions import CompanyOrAdminOnlyPermission
from as3.core.models import *
from django.db import connection
from rest_framework.views import APIView


class BaseApiViewMixin(APIView):
    permission_classes = (CompanyOrAdminOnlyPermission,)
    
    @staticmethod
    def is_valid_user(request, company_id, course_id):
        if request.user.is_superadmin_or_admin: # admin
            # special case when for course upload dashboard from admin dashboard
            if not company_id and course_id:
                return None 
            if company_id and not Companies.objects.filter(id = company_id).exists():
                raise PermissionError("Company doesn't exists")
            else:
                return company_id
        
        if request.user.is_company_profile: #company profile
            # if company_id:
            #     raise PermissionError("Not viewable by company profile")
            if not CompanyUsers.objects.filter(idUser = request.user).exists():
                raise Exception("Company doesn't exists")
            return CompanyUsers.objects.get(idUser = request.user).idCompany.id
        raise PermissionError("No company found")
    
    @staticmethod
    def get_extra_req_params(request):
        groups = request.query_params.get('groups', None)
        teams = request.query_params.get('teams', None)
        locations = request.query_params.get('locations', None)
        programs = request.query_params.get('programs', None)
        event_date_start = request.query_params.get('start_date', None)
        event_date_end = request.query_params.get('end_date', None)
        options = {
            "groups": groups,
            "teams": teams,
            "locations": locations,
            "programs": programs,
            "programs": programs,
            "event_date_start_obj": None,
            "event_date_end_obj": None,
            "event_date_start": event_date_start,
            "event_date_end": event_date_end
        }  
        if event_date_end and event_date_start:
            event_date_start = datetime.utcfromtimestamp(int(event_date_start))
            event_date_end = datetime.utcfromtimestamp(int(event_date_end))
            options["event_date_start_obj"] = event_date_start.strftime('%Y-%m-%d %H:%M:%S')
            options["event_date_end_obj"] = event_date_end.strftime('%Y-%m-%d %H:%M:%S')
        return options
    
    @staticmethod
    def execute_raw_query(query, row_tansform):
        cursor = connection.cursor()
        cursor.execute(query.strip(" \n\t"))
        items = []
        for row in cursor:
            if row_tansform:
                items.append(row_tansform(row))
            else:
                items.append(row)
        return items