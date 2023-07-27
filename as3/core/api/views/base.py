from as3.core.api.serializers import (CompaniesSerializer, ProgramsSerializer,
                                      VenuesSerializer)
from as3.core.api.views.mixins import BaseApiViewMixin
from as3.core.models import *
from rest_framework import status
from rest_framework.response import Response


class ProgramsAPIView(BaseApiViewMixin):
    model = Programs
    serializer_class = ProgramsSerializer
    def get(self, request, *ar, **kw):
        qs = self.model.objects.filter(active = True)
        items = self.serializer_class(qs, many=True)
        return Response({"items": items.data}, status = 200)
    
    def post(self, request, *ar, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VenuesAPIView(BaseApiViewMixin):
    model = Venues
    serializer_class = VenuesSerializer
    def get(self, request, *ar, **kw):
        qs = self.model.objects.filter(active = True)
        items = self.serializer_class(qs, many=True)
        return Response({"items": items.data}, status = 200)
    
    def post(self, request, *ar, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class CompanyAPIView(BaseApiViewMixin):
    model = Companies
    serializer_class = CompaniesSerializer
    def get(self, request, *ar, **kw):
        qs = self.model.objects.filter(active = True)
        items = self.serializer_class(qs, many=True)
        return Response({"items": items.data}, status = 200)
    
    def post(self, request, *ar, **kw):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LanguageChangeView(BaseApiViewMixin):
    def post(self, request, *ar, **kw):
        language = request.data.get('language', None)
        if language in ["en", "es"]:
            request.session["language"] = language
            return Response(data = {}, status = 200)
        return Response(data = {"error": "language not supported"}, status = 400)
