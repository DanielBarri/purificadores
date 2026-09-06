from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response

from pedidos.models import Producto
from pedidos.dao.tiendadao import ProductoDAO, PedidoDAO
from pedidos.serializers import ProductoSerializer, PedidoSerializer
from django.http import Http404


# ==========================================
# 0. ROLES
# ==========================================

def es_vendedor(user):
    """Verifica si el usuario tiene rol de vendedor"""
    return user.is_authenticated and (user.groups.filter(name='Vendedor').exists() or user.is_superuser)

# ==========================================
# 1. VISTAS WEB (HTML)
# ==========================================

def landing_view(request):
    """Muestra la página de inicio del sitio web"""
    productos_destacados = ProductoDAO.obtener_destacados()
    return render(request, 'mainvista/landing.html', {'productos_destacados': productos_destacados})

def tienda_view(request):
    """Muestra el catálogo del la tienda al cliente utilizando el DAO"""
    categoria = request.GET.get('categoria')
    query = request.GET.get('q')
    productos = ProductoDAO.obtener_disponibles(categoria=categoria, query=query)
    context = {
        'productos': productos,
        'categorias': Producto.CATEGORIAS,
        'categoria_actual': categoria,
        'query_actual': query or '',
    }
    return render(request, 'mainvista/tienda.html', context)

def producto_detalle_view(request, producto_id):
    """Muestra el detalle de un producto especifico"""
    producto = ProductoDAO.obtener_por_id(producto_id)
    if not producto:
        raise Http404("Producto no encontrado")
    return render(request, 'mainvista/producto_detalle.html', {'producto': producto})

@login_required
@user_passes_test(es_vendedor, login_url='/admin/login')
def pedidos_view(request):
    """Muestra los pedidos al cliente utilizando el DAO"""
    pedidos = PedidoDAO.obtener_todos()
    return render(request, 'mainvista/pedidos.html', {'pedidos': pedidos})

def crear_pedido_action(request):
    """Procesa el formulario web de un nuevo pedido"""
    if request.method == 'POST':
        cliente_nombre = request.POST.get('cliente_nombre')
        producto_id = request.POST.get('producto_id')
        PedidoDAO.crear_pedido_con_producto(cliente_nombre, producto_id)
    return redirect('pedidos')

def cambiar_estado_action(request, pedido_id):
    """Actualiza el estado de un pedido desde la vista web"""
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        PedidoDAO.cambiar_estado(pedido_id, nuevo_estado)
    return redirect('pedidos')


# ==========================================
# 2. VISTAS API REST (JSON)
# ==========================================

class ProductoViewSet(viewsets.ViewSet):
    def list(self, request):
        productos = ProductoDAO.obtener_todos()
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

class PedidoViewSet(viewsets.ViewSet):
    def list(self, request):
        pedidos = PedidoDAO.obtener_todos()
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)