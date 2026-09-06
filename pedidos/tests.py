from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from pedidos.models import Producto, Pedido


class TiendaSmokeTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Purificador de Prueba',
            precio=1500,
            categoria='PURIFICADORES',
            stock=5,
        )

    def test_landing_carga_correctamente(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)

    def test_tienda_carga_y_muestra_productos(self):
        response = self.client.get(reverse('tienda'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Purificador de Prueba')

    def test_detalle_producto_existente(self):
        url = reverse('producto_detalle', args=[self.producto.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Purificador de Prueba')

    def test_detalle_producto_inexistente_da_404(self):
        url = reverse('producto_detalle', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class CarritoSmokeTest(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre='Filtro de Prueba',
            precio=500,
            categoria='FILTOS_REFACCIONES',
            stock=10,
        )
        self.usuario = User.objects.create_user(username='cliente1', password='clave12345')

    def test_agregar_al_carrito_incrementa_sesion(self):
        url = reverse('agregar_al_carrito', args=[self.producto.id])
        self.client.post(url, {'cantidad': 2})
        session = self.client.session
        self.assertEqual(session['carrito'][str(self.producto.id)]['cantidad'], 2)

    def test_ver_carrito_muestra_producto_agregado(self):
        self.client.post(reverse('agregar_al_carrito', args=[self.producto.id]), {'cantidad': 1})
        response = self.client.get(reverse('carrito'))
        self.assertContains(response, 'Filtro de Prueba')

    def test_confirmar_pedido_sin_login_redirige_a_login(self):
        self.client.post(reverse('agregar_al_carrito', args=[self.producto.id]), {'cantidad': 1})
        response = self.client.post(reverse('confirmar_pedido'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_confirmar_pedido_logueado_crea_pedido_y_vacia_carrito(self):
        self.client.login(username='cliente1', password='clave12345')
        self.client.post(reverse('agregar_al_carrito', args=[self.producto.id]), {'cantidad': 3})
        self.client.post(reverse('confirmar_pedido'))

        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.cliente, self.usuario)
        self.assertEqual(pedido.lineas.count(), 1)
        self.assertEqual(pedido.lineas.first().cantidad, 3)

        session = self.client.session
        self.assertEqual(session['carrito'], {})       

class CuentasSmokeTest(TestCase):
    def test_registro_crea_usuario_y_inicia_sesion(self):
        response = self.client.post(reverse('registro'), {
            'username': 'nuevocliente',
            'email': 'nuevo@example.com',
            'password1': 'ContrasenaSegura123',
            'password2': 'ContrasenaSegura123',
        })
        self.assertTrue(User.objects.filter(username='nuevocliente').exists())
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_con_credenciales_correctas(self):
        User.objects.create_user(username='usuarioexistente', password='clave12345')
        response = self.client.post(reverse('login'), {
            'username': 'usuarioexistente',
            'password': 'clave12345',
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_mis_pedidos_requiere_login(self):
        response = self.client.get(reverse('mis_pedidos'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_panel_vendedor_bloqueado_a_cliente_normal(self):
        User.objects.create_user(username='clientenormal', password='clave12345')
        self.client.login(username='clientenormal', password='clave12345')
        response = self.client.get(reverse('pedidos'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login'))

    def test_cambiar_estado_bloqueado_a_cliente_normal(self):
        pedido = Pedido.objects.create(cliente_nombre='Ana', total=100)
        User.objects.create_user(username='clientenormal2', password='clave12345')
        self.client.login(username='clientenormal2', password='clave12345')
        url = reverse('cambiar_estado', args=[pedido.id])
        response = self.client.post(url, {'nuevo_estado': 'ENTREGADO'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/admin/login'))
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado, 'POR_CONFIRMAR')

    def test_api_pedidos_requiere_rol_vendedor(self):
        Pedido.objects.create(cliente_nombre='Ana', total=100)

        # Sin sesión: acceso denegado.
        response = self.client.get('/api/pedidos/')
        self.assertEqual(response.status_code, 403)

        # Con sesión pero sin rol de vendedor: autenticado, pero sin permiso (403).
        User.objects.create_user(username='clientenormal3', password='clave12345')
        self.client.login(username='clientenormal3', password='clave12345')
        response = self.client.get('/api/pedidos/')
        self.assertEqual(response.status_code, 403)

        