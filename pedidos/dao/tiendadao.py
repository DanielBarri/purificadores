from typing import List, Optional

from django.db import models
from pedidos.models import Producto, Pedido, LineaPedido

class ProductoDAO:
    """Capa DAO para operaciones de Productos"""
    
    @staticmethod
    def obtener_todos() -> List[Producto]:
        return Producto.objects.all()

    @staticmethod
    def obtener_disponibles(categoria: Optional[str] = None, query: Optional[str] = None) -> List[Producto]:
        productos = Producto.objects.filter(disponible=True)
        if categoria:
            productos = productos.filter(categoria=categoria)
        if query:
            productos = productos.filter(models.Q(nombre__icontains=query) | models.Q(modelo__icontains=query))
        return productos

    @staticmethod
    def obtener_destacados(cantidad: int = 3) -> List[Producto]:
        return Producto.objects.filter(disponible=True)[:cantidad]

    @staticmethod
    def obtener_por_id(producto_id: int) -> Optional[Producto]:
        try:
            return Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            return None


class PedidoDAO:
    """Capa DAO para operaciones de Pedidos"""

    @staticmethod
    def obtener_todos() -> List[Pedido]:
        return Pedido.objects.all().order_by('-fecha')

    @staticmethod
    def obtener_por_cliente(usuario) -> List[Pedido]:
        return Pedido.objects.filter(cliente=usuario).order_by('-fecha')

    @staticmethod
    def crear_pedido_desde_carrito(cliente_nombre: str, carrito, usuario) -> Optional[Pedido]:
        items = list(carrito)
        if not items:
            return None

        pedido = Pedido.objects.create(
            cliente_nombre=cliente_nombre,
            cliente=usuario,
            total=carrito.total(),
        )
        for item in items:
            LineaPedido.objects.create(
                pedido=pedido,
                producto=item['producto'],
                cantidad=item['cantidad'],
                precio_unitario=item['producto'].precio,
            )
        return pedido

    @staticmethod
    def cambiar_estado(pedido_id: int, nuevo_estado: str) -> Optional[Pedido]:
        try:
            pedido = Pedido.objects.get(id=pedido_id)
            pedido.estado = nuevo_estado
            pedido.save()  # Ejecuta la consulta UPDATE en la BD
            return pedido
        except Pedido.DoesNotExist:
            return None