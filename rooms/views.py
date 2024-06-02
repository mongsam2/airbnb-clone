from django.shortcuts import render
from django.db import transaction

# models
from .models import Amenity, Room
from categories.models import Category

# serializers
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer
from reviews.serializers import ReviewSerializer
from medias.serializers import PhotoSerializer

# rest framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.permissions import IsAuthenticatedOrReadOnly

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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_rooms = Room.objects.all()
        serializer = RoomListSerializer(all_rooms, many=True, context={"request":request})
        return Response(serializer.data)

    def post(self, request):
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
        

class RoomDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(id=pk)
        except Room.DoesNotExist:
            raise NotFound("The Room Does Not Exist")


    def get(self, request, pk):
        room = self.get_object(pk)
        serializer = RoomDetailSerializer(room, context={"request":request})
        return Response(serializer.data)

    def put(self, request, pk):
        # user auth
        room = self.get_object(pk)
        
        if room.owner != request.user:
            raise PermissionDenied("Not Allowed User")
        
        # room auth
        serializer = RoomDetailSerializer(room, data=request.data, partial=True)
        if serializer.is_valid():
            room = serializer.save()
            # Put category 
            category_id = request.data.get("category")
            if category_id: # update category
                try:
                    category = Category.objects.get(id=category_id)
                    if category.kind == Category.CategoryKindChoices.EXPERIENCES:
                        raise ParseError("The Category kind should be 'rooms'")
                except Category.DoesNotExist:
                    raise ParseError("Category not found")
                room.category = category
            # Put amenities  amenity에 대한 정보가 없으면, 기존 amenities 유지
            amenities_id = request.data.get("amenities")
            if amenities_id: # update amenities
                try:
                    with transaction.atomic():
                        room.amenities.clear()
                        for id in amenities_id:
                            amenity = Amenity.objects.get(id=id)
                            room.amenities.add(amenity)
                except Exception:
                    raise ParseError("Invalid Amenities")
                
            return Response(RoomDetailSerializer(room).data)
        else:
            return Response(serializer.errors)

    def delete(self, request, pk):
        room = self.get_object(pk)
        
        if room.owner != request.user:
            raise PermissionDenied("Not Allowded User")
        room.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    
class RoomReviews(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            room = Room.objects.get(id=pk)
        except Room.DoesNotExist:
            raise NotFound
        return room

    def get(self, request, pk):
        try:
            page = request.query_params.get("page", "1")
            page = int(page)
        except ValueError:
            page = 1
        page_size = 3
        room = self.get_object(pk)
        serializer = ReviewSerializer(room.reviews.all()[(page-1)*page_size:page*page_size], many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        room = self.get_object(pk)
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(room=room, user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
    
class RoomAmenities(APIView):
    def get_object(self, pk):
        try:
            return Room.objects.get(id=pk)
        except Room.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        room = self.get_object(pk)
        page = request.query_params.get("page", "1")
        try:
            page = int(page)
        except ValueError:
            page = 1
        page_size = 5
        serializer = AmenitySerializer(room.amenities.all()[(page-1)*page_size:page*page_size], many=True)
        return Response(serializer.data)
    
class RoomPhotos(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Room.objects.get(id=pk)
        except Room.DoesNotExist:
            raise NotFound("Room Not Found")
    
    def post(self, request, pk):
        room = self.get_object(pk)
        if request.user != room.owner:
            raise PermissionDenied
        
        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(room=room)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)