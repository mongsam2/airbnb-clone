from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.exceptions import NotFound
from .models import Wishlist
from rooms.models import Room
from .serializers import WishlistSerializer

# Create your views here.
class Wishlists(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        all_wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(all_wishlists, many=True, context={"request":request})
        return Response(serializer.data)

    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
class WishlistDeatil(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, id, user):
        try:
            return Wishlist.objects.get(id=id, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    def get(self, request, id):
        wishlist = self.get_object(id, request.user)
        serializer = WishlistSerializer(wishlist, context={"request":request})
        return Response(serializer.data)
    
    def delete(self, request, id):
        wishlist = self.get_object(id, request.user)
        wishlist.delete()
        return Response(status=HTTP_200_OK)
    
    def put(self, request, id):
        wishlist = self.get_object(id, request.user)
        serializer = WishlistSerializer(wishlist, data=request.data, partial=True, context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
class WishlistRoom(APIView):
    def get_wishlist(self, id, user):
        try:
            return Wishlist.objects.get(id=id, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound
    
    def get_room(self, id):
        try:
            return Room.objects.get(id=id)
        except Room.DoesNotExist:
            return NotFound

    def put(self, request, wishlist_id, room_id):
        wishlist = self.get_wishlist(wishlist_id, request.user)
        room = self.get_room(room_id)
        if wishlist.rooms.filter(id=room_id).exists():
            wishlist.rooms.remove(room)
        else:
            wishlist.rooms.add(room)
        return Response(status=HTTP_200_OK)