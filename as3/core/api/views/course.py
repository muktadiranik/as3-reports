from rest_framework.response import Response
from as3.core.models import *
from as3.core.api.views.mixins import BaseApiViewMixin

class CommentsListApiView(BaseApiViewMixin):
    def get(self, request, company_id = None, course_id = None, *arg, **kw):
        company_instance = None
        if company_id:
            company_id = self.is_valid_user(request, company_id, None)
            try:
                company_instance = Companies.objects.get(id = company_id)
            except Companies.DoesNotExist:
                return Response(data = {"error": str("Company does not exists")}, status = 404)
    
        try:
            course_instance = Courses.objects.get(id = course_id)
        except Courses.DoesNotExist:
            return Response(data = {"error": str("Course does not exists")}, status = 404)
        
        if company_instance:
            comments = Comments.objects.select_related(
                "idParticipation", "idParticipation__idStudent").filter(
                idParticipation__idCourse = course_instance,
                idParticipation__idCompany = company_instance,
            )
        else:
            comments = Comments.objects.select_related(
                "idParticipation", "idParticipation__idStudent").filter(
                idParticipation__idCourse = course_instance)
        
        items = []
        for comment in comments:
            items.append({
                "id": comment.id,
                "comment": comment.comment,
                "timestampt": comment.timestamp,
                "participant": comment.idParticipation.idStudent.fullName(),
            })
        
        return Response(data = {"items": items}, status = 200)
    
