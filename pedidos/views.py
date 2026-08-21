from django.shortcuts import redirect, render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.response import Response

from pedidos.dao.tiendadao import ProductoDAO, PedidoDAO
from pedidos.serializers import ProductoSerializer, PedidoSerializer

# ==========================================
# 1. VISTAS WEB (HTML)
# ==========================================

def tienda_view(request):
    """Muestra el catálogo del la tienda al cliente utilizando el DAO"""
    productos = ProductoDAO.obtener_disponibles()
    return render(request, 'mainvista/tienda.html', {'productos': productos})

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