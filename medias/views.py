from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.exceptions import NotFound, PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.permissions import IsAuthenticated
from .models import Photo

# Create your views here.
class PhotoDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Photo.objects.get(id=pk)
        except Photo.DoesNotExist:
            raise NotFound
        
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        
        photo = self.get_object(pk)
        if photo.room and photo.room.owner != request.user:
            raise PermissionDenied
        
        elif photo.experience and photo.experience.host != request.user:
            raise PermissionDenied
        photo.delete()
        return Response(status=HTTP_200_OK)