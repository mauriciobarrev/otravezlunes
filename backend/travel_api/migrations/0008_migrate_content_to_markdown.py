# Generated manually for content migration

from django.db import migrations

def migrate_content_to_markdown(apps, schema_editor):
    """
    Migra el contenido existente del campo 'contenido' al nuevo campo 'contenido_markdown'
    """
    EntradaDeBlog = apps.get_model('travel_api', 'EntradaDeBlog')
    
    for entrada in EntradaDeBlog.objects.all():
        if entrada.contenido and not entrada.contenido_markdown:
            # Copiar el contenido existente al campo markdown
            entrada.contenido_markdown = entrada.contenido
            
            # Si tenemos la utilidad disponible, procesar a HTML también
            try:
                from travel_api.utils import markdown_to_html
                entrada.contenido_html = markdown_to_html(entrada.contenido_markdown)
            except ImportError:
                # Si no está disponible la utilidad, el signal se encargará después
                pass
            
            entrada.save()

def reverse_migrate_content(apps, schema_editor):
    """
    Función de reversión para volver el contenido al campo original
    """
    EntradaDeBlog = apps.get_model('travel_api', 'EntradaDeBlog')
    
    for entrada in EntradaDeBlog.objects.all():
        if entrada.contenido_markdown and not entrada.contenido:
            entrada.contenido = entrada.contenido_markdown
            entrada.save()

class Migration(migrations.Migration):

    dependencies = [
        ('travel_api', '0007_add_markdown_support'),
    ]

    operations = [
        migrations.RunPython(
            migrate_content_to_markdown,
            reverse_migrate_content,
            elidable=True,
        ),
    ] 