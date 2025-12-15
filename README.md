# AWS Control Panel

Panel de control web completo para gestionar servicios de AWS con integración de IA Assistant.

## 🔒 Seguridad

> **⚠️ IMPORTANTE**: Este proyecto maneja credenciales sensibles (AWS, API keys de IA).
> 
> - **NUNCA** subas tu archivo `.env` a repositorios públicos
> - Usa HTTPS en producción
> - Configura las API keys desde la interfaz web en lugar de variables de entorno

## 🚀 Características

- **Gestión Completa de AWS**: Administra EC2, S3, Lambda, RDS, DynamoDB, VPC y más de 30 servicios
- **AI Assistant Inteligente**: Integración con Google Gemini y DeepSeek para asistencia en tareas
- **Servicios de ML/AI**: Amazon Polly (texto a voz), Bedrock, Rekognition
- **Interfaz Intuitiva**: Dashboard moderno con Bootstrap 5
- **MCP Server**: Arquitectura de herramientas para automatización

## 📋 Requisitos

- Python 3.10+
- Credenciales de AWS configuradas
- API Key de Google Gemini o DeepSeek (opcional, para AI Assistant)

## 🔧 Instalación

### Opción 1: Instalación Local

1. Clonar el repositorio:
```bash
git clone https://github.com/Zurichk/Aws-Control.git
cd Aws-Control
```

2. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: .\Scripts\Activate.ps1
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Iniciar la aplicación:
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5041`

### Opción 2: Docker (Recomendado para Producción)

#### Con Docker Compose:
```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Construir y ejecutar
docker-compose up --build

# 3. Acceder a la aplicación
http://localhost:5041
```

#### Con Docker CLI:
```bash
# 1. Construir la imagen
docker build -t aws-control-panel .

# 2. Ejecutar el contenedor
docker run -d \
  --name aws-control \
  -p 5041:5041 \
  --env-file .env \
  aws-control-panel

# 3. Ver logs
docker logs -f aws-control
```

**Ventajas del despliegue con Docker:**
- ✅ Entorno consistente entre desarrollo y producción
- ✅ Aislamiento de dependencias
- ✅ Health checks integrados
- ✅ Fácil escalabilidad
- ✅ Despliegue en cualquier plataforma (VPS, Cloud, Coolify)

## ⚙️ Configuración

### Credenciales AWS
Puedes configurar las credenciales AWS de dos formas:
1. A través de la interfaz web en `/configuracion/aws-credentials`
2. En el archivo `.env`:
```env
AWS_ACCESS_KEY_ID=tu_access_key
AWS_SECRET_ACCESS_KEY=tu_secret_key
AWS_DEFAULT_REGION=us-east-1
```

### Proveedor de IA (Opcional)
Para usar el AI Assistant, configura una de estas APIs:
```env
AI_PROVIDER=gemini  # o deepseek
GEMINI_API_KEY=tu_api_key_gemini
DEEPSEEK_API_KEY=tu_api_key_deepseek
```

## 🐳 Despliegue en Producción

### Coolify (Recomendado)
El proyecto incluye configuración completa para despliegue con **Dockerfile** en Coolify:

- **Guía completa**: [app/docs/DEPLOY_COOLIFY.md](app/docs/DEPLOY_COOLIFY.md)
- **Método**: Dockerfile (Build Pack automático)
- **Características**:
  - Health checks integrados
  - Usuario no-root (seguridad)
  - Optimización de capas de Docker
  - Variables de entorno configurables
  - HTTPS automático con certificado SSL

### Otros Servicios Cloud
El Dockerfile también funciona en:
- **Railway**: Push to deploy
- **Render**: Dockerfile automático
- **Fly.io**: `fly launch` detecta el Dockerfile
- **Google Cloud Run**: `gcloud run deploy`
- **AWS ECS/Fargate**: Usa el Dockerfile para crear task definitions

Para instrucciones específicas de cada plataforma, consulta la [documentación de Docker](https://docs.docker.com/).

## 📚 Servicios Soportados

### Cómputo
- EC2, Lambda, Batch, ECS, EKS

### Almacenamiento
- S3, EBS, EFS, FSx

### Bases de Datos
- RDS, DynamoDB, Neptune, DocumentDB, ElastiCache

### Redes
- VPC, Route 53, CloudFront, ELB, API Gateway

### Seguridad
- IAM, KMS, ACM, Secrets Manager, Security Groups

### ML/AI
- SageMaker, Bedrock, Rekognition, Polly

### Analytics
- Athena, Glue, EMR, Kinesis

### Gestión
- CloudFormation, CloudWatch, Auto Scaling, Systems Manager, CloudTrail, Cost Explorer

## 🤖 AI Assistant

El AI Assistant puede ejecutar operaciones reales en AWS usando más de 30 herramientas:
- Crear y gestionar instancias EC2
- Configurar VPCs y redes
- Administrar buckets S3
- Crear funciones Lambda
- Y mucho más...

Selecciona tu proveedor preferido en **Configuración → Proveedor de IA**

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**Zurichk**
- GitHub: [@Zurichk](https://github.com/Zurichk)

## 🙏 Agradecimientos

- AWS por sus servicios en la nube
- Google Gemini y DeepSeek por sus APIs de IA
- La comunidad de Flask y Python
