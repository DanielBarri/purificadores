from django.db import migrations


def corregir_categoria(apps, schema_editor):
    Producto = apps.get_model('pedidos', 'Producto')
    Producto.objects.filter(categoria='FILTOS_REFACCIONES').update(categoria='FILTROS_REFACCIONES')


def revertir_categoria(apps, schema_editor):
    Producto = apps.get_model('pedidos', 'Producto')
    Producto.objects.filter(categoria='FILTROS_REFACCIONES').update(categoria='FILTOS_REFACCIONES')


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0008_alter_producto_categoria'),
    ]

    operations = [
        migrations.RunPython(corregir_categoria, revertir_categoria),
    ]