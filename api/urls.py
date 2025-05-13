from django.urls import path
from . import views

urlpatterns = [

    #redes sociales
    path('restaurantes/<slug:restaurante_slug>/redes-sociales/', views.redsocial_list_create_restaurante, name='redsocial_list_create_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/redes-sociales/<int:red_social_id>/', views.redsocial_detail_update_delete_restaurante, name='redsocial_detail_update_delete_restaurante'),

    #metodos de pago
    path('restaurantes/<slug:restaurante_slug>/metodos-pago/', views.metodopago_list_create_restaurante, name='metodopago_list_create_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/metodos-pago/<int:metodo_pago_id>/', views.metodopago_detail_update_delete_restaurante, name='metodopago_detail_update_delete_restaurante'),

    #envios
    path('restaurantes/<slug:restaurante_slug>/envios/', views.envio_list_create_restaurante, name='envio_list_create_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/envios/<int:envio_id>/', views.envio_detail_update_delete_restaurante, name='envio_detail_update_delete_restaurante'),

    #restaurantes
    path('mis-restaurantes/', views.listar_mis_restaurantes, name='listar_mis_restaurantes'),
    path('restaurantes/', views.restaurante_list_create, name='restaurante_list_create'),
    path('restaurantes/<slug:slug>/', views.restaurante_detail, name='restaurante_detail'),
    path('restaurantes/<int:pk>', views.restaurante_detail_id , name='restaurante_detail_by_pk'),
    path('restaurantes/<slug:restaurante_slug>/productos/', views.producto_list_by_restaurante_slug, name='productos_por_restaurante'),


    #ordenes
    path('restaurantes/<slug:restaurante_slug>/ordenes/', views.listar_ordenes_restaurante, name='listar_ordenes_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/ordenes/<int:orden_id>/', views.orden_detail_restaurante, name='orden_detail_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/ordenes/<int:orden_id>/estado/', views.actualizar_estado_orden, name='actualizar_estado_orden'),

    ## categorias
    path('restaurantes/<slug:restaurante_slug>/categorias/', views.categoria_list_create_restaurante, name='categoria_list_create_restaurante'),
    path('restaurantes/<slug:restaurante_slug>/categorias/<int:categoria_id>/', views.categoria_detail_update_delete_restaurante, name='categoria_detail_update_delete_restaurante'),

    #productos
    path('restaurantes/<slug:restaurante_slug>/categorias/<int:categoria_id>/productos/', views.producto_list_create_restaurante_categoria, name='producto_list_create_restaurante_categoria'),
    path('restaurantes/<slug:restaurante_slug>/categorias/<int:categoria_id>/productos/<int:producto_id>/', views.producto_detail_update_delete_restaurante_categoria, name='producto_detail_update_delete_restaurante_categoria'),

    #menu dashboard
    path('restaurantes/<slug:restaurante_slug>/menu/', views.restaurant_menu_list_view, name='restaurant_menu_list'),
    path('restaurantes/<slug:restaurante_slug>/menu/<int:product_id>/', views.product_detail_view, name='product_detail'),

    #ordenes
    path('ordenes/', views.crear_orden, name='crear_orden'),
    path('ordenes/<int:pk>/', views.orden_detail, name='orden_detail'),




    #dashboard
    path('restaurantes/<slug:restaurante_slug>/dashboard/summary/', views.restaurante_dashboard_summary, name='restaurante_dashboard_summary'),

    
]



