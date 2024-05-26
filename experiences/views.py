from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import PerkSerializer
from .models import Perk
from rest_framework.response import Response
from .serializers import PerkSerializer
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_204_NO_CONTENT

# Create your views here.
class Perks(APIView):
    
    def get(self, request):
        all_perks = Perk.objects.all()
        return Response(PerkSerializer(all_perks, many=True).data)

    def post(self, request):
        serializer = PerkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PerkDetail(APIView):

    def get_object(self, pk):
        try:
            perk = Perk.objects.get(pk=pk)
        except:
            raise NotFound
        return perk

    def get(self, request, pk):
        serializer = PerkSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        serializer = PerkSerializer(self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


    def delete(self, request, pk):
        perk = self.get_object(pk)
        perk.delete()
        return Response(status=HTTP_204_NO_CONTENT)
