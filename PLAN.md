# Plan de Funcionalidades — Aquosan Purificadores (Tienda en Línea)

## Contexto del negocio
Tienda en línea de sistemas de purificación de agua por ósmosis inversa,
con productos para hogar (Purificadores, Filtros y Refacciones) y para
uso industrial (Purificadores Industriales, mismo flujo de compra que
el resto — no requieren cotización manual separada).

## Estado actual del proyecto

Lo que ya existe y funciona:
- Modelos `Producto` (nombre, modelo, precio, categoría, disponible, imagen)
  y `Pedido` (cliente, producto único vía FK, estado, total, fecha).
- Vista de catálogo (`tienda_view`) que lista productos disponibles.
- Botón "Comprar" que crea un `Pedido` directo, sin carrito ni checkout.
- Vista de pedidos (`pedidos_view`) protegida para rol "Vendedor", con
  cambio de estado manual (Por Confirmar → ... → Entregado).
- Panel de administración Django con carga masiva de productos vía CSV.
- API REST de solo lectura (`/api/productos/`, `/api/pedidos/`).
- Configuración de entorno vía `.env` (SECRET_KEY, DEBUG, ALLOWED_HOSTS).

Limitación central: **un pedido solo puede tener un producto**. No existe
carrito, ni checkout, ni cuentas de cliente, ni pagos.

## Decisiones de negocio (confirmadas)

1. **Pagos:** pasarela en línea con **Mercado Pago**.
2. **Cuentas de cliente:** registro/inicio de sesión **obligatorio** para
   poder comprar (no habrá checkout de invitado).
3. **Envíos:** se usará **Skydropx**, pero su integración queda para una
   iteración posterior. Por ahora el checkout debe capturar la dirección
   de envío como datos simples, sin cálculo de tarifas ni guías.
4. **Facturación fiscal (CFDI):** se implementará en una sesión posterior;
   no forma parte del alcance actual.
5. **Purificadores industriales:** se compran igual que cualquier otro
   producto, sin flujo de cotización especial.
6. **Estilos:** sin frameworks de CSS (se descarta Bootstrap y Tailwind).
   Todo el sitio se estiliza con **CSS nativo** escrito a mano en
   `static/css/`. Implica reescribir `base.html`, `tienda.html` y
   `pedidos.html` (hoy usan clases de Bootstrap) además del nuevo
   template de landing page.

---

## Fase 1 — Landing Page pública
Página de entrada distinta del catálogo, visible sin login, para
marketing y confianza de marca.

- [x] Quitar el CDN de Bootstrap de `base.html` y reemplazarlo por CSS
      nativo propio (`static/css/`).
- [x] Reescribir `tienda.html` sin clases de Bootstrap (con sistema de
      diseño glassmorphism: paleta, tipografía Inter, íconos Material
      Symbols, fondo animado). `pedidos.html` queda pendiente, se hará
      en una sesión posterior.
- [x] Hero con propuesta de valor (agua purificada, ósmosis inversa),
      con imagen real (`static/img/hero.jpg`).
- [x] Sección de beneficios / tecnología (ósmosis inversa, filtros y
      refacciones, uso doméstico e industrial).
- [x] Sección de productos destacados (tomados en vivo del catálogo)
      con link a la tienda.
- [ ] Testimonios o garantías (si aplica).
- [x] Llamado a la acción hacia `/tienda/` (hero y sección de destacados).
- [ ] Footer con contacto, redes sociales, datos legales — por ahora
      solo tiene marca y enlaces internos (Tienda/Pedidos).
- [x] Ruta raíz (`/`) muestra landing; catálogo se movió a `/tienda/`.

## Fase 2 — Tienda / Catálogo
- [ ] Página de detalle de producto (`/tienda/producto/<id>/`) con
      descripción extendida, especificaciones técnicas, galería.
- [ ] Filtro por categoría en la vista de tienda.
- [ ] Buscador por nombre/modelo.
- [ ] Campo `descripcion` y `stock` (cantidad disponible) en `Producto`.
- [ ] Ocultar automáticamente productos sin stock (o mostrar "agotado").

## Fase 3 — Carrito de compras
Requiere rediseñar el modelo de datos: un pedido debe soportar
**múltiples productos y cantidades**, no un FK único como hoy.

- [ ] Nuevo modelo `LineaPedido` con `producto`, `cantidad`,
      `precio_unitario`, y FK a `Pedido`. Retirar el FK único
      `Pedido.producto`.
- [ ] Carrito persistente en sesión (funciona sin login todavía).
- [ ] Botón "Agregar al carrito" en vez de "Comprar" directo.
- [ ] Vista de carrito: ver/editar cantidades, quitar producto, subtotal.
- [ ] Cálculo de total dinámico (suma de líneas; envío se agrega en
      fase futura con Skydropx).

## Fase 4 — Cuentas de cliente
Prerrequisito para el checkout, ya que la compra exige sesión iniciada.

- [ ] Modelo de cliente (puede extender `User` de Django o usar un
      `Cliente` con OneToOne a `User`).
- [ ] Registro e inicio de sesión de clientes (distinto del login de
      "Vendedor"/staff que ya existe).
- [ ] El carrito puede armarse sin login, pero al ir a pagar redirige a
      login/registro si no hay sesión.
- [ ] Historial de pedidos del cliente autenticado.

## Fase 5 — Checkout y Pedidos
- [ ] Formulario de checkout: datos de contacto y dirección de envío
      simples (calle, ciudad, CP, teléfono) — sin integración de
      paquetería todavía.
- [ ] Confirmación de pedido antes de enviarlo a pago.
- [ ] Notificación por correo al cliente y/o vendedor al crear pedido y
      al cambiar de estado.
- [ ] Página "gracias por tu compra" con número de orden.

## Fase 6 — Integración de pago (Mercado Pago)
- [ ] Alta de cuenta/credenciales de Mercado Pago (Checkout Pro o API).
- [ ] Redirección a Mercado Pago desde el checkout con el total del
      carrito.
- [ ] Webhook de confirmación de pago que actualiza el estado del
      pedido automáticamente (de "Por Confirmar" a "Pagado").
- [ ] Manejo de pagos fallidos/cancelados/pendientes.

## Fase 7 — Panel administrativo / vendedor
- [ ] Completar API REST (create/update) si se necesita para algún
      frontend externo.
- [ ] Conectar `ProductoModelForm` a validaciones reales del admin y
      del importador CSV.
- [ ] Definir el propósito real de `AuditoriaSeguridadMiddleware`
      (métricas vs. auditoría real) y completarlo.
- [ ] Reportes básicos: ventas por periodo, productos más vendidos.

## Fase 8 — Infraestructura y producción
- [ ] Elegir base de datos de producción (¿se queda en SQLite o pasa a
      PostgreSQL?).
- [ ] Servir archivos estáticos/media en producción (Whitenoise, S3, o
      similar).
- [ ] Definir hosting/despliegue (Railway, Render, DigitalOcean, VPS).
- [ ] Pruebas automatizadas (actualmente `pedidos/tests.py` está vacío).
- [ ] HTTPS y hardening de settings (`SECURE_*` de Django) para
      producción.

---

## Backlog futuro (fuera del alcance actual)
- **Envíos con Skydropx:** cálculo de tarifas en tiempo real, generación
  de guías, tracking del pedido.
- **Facturación fiscal (CFDI):** timbrado y entrega de factura al
  cliente.
