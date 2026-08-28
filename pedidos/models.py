from django.db import models
from django.core.exceptions import ValidationError


def validar_precio_positivo(value):
    if value <= 0:
        raise ValidationError('El precio debe ser un número mayor a cero.')

# Create your models here.
class Producto(models.Model):
    CATEGORIAS = [
        ('PURIFICADORES', 'Purificadores'),
        ('FILTOS_REFACCIONES', 'Filtros y Refacciones'),
        ('PURIFICADORES_INDUSTRIALES', 'Purificadores Industriales'),
    ]
    nombre = models.CharField(max_length=100)
    modelo = models.CharField(max_length=50, null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[validar_precio_positivo])
    categoria = models.CharField(max_length=30, choices=CATEGORIAS)
    disponible = models.BooleanField(default=True)

    # Soporte para archivos multimedia (Media Files)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

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
    estado = models.CharField(max_length=20, choices=ESTADOS, default='POR_CONFIRMAR')
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente_nombre} ({self.estado})"