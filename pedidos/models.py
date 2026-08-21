from django.db import models

# Create your models here.
class Producto(models.Model):
    CATEGORIAS = [
        ('OSMOSIS', 'OSMOSIS'),
        ('SUPERFILTRACION', 'Superfiltración'),
        ('INDUSTRIAL', 'Industrial'),
    ]
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    categoria = models.CharField(max_length=10, choices=CATEGORIAS)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

class Pedido(models.Model):
    ESTADOS = [
        ('POR_CONFIRMAR', 'Por Confirmar'),
        ('RECHAZADO', 'Rechazado'),
        ('PAGADO', 'Pagado'),
        ('PREPARANDO_PEDIDO', 'Preparando Pedido'),
        ('LISTO_PARA_ENTREGA', 'Listo para Entrega'),
        ('EN_TRANSITO', 'En Tránsito'),
        ('ENTREGADO', 'Entregado'),
    ]
    cliente_nombre = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=15, choices=ESTADOS, default='POR_CONFIRMAR')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente_nombre} ({self.estado})"