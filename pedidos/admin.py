from django.contrib import admin

# Register your models here.
from .models import Producto, Pedido

admin.site.site_header = "Administración Tienda Aquosan Purificadores"
admin.site.site_title = "Panel Aquosan Purificadores"
admin.site.index_title = "Gestión de Productos y Pedidos"

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'precio', 'categoria', 'disponible')
    list_filter = ('categoria', 'disponible')
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'estado', 'total', 'fecha')
    list_filter = ('estado', 'fecha')
    search_fields = ('cliente_nombre',)