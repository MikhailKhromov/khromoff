# Generated by Django 3.0.5 on 2020-04-09 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('urlshortner', '0008_visit_shorturl'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visit',
            name='address',
        ),
    ]