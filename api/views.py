from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Restaurante, Envio, RedSocial, MetodoPago, Producto, Orden
from .serializers import (
    RestauranteSerializer, EnvioSerializer, RedSocialSerializer,
    MetodoPagoSerializer, ProductoSerializer, OrdenSerializer
)

# Create your views here.

@api_view(['GET', 'POST'])
def red_social_list_create(request):
    if request.method == 'GET':
        redes_sociales = RedSocial.objects.all()
        serializer = RedSocialSerializer(redes_sociales, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = RedSocialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def red_social_detail(request, pk):
    try:
        red_social = RedSocial.objects.get(pk=pk)
    except RedSocial.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RedSocialSerializer(red_social)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = RedSocialSerializer(red_social, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        red_social.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
def metodo_pago_list_create(request):
    if request.method == 'GET':
        metodos_pago = MetodoPago.objects.all()
        serializer = MetodoPagoSerializer(metodos_pago, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = MetodoPagoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
def metodo_pago_detail(request, pk):
    try:
        metodo_pago = MetodoPago.objects.get(pk=pk)
    except MetodoPago.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MetodoPagoSerializer(metodo_pago)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = MetodoPagoSerializer(metodo_pago, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        metodo_pago.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def producto_list_by_restaurante_slug(request, restaurante_slug):
    """
    Devuelve todos los productos del restaurante especificado por el slug en la URL.
    """
    try:
        restaurante = get_object_or_404(Restaurante, slug=restaurante_slug)
        productos = Producto.objects.filter(restaurante=restaurante)
        serializer = ProductoSerializer(productos, many=True)
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
    