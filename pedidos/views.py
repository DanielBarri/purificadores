from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from pedidos.models import Producto, Pedido
from pedidos.dao.tiendadao import ProductoDAO, PedidoDAO
from pedidos.serializers import ProductoSerializer, PedidoSerializer
from django.http import Http404
from pedidos.carrito import Carrito
from django.contrib.auth import login
from pedidos.forms import RegistroClienteForm


# ==========================================
# 0. ROLES
# ==========================================

def es_vendedor(user):
    """Verifica si el usuario tiene rol de vendedor"""
    return user.is_authenticated and (user.groups.filter(name='Vendedor').exists() or user.is_superuser)

class EsVendedorAPI(BasePermission):
    """Permiso DRF equivalente a es_vendedor(), para las vistas de la API"""
    def has_permission(self, request, view):
        return es_vendedor(request.user)

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

def registro_view(request):
    """Registro de una cuenta de cliente"""
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('tienda')
    else:
        form = RegistroClienteForm()
    return render(request, 'mainvista/registro.html', {'form': form})

@login_required
def mis_pedidos_view(request):
    """Muestra el historial de pedidos del cliente autenticado"""
    pedidos = PedidoDAO.obtener_por_cliente(request.user)
    return render(request, 'mainvista/mis_pedidos.html', {'pedidos': pedidos})

# ==========================================
# 1.1 VISTAS WEB CARRITO (HTML)
# ==========================================

def agregar_al_carrito_action(request, producto_id):
    """Agrega un producto al carrito de la sesión"""
    if request.method == 'POST':
        producto = ProductoDAO.obtener_por_id(producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        if producto and not producto.agotado:
            carrito = Carrito(request)
            carrito.agregar(producto, cantidad)
    return redirect('carrito')

def carrito_view(request):
    """Muestra el contenido del carrito de la sesión"""
    carrito = Carrito(request)
    return render(request, 'mainvista/carrito.html', {'carrito': carrito})

def actualizar_carrito_action(request, producto_id):
    """Actualiza la cantidad de un producto en el carrito"""
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        carrito = Carrito(request)
        carrito.actualizar_cantidad(producto_id, cantidad)
    return redirect('carrito')

def eliminar_del_carrito_action(request, producto_id):
    """Elimina un producto del carrito"""
    if request.method == 'POST':
        carrito = Carrito(request)
        carrito.eliminar(producto_id)
    return redirect('carrito')

@login_required
def confirmar_pedido_action(request):
    """Convierte el carrito actual en un Pedido con sus líneas"""
    if request.method == 'POST':
        cliente_nombre = request.user.get_full_name() or request.user.username
        carrito = Carrito(request)
        pedido = PedidoDAO.crear_pedido_desde_carrito(cliente_nombre, carrito, request.user)
        if pedido:
            carrito.vaciar()
    return redirect('tienda')

@login_required
@user_passes_test(es_vendedor, login_url='/admin/login')
def cambiar_estado_action(request, pedido_id):
    """Actualiza el estado de un pedido desde la vista web"""
    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        if nuevo_estado in dict(Pedido.ESTADOS):
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
    permission_classes = [IsAuthenticated, EsVendedorAPI]

    def list(self, request):
        pedidos = PedidoDAO.obtener_todos()
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)