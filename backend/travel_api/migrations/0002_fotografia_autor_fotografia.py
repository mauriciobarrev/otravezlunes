# Generated by Django 5.2.1 on 2025-05-20 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel_api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fotografia',
            name='autor_fotografia',
            field=models.CharField(blank=True, help_text='Nombre de la persona que tomó la fotografía', max_length=150, null=True),
        ),
    ]
