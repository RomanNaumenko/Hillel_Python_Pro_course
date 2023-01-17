# Generated by Django 4.1.2 on 2022-11-10 12:39

import Coffee_night.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Coffee_night', '0003_remove_event_approved_users_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='start_data',
            field=models.DateField(validators=[Coffee_night.models.validation_date]),
        ),
        migrations.AlterField(
            model_name='route',
            name='route_type',
            field=models.CharField(choices=[('HIKING', 'Hiking'), ('MOUNTAIN_CLIMBING', 'Mountain climbing'), ('SKIING', 'Skiing'), ('SNOWBOARDING', 'Snowboarding'), ('CAMPING', 'Camping'), ('FISHING', 'Fishing'), ('BIKING', 'Biking'), ('HUNTING', 'Hunting'), ('PHOTOGRAPHY', 'Photography'), ('SIGHTSEEING', 'Sightseeing'), ('OTHER', 'Other')], default='HIKING', max_length=50, validators=[Coffee_night.models.validation_route_type]),
        ),
    ]
