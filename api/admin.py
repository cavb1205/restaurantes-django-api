from django.contrib import admin

from .models import (
    Restaurante,
    RedSocial,
    MetodoPago,
    Envio,
    Categoria,
    Producto,
    TipoCocina,
    Orden,
    DetalleOrden
)

admin.site.register(Producto) 
admin.site.register(Orden)
admin.site.register(DetalleOrden)

class RedSocialInline(admin.TabularInline): # O StackedInline para otra vista
    model = RedSocial
    extra = 1 # Número de formularios extra para añadir nuevas redes
    ordering = ('orden',)

class MetodoPagoInline(admin.TabularInline):
    model = MetodoPago
    extra = 1
    ordering = ('orden',)

class EnvioInline(admin.TabularInline):
    model = Envio
    extra = 1

class CategoriaInline(admin.TabularInline):
    model = Categoria
    extra = 1
    ordering = ('orden', 'nombre',)
    prepopulated_fields = {'slug': ('nombre',)} # Autocompletar slug desde nombre


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'propietario', 'telefono', 'estado', 'direccion')
    list_filter = ('estado', 'propietario', 'tipos_cocina') # Permite filtrar por estos campos
    search_fields = ('nombre', 'slug', 'propietario__username', 'telefono', 'direccion') # Campos por los que buscar
    prepopulated_fields = {'slug': ('nombre',)} # Autocompletar slug desde nombre
    readonly_fields = ('created_at', 'updated_at') # Campos que no se pueden editar
    fieldsets = ( # Organizar campos en el formulario de edición
        (None, {
            'fields': ('propietario', 'nombre', 'slug', 'logo', 'descripcion')
        }),
        ('Contacto y Ubicación', {
            'fields': ('direccion', 'telefono')
        }),
        ('Clasificación', {
            'fields': ('tipos_cocina',)
        }),
        ('Operación', {
            'fields': ('estado', 'hora_apertura', 'hora_cierre')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',) # Ocultar por defecto
        }),
    )
    filter_horizontal = ('tipos_cocina',) # Permite seleccionar múltiples tipos de cocina
    # Añadir los inlines para editar modelos relacionados directamente desde Restaurante
    inlines = [RedSocialInline, MetodoPagoInline, EnvioInline]

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre','orden', 'activo')
    list_filter = ('activo', ) # Filtrar por restaurante
    search_fields = ('nombre', 'slug',)
    list_editable = ('orden', 'activo') # Permite editar estos campos directamente en la lista
    prepopulated_fields = {'slug': ('nombre',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ( 'orden', 'nombre')
    # Opcional: Añadir inline de productos aquí si prefieres gestionar productos desde la categoría
    # inlines = [ProductoInline]




 

@admin.register(RedSocial)
class RedSocialAdmin(admin.ModelAdmin):
    list_display = ('restaurante', 'tipo', 'orden', 'activo')
    list_filter = ('activo', 'tipo', 'restaurante__nombre')
    search_fields = ('restaurante__nombre', 'url')
    list_editable = ('orden', 'activo')
    ordering = ('restaurante__nombre', 'orden')
    readonly_fields = ('created_at', 'updated_at')
    
@admin.register(TipoCocina)
class TipoCocinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    search_fields = ('nombre',)
    prepopulated_fields = {'slug': ('nombre',)} # Útil para autocompletar el slug

# Register your models here.

