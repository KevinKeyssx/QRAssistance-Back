# QRAssistance Backend

Backend para gestionar asistencias y formularios dinámicos utilizando FastAPI y MongoDB.

## 🚀 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:
- [ Docker ]( https://www.docker.com/ ) y Docker Compose
- [ Python 3.8+ ]( https://www.python.org/ )

## 📂 Estructura del Proyecto

El proyecto está organizado en los siguientes directorios principales:
- `entities/`: Modelos de MongoDB ( por ejemplo, `Member`, `Assistance`, `QR` ).
- `routers/`: Controladores y rutas de la API de FastAPI.
- `services/`: Lógica de base de datos e interacción entre los datos.

## ⚙️ Configuración

1. Abre una terminal y navega hasta la raíz del proyecto.
2. Crea un archivo `.env` en el directorio raíz asegurándote de definir las siguientes variables:

```env
MONGO_USERNAME   = mongo
MONGO_PASSWORD   = password_seguro
MONGO_DATABASE   = qrassistance
MONGONAME        = qrassistance
MONGO_LOCAL_URL  = mongodb://mongo:password_seguro@localhost:27017/qrassistance?authSource=qrassistance
# MONGO_PUBLIC_URL = opcional_url_de_produccion
```

## 🐳 Base de Datos con Docker

El proyecto utiliza Docker Compose para levantar una instancia local de MongoDB de manera rápida. Para iniciar la base de datos, ejecuta el siguiente comando:

```bash
docker-compose up -d
```

Este comando levantará el contenedor `qrassistance-mongo` de la imagen de `mongo:6`, usando las credenciales mapeadas por tu `.env`, y exponiéndolo en el puerto local `27017`. Puedes consultar los logs corriendo `docker-compose logs -f`.

## 💻 Instalación y Ejecución de la API

1. **Crear y activar un entorno virtual ( Recomendado ):**
```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux / macOS:
source venv/bin/activate
```

2. **Instalar dependencias:**
El proyecto incluye un script de dependencias básicas. Para instalarlas ejecuta:
```bash
pip install -r requirements.txt
```

3. **Ejecutar el servidor localmente:**
Una vez instaladas las dependencias y con el contenedor de MongoDB en ejecución, inicia la aplicación de FastAPI:
```bash
uvicorn main:app --reload
```

El servidor estará escuchando en `http://localhost:8000`.

## 📚 Documentación de la API

FastAPI genera documentación automática de manera nativa. 
Una vez iniciada la aplicación, dirígete a tu navegador web favorito:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
