from django.db import models
from django.contrib.gis.db.models import PointField

from libs.choices import Choices
from libs.fields import ChoicesField, MoneyField


class TripRoute(models.Model):
    TYPES = Choices(
        'journey',
        'entertainment',
        'excursion',
    )

    guide_profile = models.ForeignKey('GuideProfile', on_delete=models.CASCADE)

    title = models.CharField(max_length=1024)
    description = models.TextField()

    type = ChoicesField(choices=TYPES, default=TYPES.journey)
    country = models.CharField(max_length=30, default="", blank=True)
    city = models.CharField(max_length=30, default="", blank=True)
    nop = models.PositiveIntegerField("Number of participants")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def trip_route_points(self):
        return self.triproutepoint_set.all()

    def trip_route_pictures(self):
        return self.triproutepicture_set.all()


class TripRoutePoint(models.Model):
    trip_route = models.ForeignKey('TripRoute', on_delete=models.CASCADE)
    cpp = MoneyField()
    location = PointField(null=True, default=None, blank=True)
    title = models.CharField(max_length=1024, default="", blank=True)
    description = models.TextField(default="", blank=True)

    def __str__(self):
        return str(self.id)


class TripRoutePicture(models.Model):
    trip_route = models.ForeignKey('TripRoute', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='trip-route-picture')
    is_poster = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.image.url

    @property
    def image_url(self):
        return self.image.url


class TripRouteComment(models.Model):
    trip_route = models.ForeignKey('TripRoute', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class Trip(models.Model):
    STATUSES = Choices(
        'created',
        'confirmed',
        'rejected',
        'completed',
        'canceled',
    )

    trip_route = models.ForeignKey('TripRoute', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    participants = models.ManyToManyField('Client', blank=True)
    date_from = models.DateField()
    date_to = models.DateField()
    status = ChoicesField(choices=STATUSES, default=STATUSES.created)
    reason = models.TextField(default="", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class TripRequest(models.Model):
    STATUSES = Choices(
        'created',
        'accepted',
        'declined',
        'payed',
        'confirmed',
        'rejected',
        'completed',
        'canceled',
    )

    trip = models.ForeignKey('Trip', on_delete=models.CASCADE)
    client = models.ForeignKey('Client', on_delete=models.CASCADE)

    status = ChoicesField(choices=STATUSES, default=STATUSES.created)
    reason = models.TextField(default="", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class TripDeposit(models.Model):
    trip_request = models.ForeignKey('TripRequest', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = MoneyField()
    is_funded = models.BooleanField(default=False)
    is_hold = models.BooleanField()

    def __str__(self):
        return str(self.id)
