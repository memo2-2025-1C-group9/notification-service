# Notification service

## Tabla de Contenido
1. Introduccion
2. Requisitos Previos
3. Requisitos
4. Instalacion
5. Run
6. FastAPI Links
7. Pytest Links

## Introduccion
Bienvenido a ClassConnect!

En nuestra plataforma de aprendizaje de la proxima generacion
podras crear, editar y eliminar tus cursos como mejor te parezca.
Cada curso tendra titulo y descripcion y podras consultarlos cuando gustes!

## Instalacion
1. Clonar el Repo:
```sh
git clone https://github.com/memo2-2025-1C-group9/notification-service.git
cd  notification-service
```

2. Crear el env development a partir del example:
```sh
cp .env.example .env.development
```

## Run
```sh
docker-compose --profile app up --build
```


## Documentación de Endpoints

### Gestión de Preferencias de Usuario

```
GET /me/preferences
```
Obtiene las preferencias de notificación del usuario autenticado.

**Autenticación**: Requiere JWT token del usuario en header como **bearer token**

**Respuesta**: 
```json
{
    "id": 1,
    "examen_email": bool,
    "examen_push": bool,
    "tarea_email": bool,
    "tarea_push": bool
}
```

#### PUT /me/editpreferences
Actualiza las preferencias de notificación del usuario.

**Autenticación**: Requiere JWT token del usuario en header como **bearer token**

**Body**:
```json
{
    "examen_email": bool,
    "examen_push": bool,
    "tarea_email": bool,
    "tarea_push": bool
}
```

### Notificaciones

#### POST /notify/user
Crea una notificación para un usuario específico.

**Autenticación**: Requiere JWT token del **servicio** en header como **bearer token**

**Body**:
```json
{
    "id_user": 1,
    "notification_type": "Tarea",
    "event": "Entregado",
    "data": {
        "titulo": "Tarea 1",
        "descripcion": "Descripción de la tarea",
        "fecha": "2024-03-20",
        "instrucciones": "Instrucciones de la tarea",
        "nota": 9.5,
        "feedback": "Excelente trabajo"
    }
}
```

#### POST /notify/course
Crea una notificación para todos los usuarios de un curso.

**Autenticación**: Requiere JWT token del **servicio** en header como **bearer token**

**Body**:
```json
{
    "id_course": "curso-123",
    "notification_type": "Tarea",
    "event": "Nuevo",
    "data": {
        "titulo": "Tarea 1",
        "descripcion": "Descripción de la tarea",
        "fecha": "2024-03-20",
        "instrucciones": "Instrucciones de la tarea"
    }
}
```

## Despliegue en Render

Este proyecto está configurado para desplegar automáticamente en Render como un servicio web a través de GitHub Actions.


### Configuración de GitHub Secrets

Añade los siguientes secretos en tu repositorio de GitHub:

1. Ve a tu repositorio -> Settings -> Secrets and variables -> Actions
2. Añade los siguientes secretos:
   - `RENDER_API_KEY`: Tu API key de Render
   - `RENDER_SERVICE_ID`: El ID de tu servicio web en Render
   - Adicionalmente, añade cualquier otra variable de entorno que necesite tu aplicación:
     - `ENVIRONMENT`: Por ejemplo, "production"
     - `PORT`: Render asigna este valor automáticamente, así que no es necesario configurarlo.

### Funcionamiento

Cuando se hace push a la rama main, el flujo de trabajo de CI/CD:

1. Ejecuta linting y tests
2. Despliega la aplicación en Render
3. Copia las variables de entorno desde los secretos de GitHub a la configuración de Render

