# Generated manually for populating slugs

from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    """Populate slug field for existing EntradaDeBlog entries"""
    EntradaDeBlog = apps.get_model('travel_api', 'EntradaDeBlog')
    
    for entrada in EntradaDeBlog.objects.all():
        if not entrada.slug and entrada.titulo:
            # Generate slug from title
            base_slug = slugify(entrada.titulo)
            slug = base_slug
            counter = 1
            
            # Ensure unique slug
            while EntradaDeBlog.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            entrada.slug = slug
            entrada.save()


def reverse_populate_slugs(apps, schema_editor):
    """Reverse migration - clear all slugs"""
    EntradaDeBlog = apps.get_model('travel_api', 'EntradaDeBlog')
    EntradaDeBlog.objects.update(slug=None)


class Migration(migrations.Migration):

    dependencies = [
        ('travel_api', '0013_add_slug_field'),
    ]

    operations = [
        migrations.RunPython(populate_slugs, reverse_populate_slugs),
    ] 