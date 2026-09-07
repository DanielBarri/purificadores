from pedidos.carrito import Carrito
from pedidos.views import es_vendedor


def carrito_cantidad(request):
    return {'carrito_cantidad': len(Carrito(request))}


def rol_usuario(request):
    return {'es_vendedor': es_vendedor(request.user)}