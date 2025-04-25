# API de Restaurantes

API REST desarrollada con Django y Django REST Framework para gestionar restaurantes y sus métodos de envío.

## Características

- Gestión de restaurantes
- Gestión de métodos de envío por restaurante
- API RESTful completa
- Documentación automática de la API

## Requisitos

- Python 3.x
- Django 5.2
- Django REST Framework 3.16.0

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecutar migraciones:
   ```bash
   python manage.py migrate
   ```
5. Iniciar el servidor:
   ```bash
   python manage.py runserver
   ```

## Endpoints

### Restaurantes
- `GET /api/restaurantes/` - Listar todos los restaurantes
- `POST /api/restaurantes/` - Crear un nuevo restaurante
- `GET /api/restaurantes/{id}/` - Obtener detalles de un restaurante
- `PUT /api/restaurantes/{id}/` - Actualizar un restaurante
- `DELETE /api/restaurantes/{id}/` - Eliminar un restaurante

### Envíos
- `GET /api/envios/` - Listar todos los métodos de envío
- `POST /api/envios/` - Crear un nuevo método de envío
- `GET /api/envios/{id}/` - Obtener detalles de un método de envío
- `PUT /api/envios/{id}/` - Actualizar un método de envío
- `DELETE /api/envios/{id}/` - Eliminar un método de envío 