from pedidos.models import Producto

CARRITO_SESSION_KEY = 'carrito'


class Carrito:
    """Envuelve request.session para manejar el carrito de compras."""

    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get(CARRITO_SESSION_KEY)
        if carrito is None:
            carrito = self.session[CARRITO_SESSION_KEY] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id)
        if producto_id in self.carrito:
            self.carrito[producto_id]['cantidad'] += cantidad
        else:
            self.carrito[producto_id] = {'cantidad': cantidad}
        self.guardar()

    def actualizar_cantidad(self, producto_id, cantidad):
        producto_id = str(producto_id)
        if producto_id not in self.carrito:
            return
        if cantidad > 0:
            self.carrito[producto_id]['cantidad'] = cantidad
        else:
            self.eliminar(producto_id)
        self.guardar()

    def eliminar(self, producto_id):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def vaciar(self):
        self.session[CARRITO_SESSION_KEY] = {}
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def __iter__(self):
        productos = Producto.objects.filter(id__in=self.carrito.keys())
        productos_por_id = {str(producto.id): producto for producto in productos}
        for producto_id, datos in self.carrito.items():
            producto = productos_por_id.get(producto_id)
            if not producto:
                continue
            item = dict(datos)
            item['producto'] = producto
            item['subtotal'] = producto.precio * datos['cantidad']
            yield item

    def __len__(self):
        return sum(datos['cantidad'] for datos in self.carrito.values())

    def total(self):
        return sum(item['subtotal'] for item in self)