# 🔒 Guía de Seguridad - AWS Control Panel

## ⚠️ Información Sensible

Este proyecto maneja información sensible que **NUNCA** debe ser expuesta:

1. **Credenciales AWS** (Access Key, Secret Key, Session Token)
2. **API Keys de IA** (Gemini, DeepSeek)
3. **SECRET_KEY de Flask**

## 🛡️ Medidas de Seguridad Implementadas

### 1. Protección de API Keys en el Frontend

- ✅ Las API keys **NO** se envían al navegador con el atributo `value`
- ✅ Solo se muestra un placeholder `••••••••••••••••` si la key existe
- ✅ Los campos son de tipo `password` y tienen `autocomplete="off"`
- ✅ Las keys solo se actualizan si el usuario proporciona una nueva

### 2. Protección en el Backend

- ✅ Las API keys se almacenan **solo en sesión** o variables de entorno
- ✅ Las sesiones están configuradas con:
  - `SESSION_COOKIE_HTTPONLY=True`: No accesible desde JavaScript
  - `SESSION_COOKIE_SECURE=True`: Solo se transmite por HTTPS (producción)
  - `SESSION_COOKIE_SAMESITE=Lax`: Protección contra CSRF
  - Tiempo de expiración: 1 hora

### 3. Variables de Entorno

- ✅ El archivo `.env` está en `.gitignore` (nunca se sube a Git)
- ✅ Se proporciona `.env.example` sin valores reales
- ✅ Las credenciales AWS se leen de variables de entorno

### 4. Código Fuente

- ✅ Ninguna API key está hardcodeada en el código
- ✅ Los logs **NO** muestran las keys completas (solo primeros 10 caracteres)

## 🚨 Buenas Prácticas

### Para Desarrollo Local

1. **Genera una SECRET_KEY segura**:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   
2. **Copia y configura .env**:
   ```bash
   cp .env.example .env
   # Edita .env con tus credenciales reales
   ```

3. **NUNCA** hagas commit del archivo `.env`:
   ```bash
   # Verifica que .env esté ignorado
   git check-ignore .env
   ```

### Para Coolify/Producción

1. **Define las variables de entorno en Coolify**:
   - No uses el archivo `.env` en producción
   - Configura todas las variables en la interfaz de Coolify
   
2. **Usa HTTPS obligatorio**:
   - Coolify proporciona SSL automático
   - Las cookies de sesión solo se transmiten por HTTPS

3. **Configura las API keys desde el formulario web**:
   - Ve a `/configuracion/ai-provider`
   - Introduce las API keys (se guardan en sesión cifrada)
   - Ventaja: No quedan en variables de entorno persistentes

### Para Usuarios del Panel

1. **Acceso con credenciales AWS temporales**:
   - Usa AWS Academy Learner Lab (credenciales temporales de 4 horas)
   - O crea un usuario IAM con permisos mínimos necesarios

2. **Protege tu SECRET_KEY**:
   - Usa una clave de 64+ caracteres aleatorios
   - Cámbiala regularmente en producción

3. **No compartas tu sesión**:
   - Cierra sesión al terminar
   - No uses el panel en computadoras públicas

## 🔍 Verificación de Seguridad

### Checklist antes de desplegar

- [ ] `.env` no está en el repositorio
- [ ] `.gitignore` incluye `.env`
- [ ] `SECRET_KEY` es una cadena aleatoria de 64+ caracteres
- [ ] No hay API keys hardcodeadas en el código
- [ ] HTTPS está habilitado en producción
- [ ] Las variables de entorno están configuradas en Coolify

### Cómo verificar que las keys NO son visibles

1. **Inspecciona el HTML**:
   - Abre DevTools (F12) → Elements
   - Busca los inputs de API key
   - ✅ NO debe aparecer `value="sk-..."` ni `value="AIza..."`

2. **Revisa Network requests**:
   - DevTools → Network → Filtrar por "ai-provider"
   - ✅ Las keys deben aparecer solo en el payload POST cuando se actualizan
   - ✅ En GET, las keys NO deben aparecer

3. **Revisa la respuesta del servidor**:
   ```bash
   curl http://localhost:5041/configuracion/ai-provider
   ```
   - ✅ El HTML NO debe contener las API keys reales

## 🚨 Qué hacer si una key fue expuesta

1. **Revoca inmediatamente la API key**:
   - Gemini: https://aistudio.google.com/app/apikey
   - DeepSeek: https://platform.deepseek.com/
   
2. **Genera una nueva key**

3. **Actualiza la configuración**:
   - En Coolify: actualiza la variable de entorno
   - O usa el formulario web para actualizar

4. **Si fue commiteada a Git**:
   ```bash
   # Elimina de historial (requiere force push)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

## 📚 Recursos Adicionales

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

---

**Última actualización**: 15 de diciembre de 2025
