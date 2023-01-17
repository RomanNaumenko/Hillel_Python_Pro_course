from django.db import models
from django.utils.translation import gettext_lazy as _
import json
from .views import ValidationError
from datetime import datetime, date

route_type_list = ['Hiking', 'Mountain climbing', 'Skiing', 'Snowboarding', 'Camping', 'Fishing', 'Biking',
                   'Hunting', 'Photography', 'Sightseeing', 'Other']


def validation_stop_point(value):
    try:
        stop_point = json.loads(value)
        for itm in stop_point:
            if 'name' in itm and 'lat' in itm and 'lon' in itm:
                continue
            else:
                raise ValidationError('Invalid stopping point', params={'value': value})

    except:
        raise ValidationError('Not a valid json', params={'value': value})


def validation_route_type(value):
    if value.title() not in route_type_list:
        raise ValidationError('Invalid route type')


def validation_date(value):
    # try:
    #     parsed_date = datetime.datetime.strptime(str(value), "%Y-%m-%d")
    # except:
    #     raise ValidationError('Invalid date format')

    if date.today() > value:
        raise ValidationError('ERROR')


class Places(models.Model):
    name = models.CharField(max_length=50)


class Route(models.Model):
    start_point = models.IntegerField()
    stop_point = models.CharField(max_length=100)
    destination_point = models.IntegerField()
    country = models.CharField(max_length=50)
    loc = models.CharField(max_length=50)  # Локація
    desc = models.TextField()  # Опис походу

    class Types(models.TextChoices):
        HIKING = 'HIKING', _('Hiking')
        MOUNTAIN_CLIMBING = 'MOUNTAIN_CLIMBING', _('Mountain climbing')
        SKIING = 'SKIING', _('Skiing')
        SNOWBOARDING = 'SNOWBOARDING', _('Snowboarding')
        CAMPING = 'CAMPING', _('Camping')
        FISHING = 'FISHING', _('Fishing')
        BIKING = 'BIKING', _('Biking')
        HUNTING = 'HUNTING', _('Hunting')
        PHOTOGRAPHY = 'PHOTOGRAPHY', _('Photography')
        SIGHTSEEING = 'SIGHTSEEING', _('Sightseeing')
        OTHER = 'OTHER', _('Other')

    route_type = models.CharField(max_length=50, choices=Types.choices,
                                  default=Types.HIKING, validators=[validation_route_type])  # Тип походу
    duration = models.IntegerField()  # Тривалість походу


class Event(models.Model):
    id_route = models.IntegerField()
    event_admin = models.IntegerField()
    event_users = models.CharField(max_length=50)
    start_data = models.DateField(validators=[validation_date])
    price = models.IntegerField()


class Review(models.Model):
    id_route = models.IntegerField()
    text = models.TextField(max_length=500)
    rating = models.IntegerField()
