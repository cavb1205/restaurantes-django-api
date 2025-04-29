from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from rest_framework import status
from .models import Restaurante, Envio, RedSocial, MetodoPago, Producto, Orden, Categoria
from .serializers import (
    RestauranteSerializer, EnvioSerializer, RedSocialSerializer,
    MetodoPagoSerializer, ProductoSerializer, OrdenSerializer,OrdenEstadoUpdateSerializer, CategoriaSerializer, ProductoClienteSerializer
)

# Create your views here.

@api_view(['GET', 'POST']) # Permite GET para listar, POST para crear
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante como parámetro de la URL
def redsocial_list_create_restaurante(request, restaurante_slug):
    """
    Lista redes sociales para un restaurante específico por slug (GET)
    o crea una nueva red social para ese restaurante (POST).
    Verifica que el usuario autenticado sea el propietario.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Si la verificación de permiso pasa...
    if request.method == 'GET':
        # 2. Si es GET: Listar todas las redes sociales de ESTE restaurante
        # Filtramos las redes sociales por el restaurante encontrado.
        # Asumiendo que tienes un campo 'orden' en RedSocial para ordenar
        redes_sociales = RedSocial.objects.filter(restaurante=restaurante).order_by('orden')
        # Serializar la lista de redes sociales.
        serializer = RedSocialSerializer(redes_sociales, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 2. Si es POST: Crear una nueva red social.
        # El serializador valida los datos recibidos (tipo, url, orden, activo).
        # El campo 'restaurante' en el serializador es read_only y NO se espera en los datos de entrada.
        serializer = RedSocialSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la nueva instancia de RedSocial.
            # **Inyectamos manualmente el restaurante** encontrado y verificado,
            # asociando la nueva red social a este restaurante.
            red_social_creada = serializer.save(restaurante=restaurante)

            # Serializar la red social creada para la respuesta.
            return Response(RedSocialSerializer(red_social_creada).data, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE']) # Permite GET, PUT, PATCH, DELETE
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante y el ID de la red social como parámetros
def redsocial_detail_update_delete_restaurante(request, restaurante_slug, red_social_id):
    """
    Recupera (GET), actualiza (PUT/PATCH) o elimina (DELETE) una red social específica por ID,
    verificando que pertenezca al restaurante del usuario autenticado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar la propiedad.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar la red social por su ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    # get_object_or_404 buscará por ID y añadirá el filtro por restaurante.
    red_social = get_object_or_404(RedSocial, id=red_social_id, restaurante=restaurante)


    # Si la verificación de permiso y la pertenencia de la red social pasan...
    if request.method == 'GET':
        # 3. Si es GET: Recuperar los detalles de la red social
        serializer = RedSocialSerializer(red_social)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # 3. Si es PUT o PATCH: Actualizar la red social.
        partial = request.method == 'PATCH' # partial=True para PATCH
        # Inicializa el serializador con la instancia existente y los datos de la petición.
        # El campo 'restaurante' no debe enviarse (es read_only).
        serializer = RedSocialSerializer(red_social, data=request.data, partial=partial)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la instancia actualizada. No necesitamos pasar 'restaurante'.
            serializer.save()
            # Devolver la red social actualizada serializada.
            return Response(serializer.data)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 3. Si es DELETE: Eliminar la red social.
        red_social.delete()
        # Devolver una respuesta de éxito sin contenido.
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST']) # Permite GET para listar, POST para crear
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante como parámetro de la URL
def envio_list_create_restaurante(request, restaurante_slug):
    """
    Lista opciones de envío para un restaurante específico por slug (GET)
    o crea una nueva opción de envío para ese restaurante (POST).
    Verifica que el usuario autenticado sea el propietario.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Si la verificación de permiso pasa...
    if request.method == 'GET':
        # 2. Si es GET: Listar todas las opciones de envío de ESTE restaurante
        # Filtramos las opciones de envío por el restaurante encontrado.
        # Puedes añadir ordenamiento aquí, ej: .order_by('precio', 'nombre')
        envios = Envio.objects.filter(restaurante=restaurante).order_by('precio', 'nombre')
        # Serializar la lista de opciones de envío.
        serializer = EnvioSerializer(envios, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 2. Si es POST: Crear una nueva opción de envío.
        # El serializador valida los datos recibidos (nombre, estado, precio).
        # El campo 'restaurante' en el serializador es read_only y NO se espera en los datos de entrada.
        serializer = EnvioSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la nueva instancia de Envio.
            # **Inyectamos manualmente el restaurante** encontrado y verificado,
            # asociando la nueva opción de envío a este restaurante.
            envio_creado = serializer.save(restaurante=restaurante)

            # Serializar la opción de envío creada para la respuesta.
            return Response(EnvioSerializer(envio_creado).data, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE']) # Permite GET, PUT, PATCH, DELETE
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante y el ID de la opción de envío como parámetros
def envio_detail_update_delete_restaurante(request, restaurante_slug, envio_id):
    """
    Recupera (GET), actualiza (PUT/PATCH) o elimina (DELETE) una opción de envío específica por ID,
    verificando que pertenezca al restaurante del usuario autenticado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar la propiedad.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar la opción de envío por su ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    # get_object_or_404 buscará por ID y añadirá el filtro por restaurante.
    envio = get_object_or_404(Envio, id=envio_id, restaurante=restaurante)


    # Si la verificación de permiso y la pertenencia de la opción de envío pasan...
    if request.method == 'GET':
        # 3. Si es GET: Recuperar los detalles de la opción de envío
        serializer = EnvioSerializer(envio)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # 3. Si es PUT o PATCH: Actualizar la opción de envío.
        partial = request.method == 'PATCH' # partial=True para PATCH
        # Inicializa el serializador con la instancia existente y los datos de la petición.
        # El campo 'restaurante' no debe enviarse (es read_only).
        serializer = EnvioSerializer(envio, data=request.data, partial=partial)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la instancia actualizada. No necesitamos pasar 'restaurante'.
            serializer.save()
            # Devolver la opción de envío actualizada serializada.
            return Response(serializer.data)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 3. Si es DELETE: Eliminar la opción de envío.
        envio.delete()
        # Devolver una respuesta de éxito sin contenido.
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST']) # Permite GET para listar, POST para crear
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante como parámetro de la URL
def metodopago_list_create_restaurante(request, restaurante_slug):
    """
    Lista métodos de pago para un restaurante específico por slug (GET)
    o crea un nuevo método de pago para ese restaurante (POST).
    Verifica que el usuario autenticado sea el propietario.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Si la verificación de permiso pasa...
    if request.method == 'GET':
        # 2. Si es GET: Listar todos los métodos de pago de ESTE restaurante
        # Filtramos los métodos de pago por el restaurante encontrado.
        metodos_pago = MetodoPago.objects.filter(restaurante=restaurante).order_by('orden') # Asumiendo que tienes un campo 'orden' en MetodoPago
        # Serializar la lista de métodos de pago.
        serializer = MetodoPagoSerializer(metodos_pago, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 2. Si es POST: Crear un nuevo método de pago.
        # El serializador valida los datos recibidos (tipo, descripcion, orden, activo, configuracion).
        # El campo 'restaurante' en el serializador es read_only y NO se espera en los datos de entrada.
        serializer = MetodoPagoSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la nueva instancia de MetodoPago.
            # **Inyectamos manualmente el restaurante** encontrado y verificado,
            # asociando el nuevo método de pago a este restaurante.
            metodo_pago_creado = serializer.save(restaurante=restaurante)

            # Serializar el método de pago creado para la respuesta.
            return Response(MetodoPagoSerializer(metodo_pago_creado).data, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE']) # Permite GET, PUT, PATCH, DELETE
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante y el ID del método de pago como parámetros
def metodopago_detail_update_delete_restaurante(request, restaurante_slug, metodo_pago_id):
    """
    Recupera (GET), actualiza (PUT/PATCH) o elimina (DELETE) un método de pago específico por ID,
    verificando que pertenezca al restaurante del usuario autenticado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar la propiedad.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar el método de pago por su ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    # get_object_or_404 buscará por ID y añadirá el filtro por restaurante.
    metodo_pago = get_object_or_404(MetodoPago, id=metodo_pago_id, restaurante=restaurante)


    # Si la verificación de permiso y la pertenencia del método de pago pasan...
    if request.method == 'GET':
        # 3. Si es GET: Recuperar los detalles del método de pago
        serializer = MetodoPagoSerializer(metodo_pago)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # 3. Si es PUT o PATCH: Actualizar el método de pago.
        partial = request.method == 'PATCH' # partial=True para PATCH
        # Inicializa el serializador con la instancia existente y los datos de la petición.
        # El campo 'restaurante' no debe enviarse (es read_only).
        serializer = MetodoPagoSerializer(metodo_pago, data=request.data, partial=partial)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la instancia actualizada. No necesitamos pasar 'restaurante'.
            serializer.save()
            # Devolver el método de pago actualizado serializado.
            return Response(serializer.data)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 3. Si es DELETE: Eliminar el método de pago.
        metodo_pago.delete()
        # Devolver una respuesta de éxito sin contenido.
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def producto_list_by_restaurante_slug(request, restaurante_slug):
    """
    Devuelve todos los productos del restaurante especificado por el slug en la URL.
    """
    try:
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)
        productos = Producto.objects.filter(restaurante=restaurante)
        serializer = ProductoClienteSerializer(productos, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
def restaurante_list_create(request):
    if request.method == 'GET':
        restaurantes = Restaurante.objects.all().order_by('estado','slug')
        serializer = RestauranteSerializer(restaurantes, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RestauranteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def restaurante_detail(request, slug):
    
    try:
        
        restaurante = get_object_or_404(Restaurante, slug=slug)
        
    except Restaurante.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RestauranteSerializer(restaurante)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = RestauranteSerializer(restaurante, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        restaurante.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def restaurante_detail_id(request, pk):
    
    try:
        
        restaurante = get_object_or_404(Restaurante, id=pk)
        
    except Restaurante.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RestauranteSerializer(restaurante)
        return Response(serializer.data)
    

@api_view(['GET', 'POST'])
def envio_list_create(request):
    if request.method == 'GET':
        envios = Envio.objects.all()
        serializer = EnvioSerializer(envios, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = EnvioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def envio_detail(request, pk):
    try:
        envio = Envio.objects.get(pk=pk)
    except Envio.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EnvioSerializer(envio)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = EnvioSerializer(envio, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        envio.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST']) # Solo permitirá peticiones POST
# Si requieres que el usuario esté logueado para crear órdenes, descomenta la línea de abajo:
# @permission_classes([IsAuthenticated])
def crear_orden(request):
    """
    Crea una nueva orden.
    """
    print("ingresa a crear orden")
    print(request.data)
    print("usuario autenticado:", request.user) # Verifica el usuario autenticado
    # Inicializa el serializador con los datos de la petición
    # Pasar 'request' en context es útil si tu serializador necesita acceder al usuario actual
    # para validar algo o si asignas el usuario dentro del serializador (menos común)
    serializer = OrdenSerializer(data=request.data, context={'request': request})
    

    # Valida los datos recibidos
    if serializer.is_valid():
        # Si los datos son válidos, guarda la nueva orden y sus detalles
        # Si el campo 'usuario' en el modelo Orden NO permite null=True
        # y quieres que la orden se asocie al usuario autenticado,
        # DEBES pasarlo al método save del serializador:
        orden_creada = serializer.save(usuario=request.user) # Asigna el usuario autenticadoç
        print("Orden creada:", orden_creada)

        # Devuelve una respuesta con los datos de la orden creada y estado 201 Created
        # El serializador (después de save) contendrá los datos completos de la orden creada, incluyendo el total calculado, etc.
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # Si los datos no son válidos, devuelve los errores y estado 400 Bad Request
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def orden_detail(request, pk):
    """
    Devuelve los detalles de una orden específica.
    """
    try:
        orden = Orden.objects.get(pk=pk)
    except Orden.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrdenSerializer(orden)
        return Response(serializer.data)
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = OrdenSerializer(orden)
        return Response(serializer.data)
    return Response(status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET']) # Solo permitirá peticiones GET
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
def listar_ordenes_restaurante(request, restaurante_slug):
    """
    Lista las órdenes para un restaurante específico por slug,
    verificando que el usuario autenticado sea el propietario.
    """
    user = request.user # Obtener el usuario autenticado

    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    if restaurante.propietario != user:
        return Response({"error": "No tienes permiso para ver las órdenes de este restaurante."}, status=status.HTTP_403_FORBIDDEN)

    # 3. Si la verificación de permiso pasa, filtrar las órdenes para este restaurante.
    ordenes = Orden.objects.filter(restaurante=restaurante).order_by('-created_at')

    # 4. Serializar las órdenes
    serializer = OrdenSerializer(ordenes, many=True, context={'request': request})

    # 5. Devolver la respuesta
    return Response(serializer.data)   


@api_view(['PATCH']) # Usamos PATCH para actualizaciones parciales (solo un campo)
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# La función acepta el ID de la orden como parámetro
def actualizar_estado_orden(request, restaurante_slug, orden_id):
    """
    Actualiza el estado de una orden específica por ID,
    verificando que el usuario autenticado sea el propietario del restaurante asociado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Intentar encontrar la orden por el ID
    # get_object_or_404 devolverá 404 si la orden no existe.
    orden = get_object_or_404(Orden, id=orden_id)

    # 2. **Verificación de Permiso Crucial:** Asegurarse de que el usuario autenticado
    # es el propietario del restaurante asociado a esta orden.
    # Accedemos a la instancia del restaurante a través de la orden
    restaurante_orden = orden.restaurante

    # Comparamos el propietario del restaurante con el usuario autenticado
    if restaurante_orden.propietario != user:
        # Si el usuario NO es el propietario del restaurante de esta orden, denegar el acceso.
        return Response(
            {"detail": "No tienes permiso para actualizar el estado de esta orden."},
            status=status.HTTP_403_FORBIDDEN # 403 Forbidden
        )

    # 3. Si la verificación de permiso pasa, proceder a actualizar el estado.
    # Usamos el OrdenEstadoUpdateSerializer.
    # partial=True permite enviar solo el campo 'estado' en el cuerpo de la petición.
    serializer = OrdenEstadoUpdateSerializer(orden, data=request.data, partial=True)

    # 4. Validar los datos (solo el estado)
    if serializer.is_valid():
        # Guardar la instancia con el estado actualizado
        serializer.save()

        # 5. Opcional: Serializar la orden COMPLETA para devolver la respuesta
        # Usamos el OrdenSerializer completo para incluir todos los detalles anidados
        # en la respuesta, como en la vista de detalle GET.
        full_serializer = OrdenSerializer(orden, context={'request': request}) # Pasa el contexto si es necesario en el serializador
        return Response(full_serializer.data)

        # Si solo quisieras confirmar el estado actualizado:
        # return Response({'status': 'success', 'orden_id': orden.id, 'new_estado': orden.estado})


    # 6. Si los datos no son válidos (ej: el valor de estado no es una opción válida en el modelo)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST']) # Permite GET para listar, POST para crear
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante como parámetro de la URL
def categoria_list_create_restaurante(request, restaurante_slug):
    """
    Lista categorías para un restaurante específico por slug (GET)
    o crea una nueva categoría para ese restaurante (POST).
    Verifica que el usuario autenticado sea el propietario.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad: Si el propietario del restaurante no es el usuario autenticado...
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Si la verificación de permiso pasa...
    if request.method == 'GET':
        print("usuario autenticado:", user) # Verifica el usuario autenticado
        print("restaurante encontrado:", restaurante) # Verifica el restaurante encontrado
        # 2. Si es GET: Listar todas las categorías de ESTE restaurante
        # Filtramos las categorías por el restaurante encontrado
        categorias = Categoria.objects.filter(restaurante=restaurante).order_by('orden', 'nombre')
        # Serializar la lista de categorías
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 2. Si es POST: Crear una nueva categoría
        # El serializador valida los datos recibidos (nombre, descripcion, orden, activo).
        # NO se espera el campo 'restaurante' en los datos de entrada porque es read_only en el serializador.
        serializer = CategoriaSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la nueva instancia de Categoría.
            # **Inyectamos manualmente el restaurante** encontrado y verificado,
            # asociando la nueva categoría a este restaurante.
            # El slug se autogenerará automáticamente en el método save del modelo Categoria.
            categoria_creada = serializer.save(restaurante=restaurante)

            # Serializar la categoría creada para la respuesta
            # Usamos el mismo CategoriaSerializer para mostrar la categoría recién creada.
            return Response(CategoriaSerializer(categoria_creada).data, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE']) # Permite GET, PUT, PATCH, DELETE
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante y el ID de la categoría como parámetros
def categoria_detail_update_delete_restaurante(request, restaurante_slug, categoria_id):
    """
    Recupera (GET), actualiza (PUT/PATCH) o elimina (DELETE) una categoría específica por ID,
    verificando que pertenezca al restaurante del usuario autenticado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar la propiedad.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar la categoría por su ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    # get_object_or_404 buscará la categoría por ID y añadirá el filtro por restaurante.
    # Esto asegura que un propietario no pueda acceder a categorías de otros restaurantes
    # incluso si conoce el ID de la categoría.
    categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)


    # Si la verificación de permiso y la pertenencia de la categoría pasan...
    if request.method == 'GET':
        # 3. Si es GET: Recuperar los detalles de la categoría
        serializer = CategoriaSerializer(categoria)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # 3. Si es PUT o PATCH: Actualizar la categoría
        # partial=True permite actualizaciones parciales (solo enviar los campos a modificar, útil para PATCH).
        partial = request.method == 'PATCH'
        # Inicializa el serializador con la instancia existente y los datos de la petición.
        serializer = CategoriaSerializer(categoria, data=request.data, partial=partial)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la categoría actualizada. Como ya pasamos la instancia, save() llama a update().
            # No necesitamos pasar 'restaurante' aquí de nuevo porque ya está asociado a la instancia.
            serializer.save()
            # Devolver la categoría actualizada serializada
            return Response(serializer.data)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 3. Si es DELETE: Eliminar la categoría
        # Elimina la instancia de la categoría encontrada
        categoria.delete()
        # Devolver una respuesta de éxito sin contenido
        return Response(status=status.HTTP_204_NO_CONTENT)




@api_view(['GET', 'POST']) # Permite GET para listar, POST para crear
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante y el ID de la categoría como parámetros de la URL
def producto_list_create_restaurante_categoria(request, restaurante_slug, categoria_id):
    """
    Lista productos para una categoría específica dentro de un restaurante (GET)
    o crea un nuevo producto para esa categoría (POST).
    Verifica que el usuario autenticado sea el propietario y que la categoría
    pertenezca a ese restaurante.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar la categoría por ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    # get_object_or_404 buscará la categoría por ID y añadirá el filtro por restaurante.
    # Esto asegura que un propietario no pueda gestionar productos en una categoría que no es suya.
    categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)


    # Si la verificación de permiso y la pertenencia de la categoría pasan...
    if request.method == 'GET':
        # 3. Si es GET: Listar productos de esta categoría.
        # Filtramos los productos que pertenecen a ESTA categoría específica.
        productos = Producto.objects.filter(categoria=categoria).order_by('orden', 'nombre')
        # Serializar la lista de productos.
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        # 3. Si es POST: Crear un nuevo producto para esta categoría y restaurante.
        # El serializador valida los datos recibidos (nombre, precio, cantidad, etc.).
        # El campo 'categoria' en los datos de entrada (JSON) debe contener el ID de la categoría.
        # El campo 'restaurante' y 'slug' en el serializador son read_only y NO deben enviarse.
        serializer = ProductoSerializer(data=request.data)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda la nueva instancia de Producto.
            # **Inyectamos manualmente la categoría** encontrada y verificada,
            # **e inyectamos manualmente el restaurante** encontrado y verificado.
            # Esto asegura que el nuevo producto quede correctamente asociado
            # a la categoría y al restaurante correctos.
            # El slug del producto se autogenerará automáticamente en el método save del modelo Producto.
            producto_creado = serializer.save(categoria=categoria, restaurante=restaurante)

            # Serializar el producto creado para la respuesta.
            # Usamos el mismo ProductoSerializer para mostrar el producto recién creado.
            return Response(ProductoSerializer(producto_creado).data, status=status.HTTP_201_CREATED)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE']) # Permite GET, PUT, PATCH, DELETE
@permission_classes([IsAuthenticated]) # Requiere que el usuario esté autenticado
# Acepta el slug del restaurante, el ID de la categoría y el ID del producto como parámetros
def producto_detail_update_delete_restaurante_categoria(request, restaurante_slug, categoria_id, producto_id):
    """
    Recupera (GET), actualiza (PUT/PATCH) o elimina (DELETE) un producto específico por ID,
    verificando que pertenezca a la categoría y restaurante del usuario autenticado.
    """
    user = request.user # Obtener el usuario autenticado

    # 1. Encontrar el restaurante por slug y verificar la propiedad.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        return Response(
            {"detail": "No tienes permiso para gestionar este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 2. Encontrar la categoría por ID **Y** asegurarse de que pertenezca a ESTE restaurante.
    categoria = get_object_or_404(Categoria, id=categoria_id, restaurante=restaurante)

    # 3. Encontrar el producto por su ID **Y** asegurarse de que pertenezca a ESTA categoría y ESTE restaurante.
    # get_object_or_404 buscará el producto por ID y añadirá los filtros por categoria y restaurante.
    # Esta es una verificación de seguridad crucial.
    producto = get_object_or_404(Producto, id=producto_id, categoria=categoria, restaurante=restaurante)


    # Si todas las verificaciones de permiso y pertenencia pasan...
    if request.method == 'GET':
        # 4. Si es GET: Recuperar los detalles del producto
        serializer = ProductoSerializer(producto)
        return Response(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        # 4. Si es PUT o PATCH: Actualizar el producto.
        # partial=True permite actualizaciones parciales (útil para PATCH).
        partial = request.method == 'PATCH'
        # Inicializa el serializador con la instancia existente 'producto' y los datos de la petición.
        # El campo 'categoria' en los datos de entrada (si se envía) debe ser el ID de la categoría actual.
        # El campo 'restaurante' y 'slug' no deben enviarse (son read_only).
        serializer = ProductoSerializer(producto, data=request.data, partial=partial)

        # Validar los datos recibidos
        if serializer.is_valid():
            # Guarda el producto actualizado. Como ya pasamos la instancia, save() llama a update().
            # No necesitamos pasar 'categoria' ni 'restaurante' aquí de nuevo porque ya están asociados a la instancia.
            serializer.save()
            # Devolver el producto actualizado serializado.
            return Response(serializer.data)

        # Si los datos no son válidos, devolver errores 400
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # 4. Si es DELETE: Eliminar el producto.
        # Elimina la instancia del producto encontrada.
        producto.delete()
        # Devolver una respuesta de éxito sin contenido.
        return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def restaurante_dashboard_summary(request, restaurante_slug):
    """
    Proporciona un resumen de datos para el panel de control de un restaurante específico.
    Incluye conteos de órdenes por estado, ventas del día y órdenes recientes.
    Verifica que el usuario autenticado sea el propietario del restaurante.
    """
    user = request.user 

    # 1. Encontrar el restaurante por slug y verificar que el usuario sea el propietario.
    # get_object_or_404 devolverá 404 si el restaurante no existe.
    restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)

    # Verificar la propiedad
    if restaurante.propietario != user:
        # Denegar el acceso con 403 Forbidden
        return Response(
            {"detail": "No tienes permiso para ver el resumen de este restaurante."},
            status=status.HTTP_403_FORBIDDEN
        )

    # Si la verificación de permiso pasa...

    # Obtener el inicio y fin del día actual (considerando zona horaria si es relevante)
    # Para simplicidad, usaremos la hora del servidor. Puedes ajustar esto si necesitas manejar zonas horarias específicas.
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)


    # 2. Calcular los datos de resumen para ESTE restaurante

    # Conteo de Órdenes por Estado
    ordenes_pendientes_count = Orden.objects.filter(
        restaurante=restaurante, # Filtrar por el restaurante del propietario
        estado='pendiente'      # Filtrar por estado 'pendiente'
    ).count() # Contar los resultados

    ordenes_en_proceso_count = Orden.objects.filter(
        restaurante=restaurante,
        estado='en_proceso' # O el valor que uses para 'en proceso'
    ).count()

     # Puedes añadir más estados relevantes para el panel, como 'en_camino', 'lista_para_recoger', etc.
    ordenes_en_camino_count = Orden.objects.filter(
        restaurante=restaurante,
        estado='en_camino'
    ).count()


    # Ventas Totales del Día (solo órdenes completadas/entregadas)
    # Filtramos por restaurante, estado 'entregada' y fecha de creación 'hoy'.
    # Usamos .aggregate(Sum('total')) para sumar el campo 'total'.
    # Usamos or 0 para que si no hay ventas hoy, el resultado sea 0 en lugar de None.
    ventas_hoy_total = Orden.objects.filter(
        restaurante=restaurante,         # Filtrar por restaurante
        estado='entregada',              # Solo contar órdenes entregadas como ventas
        created_at__gte=today_start,     # Creadas desde el inicio de hoy
        created_at__lt=today_end         # Creadas hasta el final de hoy
    ).aggregate(Sum('total'))['total__sum'] or 0


    # Órdenes Recientes (ej: las últimas 5 órdenes, excluyendo las entregadas o canceladas si prefieres)
    # Filtramos por restaurante y ordenamos por fecha de creación descendente.
    # Limitamos a las primeras 5 con [:5].
    ordenes_recientes = Orden.objects.filter(
        restaurante=restaurante
        # Opcional: .exclude(estado__in=['entregada', 'cancelada']) si solo quieres las activas
    ).order_by('-created_at')[:5] # Obtener las últimas 5 órdenes


    # Serializar las órdenes recientes. Usaremos el OrdenSerializer completo.
    # many=True porque es una lista de órdenes. Pasa el contexto si tu serializador lo necesita.
    ordenes_recientes_serializer = OrdenSerializer(ordenes_recientes, many=True, context={'request': request})


    # 3. Estructurar los datos de resumen en un diccionario
    summary_data = {
        "ordenes": {
            "pendiente": ordenes_pendientes_count,
            "en_proceso": ordenes_en_proceso_count,
            "en_camino": ordenes_en_camino_count,
            # Puedes añadir más estados aquí si los calculaste
        },
        "ventas": {
            "hoy": ventas_hoy_total,
            # Podrías añadir ventas de la semana, mes, etc. haciendo ajustes en el filtro de fecha
        },
        "ordenes_recientes": ordenes_recientes_serializer.data, # Incluye la lista serializada de órdenes recientes
        # Puedes añadir más datos aquí, ej: "productos_mas_vendidos" (requiere agregaciones más complejas)
    }


    # 4. Devolver los datos de resumen como una respuesta JSON
    return Response(summary_data)