from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Amenity, Room
from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer
from reviews.serializers import ReviewSerializer

class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = ("name", "description")

class RoomListSerializer(ModelSerializer):
    rating = SerializerMethodField()
    is_owner = SerializerMethodField()

    class Meta:
        model = Room
        fields = ("name", "city", "country", "price", "rating", "is_owner")

    def get_rating(self, room):
        return room.rating()

    def get_is_owner(self, room):
        request = self.context["request"]
        return request.user == room.owner

class RoomDetailSerializer(ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    rating = SerializerMethodField()
    reviews_count = SerializerMethodField()
    is_owner = SerializerMethodField()

    

    class Meta:
        model = Room
        fields = "__all__"

    def get_rating(self, room):
        return room.rating()
    
    def get_reviews_count(self, room):
        return room.reviews_count()
    
    def get_is_owner(self, room):
        request = self.context["request"]
        return request.user == room.owner