# Generated by Django 4.0.1 on 2022-06-21 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_room_idn'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='idn',
        ),
    ]
