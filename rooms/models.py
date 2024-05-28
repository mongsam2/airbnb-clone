from django.db import models
from common.models import CommonModel

# Create your models here.
class Room(CommonModel):

    class RoomKindChoices(models.TextChoices):
        ENTIRE_PLACE = ("entire_place", "Entire Place")
        PRIVATE_ROOM = ('private_room', 'Private Room')
        SHARED_ROOM = ("shared_room", "Shared Room")

    name = models.CharField(max_length=180, default="___")
    country = models.CharField(max_length=50, default="한국")
    city = models.CharField(max_length=80, default="서울")
    price = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    toilets = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(max_length=250)
    pet_friendly = models.BooleanField()
    kind = models.CharField(max_length=20, choices=RoomKindChoices)
    owner = models.ForeignKey("users.User", on_delete=models.CASCADE)
    amenities = models.ManyToManyField("rooms.Amenity")
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def rating(room):
        count = room.reviews.count()
        if count == 0:
            return 0
        else:
            total_rating = 0
            for review in room.reviews.all().values("rating"): # 딕셔너리 형태로 반환
                total_rating += review["rating"]
            return round(total_rating / count, 2)
    
    def reviews_count(self):
        return self.reviews.count()
    

class Amenity(CommonModel):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=150, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name