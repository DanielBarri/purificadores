from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/productos', views.ProductoViewSet, basename='api_productos')
router.register(r'api/pedidos', views.PedidoViewSet, basename='api_pedidos')

urlpatterns = [
    # Rutas Web (HTML)
    path('', views.landing_view, name='landing'),
    path('tienda/', views.tienda_view, name='tienda'),
    path('pedidos/', views.pedidos_view, name='pedidos'),
    path('pedido/nuevo/', views.crear_pedido_action, name='crear_pedido'),
    path('pedido/<int:pedido_id>/estado/', views.cambiar_estado_action, name='cambiar_estado'),

    # Rutas API
    path('', include(router.urls)),
]