from django.db import models
from common.models import CommonModel

# Create your models here.

class Booking(CommonModel):
    
    class BookingKindChoices(models.TextChoices):
        ROOM = ("room", "Room")
        EXPERIENCE = ("experience", "Experiecne")
    
    kind = models.CharField(max_length=15, choices=BookingKindChoices)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey("rooms.Room", on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    experience = models.ForeignKey("experiences.Experience", on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    experience_time = models.DateTimeField(null=True, blank=True)
    guests = models.PositiveIntegerField(default=1)

    def __str__(self) -> str:
        return f"{self.kind} / {self.user}"
