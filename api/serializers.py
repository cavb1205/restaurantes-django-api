from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from .models import Restaurante, Envio, RedSocial, MetodoPago, TipoCocina, Categoria, Producto, Orden, DetalleOrden

class RedSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedSocial
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class MetodoPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetodoPago
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class EnvioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Envio
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at') 
        
class TipoCocinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoCocina
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')
        
class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    class Meta:
        model = Producto
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class RestauranteSerializer(serializers.ModelSerializer):
    tipos_cocina = TipoCocinaSerializer(many=True, read_only=True) 
    redes_sociales = RedSocialSerializer(many=True, read_only=True)
    metodos_pago = MetodoPagoSerializer(many=True, read_only=True)
    envios = EnvioSerializer(many=True, read_only=True)
    
    
    
    class Meta:
        model = Restaurante
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

## Serializador para los detalles de la orden (ítems)
class DetalleOrdenSerializer(serializers.ModelSerializer):
    # Este campo 'producto_details' es SOLO para la SALIDA (lectura).
    # Obtiene los datos del campo 'producto' del modelo y los serializa usando ProductoSerializer.
    producto_details = ProductoSerializer(source='producto', read_only=True) # Campo para la SALIDA

    # El campo 'producto' (la ForeignKey al modelo Producto) se maneja implícitamente
    # por ModelSerializer al estar en Meta.fields.
    # Acepta el ID del producto en la ENTRADA por defecto. No necesitamos definirlo explícitamente aquí.


    class Meta:
        model = DetalleOrden
        # Incluimos TODOS los campos que queremos manejar.
        # 'producto': Campo del modelo (ForeignKey) - Para ENTRADA (ID) y mapeo interno.
        # 'producto_details': Campo del serializador - Para SALIDA (detalles completos del producto).
        fields = [
            'id',
            'orden',              # ForeignKey al modelo Orden
            'producto',           # ForeignKey al modelo Producto (acepta ID en entrada)
            'producto_details',   # Campo del serializador (salida con detalles completos)
            'cantidad',
            'precio_unitario',
            'subtotal',
            'created_at',
            'updated_at',
        ]
        # read_only_fields: Campos que NUNCA se aceptan en la entrada.
        # Incluye los campos automáticos, calculados, asignados por la orden padre, y los campos solo para salida.
        read_only_fields = (
            'id',
            'orden',
            'producto_details',   # <-- ¡Asegúrate de que esté aquí!
            'precio_unitario',
            'subtotal',
            'created_at',
            'updated_at',
        )


# Serializador para la orden principal
class OrdenSerializer(serializers.ModelSerializer):
    restaurante_details = RestauranteSerializer(source='restaurante', read_only=True) # <-- Salida completa del Restaurante
    metodo_pago_details = MetodoPagoSerializer(source='metodo_pago', read_only=True) # <-- Salida completa del MetodoPago
    envio_details = EnvioSerializer(source='envio', read_only=True) # <-- Salida completa del Envio



    # Campo para manejar la lista de detalles de la orden (los ítems)
    # El nombre del campo DEBE coincidir con el related_name='items' en el ForeignKey de DetalleOrden a Orden
    items = DetalleOrdenSerializer(many=True) # many=True para una lista, NO read_only=True para aceptar entrada

    class Meta:
        model = Orden
        # Incluimos todos los campos necesarios para la entrada y salida.
        # 'usuario' se asigna típicamente en la vista desde request.user.
        # 'estado' tiene un default en el modelo.
        # 'total' se calcula en el backend.
        fields = [
            'id',
            'usuario', # Si se asigna en la vista, puede ser read_only en la entrada
            'restaurante',
            'estado',
            'total',
            'metodo_pago',
            'cliente_nombre',
            'cliente_telefono',
            'cliente_email',
            'direccion_envio',
            'instrucciones_especiales',
            'envio',
            'created_at',
            'updated_at',
            'items', # Campo para la lista de ítems anidados
            'envio_details', # Detalles del envío (solo salida)
            'metodo_pago_details', # Detalles del método de pago (solo salida)
            'restaurante_details', # Detalles del restaurante (solo salida)
        ]
        # Los campos que se establecen automáticamente o se calculan son read_only
        read_only_fields = ('id', 'estado', 'total', 'created_at', 'updated_at')
        # Si el usuario se asigna en la vista:
        # read_only_fields = ('id', 'usuario', 'estado', 'total', 'created_at', 'updated_at')


    # Sobrescribir el método create para manejar la creación de la Orden y sus DetalleOrden
    @transaction.atomic # Usar una transacción para asegurar que todo se guarde o nada se guarde
    def create(self, validated_data):
        # Extraer la lista de ítems de los datos validados ANTES de crear la Orden
        items_data = validated_data.pop('items')

        # **Asignar el usuario actual si está autenticado**
        # Esto se hace comúnmente en la vista, pasando request.user al serializador:
        # serializer.save(usuario=request.user)
        # Si lo haces en el serializador (menos común pero posible si pasas el request en el context):
        usuario_instance = validated_data.pop('usuario')

        # Crear la instancia de la Orden (sin los ítems aún)
        # validated_data ahora contiene todos los campos de Orden excepto 'items'
        orden = Orden.objects.create(**validated_data)

        total_orden_calculado = 0

        # Procesar los ítems y crear los DetalleOrden
        for item_data in items_data:
            producto_id = item_data.get('producto') # Obtenemos el ID del producto de los datos del ítem
            cantidad = item_data.get('cantidad') # Obtenemos la cantidad

            # **Validar y obtener el producto y su precio actual de la base de datos**
            try:
                producto = Producto.objects.get(id=producto_id.id) # item_data['producto'] es una instancia por PrimaryKeyRelatedField
                precio_unitario_actual = producto.precio # OBTENER EL PRECIO DE LA BD
            except Producto.DoesNotExist:
                # Manejar error: el producto no existe. Lanzar una excepción de validación.
                raise serializers.ValidationError(f"El producto con ID {producto_id.id} no existe.")
            except AttributeError:
                 # Manejar error si 'producto' no es una instancia válida (debería ser manejado por PrimaryKeyRelatedField)
                 raise serializers.ValidationError("Datos de producto inválidos o faltantes en los ítems.")

            # Calcular subtotal para este ítem
            subtotal_item = cantidad * precio_unitario_actual

            # Crear la instancia de DetalleOrden
            DetalleOrden.objects.create(
                orden=orden, # Asignar la orden que acabamos de crear
                producto=producto, # Asignar la instancia del producto
                cantidad=cantidad,
                precio_unitario=precio_unitario_actual, # Usar el precio obtenido de la BD
                subtotal=subtotal_item # Usar el subtotal calculado
            )

            # Sumar al total calculado de la orden
            total_orden_calculado += subtotal_item

        # **Calcular y añadir el costo de envío al total**
        costo_envio = 0
        if orden.envio: # Verificar si se seleccionó una opción de envío (la instancia ya está en orden.envio)
             try:
                 # No necesitas hacer otro query si ya tienes la instancia relacionada
                 costo_envio = orden.envio.precio
             except AttributeError:
                  # Manejar si 'envio' no tiene el atributo precio (no debería pasar si el modelo está bien)
                  print(f"Advertencia: La instancia de Envío {orden.envio} no tiene el atributo precio.")
                  costo_envio = 0


        total_orden_calculado += costo_envio

        # Guardar el total calculado en la instancia de la Orden
        orden.total = total_orden_calculado
        orden.save() # Guardar la orden nuevamente para actualizar el total

        # Devolver la instancia de la Orden creada y completa
        return orden

 

class OrdenEstadoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializador para permitir solo la actualización del campo 'estado' de una orden.
    """
    class Meta:
        model = Orden
        fields = ['estado'] 