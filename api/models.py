from django.db import models
from django.utils.text import slugify
from django.core.validators import URLValidator
from django.conf import settings
from django.utils import timezone


class TipoCocina(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Tipo de Cocina"
        verbose_name_plural = "Tipos de Cocina"
        ordering = ['nombre']

class Restaurante(models.Model):
    ESTADOS = [
        ('abierto', 'Abierto'),
        ('cerrado', 'Cerrado'),
    ]

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='restaurantes_gestionados',
        verbose_name='Propietario/Administrador',
        null=True
    )

    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    descripcion = models.TextField()
    tipos_cocina = models.ManyToManyField(
        TipoCocina, blank=True, related_name='restaurantes', verbose_name='Tipos de Cocina')
    estado = models.CharField(
        max_length=20, choices=ESTADOS, default='abierto')
    hora_apertura = models.TimeField(default='09:00:00')
    hora_cierre = models.TimeField(default='20:00:00')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.nombre)
            slug = base_slug
            num = 1
            while Restaurante.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        owner_info = f" ({self.propietario.username})"
        return f"{self.nombre} - {owner_info}"

    class Meta:
        verbose_name = 'Restaurante'
        verbose_name_plural = 'Restaurantes'
        ordering = ['nombre']


class RedSocial(models.Model):
    TIPOS_RED = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('twitter', 'Twitter'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('whatsapp', 'WhatsApp'),
    ]

    restaurante = models.ForeignKey(
        'Restaurante', on_delete=models.CASCADE, related_name='redes_sociales')
    tipo = models.CharField(max_length=20, choices=TIPOS_RED)
    url = models.URLField(max_length=200, validators=[URLValidator()])
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Red Social'
        verbose_name_plural = 'Redes Sociales'
        ordering = ['orden']
        unique_together = ['restaurante', 'tipo']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.restaurante.nombre}"


class MetodoPago(models.Model):
    TIPOS_PAGO = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),

    ]

    restaurante = models.ForeignKey(
        'Restaurante', on_delete=models.CASCADE, related_name='metodos_pago')
    tipo = models.CharField(max_length=20, choices=TIPOS_PAGO)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    configuracion = models.JSONField(
        blank=True, null=True, help_text="Configuración del método de pago")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
        ordering = ['orden']
        unique_together = ['restaurante', 'tipo']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.restaurante.nombre}"


class Envio(models.Model):
    ESTADOS_ENVIO = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=100)
    estado = models.CharField(
        max_length=20, choices=ESTADOS_ENVIO, default='activo')
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name='envios')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nombre} - {self.restaurante.nombre}"


class Categoria(models.Model):
    """Categorías para los productos del menú """
    
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100,
                            blank=True,
                            help_text="En blanco para autogenerar basado en el nombre")
    descripcion = models.TextField(blank=True, null=True)
    orden = models.PositiveIntegerField(
        default=0, help_text="Orden de aparición en el menú")
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Crear slug único para la categoría dentro del restaurante
            base_slug = slugify(self.nombre)
            slug = base_slug
            num = 1
            # Asegurar que el slug sea único PARA ESTE RESTAURANTE
            while Categoria.objects.filter(restaurante=self.restaurante, slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre}"

    class Meta:
        verbose_name = 'Categoría de Producto'
        verbose_name_plural = 'Categorías de Productos'
        #luego por orden y nombre
        ordering = ['orden', 'nombre']
        
        
        


class Producto(models.Model):
    """Productos individuales del menú"""
    DISPONIBILIDAD = [
        ('disponible', 'Disponible'),
        ('agotado', 'Agotado Temporalmente'),
        # Puedes añadir más estados si necesitas
    ]

    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='productos')
    restaurante = models.ForeignKey(
        Restaurante, on_delete=models.CASCADE, related_name='productos', null=True)
    nombre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True,
                            help_text="Dejar en blanco para autogenerar basado en el nombre")
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    activo = models.BooleanField(
        default=True, help_text="Indica si el producto se muestra en el menú")
    disponibilidad = models.CharField(
        max_length=20, choices=DISPONIBILIDAD, default='disponible')
    orden = models.PositiveIntegerField(
        default=0, help_text="Orden de aparición dentro de la categoría")
    # Opcional: Campo para destacar un producto
    destacado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def save(self, *args, **kwargs):
        if not self.slug:
            # Crear slug único para el producto dentro de su categoría
            base_slug = slugify(self.nombre)
            slug = base_slug
            num = 1
            # Asegurar que el slug sea único PARA ESTA CATEGORÍA
            while Producto.objects.filter(categoria=self.categoria, slug=slug).exists():
                slug = f'{base_slug}-{num}'
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.categoria.nombre})"

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        # Ordenar por categoría, luego por orden y nombre
        ordering = ['orden', 'nombre']
        # El slug debe ser único por categoría
        
        
class Orden(models.Model):
    """Representa una orden realizada por un usuario."""

    ESTADOS_ORDEN = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('en_camino', 'En Camino'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT, # No borrar el usuario si tiene órdenes
        related_name='ordenes',
        verbose_name='Cliente',
        null=True,
        blank=True # Puede ser nulo si la orden es anónima o no autenticada
    )
    restaurante = models.ForeignKey(
        'Restaurante',
        on_delete=models.PROTECT, # No borrar el restaurante si tiene órdenes
        related_name='ordenes',
        verbose_name='Restaurante'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_ORDEN,
        default='pendiente',
        verbose_name='Estado de la Orden'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total de la Orden',
        null=True
    )
    metodo_pago = models.ForeignKey(
        'MetodoPago',
        on_delete=models.SET_NULL, # Si se elimina el método de pago, no eliminar la orden
        related_name='ordenes',
        verbose_name='Método de Pago',
        null=True, # Puede ser nulo si el pago falla o es contra entrega
        blank=True
    )
    cliente_nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre del Cliente')
    cliente_telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono del Cliente')
    cliente_email = models.EmailField(max_length=254, blank=True, null=True, verbose_name='Correo del Cliente')
    direccion_envio = models.TextField(
        verbose_name='Dirección de Envío'
    )
    instrucciones_especiales = models.TextField(
        verbose_name='Instrucciones Especiales',
        blank=True,
        null=True
    )
    envio = models.ForeignKey(
        'Envio',
        on_delete=models.SET_NULL, # Si se elimina la opción de envío, no eliminar la orden
        related_name='ordenes',
        verbose_name='Opción de Envío',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at'] # Las órdenes más recientes primero

    def __str__(self):
        return f"Orden #{self.pk} - {self.get_estado_display()}"

    # Puedes añadir un método para calcular el total si no lo calculas antes de guardar
    # def calcular_total(self):
    #     return sum(item.subtotal for item in self.items.all())


class DetalleOrden(models.Model):
    """Representa un producto específico dentro de una orden."""

    orden = models.ForeignKey(
        'Orden',
        on_delete=models.CASCADE, # Si se elimina la orden, eliminar sus detalles
        related_name='items', # Para acceder a los detalles desde la orden: orden.items.all()
        verbose_name='Orden'
    )
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.PROTECT, # No eliminar el producto si está en una orden
        related_name='detalles_orden',
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField(
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio Unitario al momento de la Orden'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal del Item'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        null=True
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización',
        null=True
    )

    class Meta:
        verbose_name = 'Detalle de Orden'
        verbose_name_plural = 'Detalles de Órdenes'
        # Un producto dentro de una orden específica es único
        unique_together = ['orden', 'producto']

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Orden #{self.orden.pk}"

    # Opcional: Sobrescribir save para asegurar que el subtotal se calcule automáticamente
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)