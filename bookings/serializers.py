from .models import Booking
from rest_framework.serializers import ModelSerializer, DateField, ValidationError
from django.utils import timezone

class PublicBookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = ("id", "check_in", "check_out", "experience_time", "guests")

class CreateRoomBookingSerializer(ModelSerializer):

    check_in = DateField()
    check_out = DateField()

    class Meta:
        model = Booking
        fields = ("check_in", "check_out", "guests")

    def validate_check_in(self, value):
        now = timezone.now().date()
        if value < now:
            raise ValidationError("Can't book in the past")
        return value
    
    def validate_check_out(self, value):
        now = timezone.now().date()
        if value < now:
            raise ValidationError("Can't book in the past")
        return value

    def validate(self, data):
        if data["check_out"] <= data["check_in"]:
            raise ValidationError("Check in should be smaller than check out")
        
        if Booking.objects.filter(check_in__lt=data["check_out"], check_out__gt=data["check_in"], room__id=self.context["room_id"]).exists():
            raise ValidationError("The booking already exists")
        return data