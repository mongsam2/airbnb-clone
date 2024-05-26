from django.shortcuts import render
from django.db import transaction

# models
from .models import Amenity, Room
from categories.models import Category

# serializers
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer

# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT

# Create your views here.
class Amenities(APIView):

    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            new_amenity = serializer.save()
            return Response(AmenitySerializer(new_amenity).data)
        else:
            return Response(serializer.errors)


class AmenityDetail(APIView):
    def get_object(self, pk):
        try:
            amenity = Amenity.objects.get(pk=pk)
        except Amenity.DoesNotExist:
            raise NotFound
        return amenity
    
    def get(self, request, pk):
        serializer = AmenitySerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        serializer = AmenitySerializer(self.get_object(pk), data=request.data, partial=True)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        amenity = self.get_object(pk)
        amenity.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    

class Rooms(APIView):
    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(all_rooms, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.is_authenticated:
            serializer = RoomDetailSerializer(data=request.data)
            
            if serializer.is_valid():
                # category auth
                category_id = request.data.get("category")
                
                if not category_id:
                    raise ParseError("Category is required") # 유저가 잘못된 데이터를 전송했을 때
                
                try:
                    category = Category.objects.get(id=category_id)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The Category kind should be 'rooms'")

                except Category.DoesNotExist:
                    raise ParseError("Category not found")
                
                # Amenities transaction
                try:
                    with transaction.atomic():
                        room = serializer.save(owner=request.user, category=category)   

                        # amenities auth
                        amenities = request.data.get("amenities")
                        for amenity_id in amenities:
                            amenity = Amenity.objects.get(id=amenity_id)
                            room.amenities.add(amenity)
                        return Response(serializer.data)
                except Exception:
                    raise ParseError("Invalid Amenities")
            else:
                return Response(serializer.errors)
        else:
            raise NotAuthenticated
        

class RoomDetail(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(id=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data)

    def put(self, request, pk):
        pass    

    def delete(self, request, pk):
        room = self.get_object(pk)
        
        if not request.user.is_authenticated:
            raise NotAuthenticated("User is not Authenticated")
        if room.owner != request.user:
            raise PermissionDenied("Not Allowded User")
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)