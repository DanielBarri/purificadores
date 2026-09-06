from pedidos.carrito import Carrito


def carrito_cantidad(request):
    return {'carrito_cantidad': len(Carrito(request))}