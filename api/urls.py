from django.urls import path
from . import views

urlpatterns = [
    path('redes-sociales/', views.red_social_list_create, name='red_social_list_create'),
    path('redes-sociales/<int:pk>/', views.red_social_detail, name='red_social_detail'),

    path('metodos-pago/', views.metodo_pago_list_create, name='metodo_pago_list_create'),
    path('metodos-pago/<int:pk>/', views.metodo_pago_detail, name='metodo_pago_detail'),

    path('restaurantes/', views.restaurante_list_create, name='restaurante_list_create'),
    path('restaurantes/<slug:slug>/', views.restaurante_detail, name='restaurante_detail'),
    path('restaurantes/<int:pk>', views.restaurante_detail_id , name='restaurante_detail_by_pk'),
    path('restaurantes/<slug:restaurante_slug>/productos/', views.producto_list_by_restaurante_slug, name='productos_por_restaurante'),

    path('envios/', views.envio_list_create, name='envio_list_create'),
    path('envios/<int:pk>/', views.envio_detail, name='envio_detail'),

    #ordenes
    path('ordenes/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),
    
]



