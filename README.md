# WaveStudio Backend

Backend API para WaveStudio, desarrollado con FastAPI y PostgreSQL.

## Configuración de CI/CD con GitHub Actions y AWS

Este repositorio incluye un pipeline de CI/CD configurado con GitHub Actions para desplegar automáticamente la aplicación en AWS EC2 cuando se realiza un push a la rama principal.

### Requisitos previos

1. Una cuenta de AWS con acceso a:
   - EC2
   - ECR (Elastic Container Registry)
   - IAM (para crear credenciales)

2. Una instancia EC2 ejecutando Ubuntu

3. Un repositorio en GitHub

### Configuración de AWS

#### 1. Crear un repositorio ECR

1. Ve a la consola de AWS y navega a Amazon ECR
2. Haz clic en "Create repository"
3. Introduce un nombre para el repositorio (por ejemplo, "wavestudio-backend")
4. Haz clic en "Create repository"

#### 2. Crear un usuario IAM con permisos para ECR

1. Ve a la consola de AWS y navega a IAM
2. Haz clic en "Users" y luego en "Add user"
3. Introduce un nombre para el usuario (por ejemplo, "github-actions")
4. Selecciona "Programmatic access"
5. Haz clic en "Next: Permissions"
6. Haz clic en "Attach existing policies directly"
7. Busca y selecciona las siguientes políticas:
   - AmazonECR-FullAccess
   - AmazonEC2ContainerRegistryFullAccess
8. Haz clic en "Next: Tags", "Next: Review" y finalmente en "Create user"
9. **Importante**: Guarda el Access Key ID y Secret Access Key, los necesitarás más adelante

### Configuración de la instancia EC2

Puedes configurar tu instancia EC2 usando el script proporcionado:

```bash
# Primero, sube el script a tu instancia EC2 (desde tu máquina local)
scp scripts/setup-ec2.sh ubuntu@tu-instancia-ec2:~/

# Luego, conéctate a tu instancia EC2 y ejecuta el script
ssh ubuntu@tu-instancia-ec2
chmod +x setup-ec2.sh
./setup-ec2.sh
```

⚠️ **Importante**: El script `setup-ec2.sh` está diseñado para ejecutarse en una instancia EC2 con Ubuntu, no en tu máquina local macOS o Windows.

El script instalará:
- Docker y Docker Compose
- Nginx
- Certbot para SSL
- AWS CLI
- Configurará el firewall

### Configuración de GitHub Secrets

Puedes configurar los secrets de GitHub manualmente o usar el script proporcionado:

```bash
# Hacer el script ejecutable
chmod +x scripts/setup-github-secrets.sh

# Ejecutar el script
./scripts/setup-github-secrets.sh
```

El script te guiará para configurar los siguientes secrets en tu repositorio de GitHub:

1. `AWS_ACCESS_KEY_ID`: El Access Key ID del usuario IAM
2. `AWS_SECRET_ACCESS_KEY`: El Secret Access Key del usuario IAM
3. `AWS_REGION`: La región de AWS (por ejemplo, "us-east-1")
4. `ECR_REPOSITORY`: El nombre del repositorio ECR
5. `EC2_HOST`: La dirección IP pública o el nombre de dominio de tu instancia EC2
6. `EC2_USERNAME`: El nombre de usuario para SSH (normalmente "ubuntu")
7. `EC2_SSH_KEY`: La clave SSH privada para conectar a tu instancia EC2
8. `DB_HOST`: El host de la base de datos
9. `DB_NAME`: El nombre de la base de datos
10. `DB_USER`: El usuario de la base de datos
11. `DB_PASSWORD`: La contraseña de la base de datos
12. `SECRET_KEY`: La clave secreta para JWT
13. `MASTER_USERNAME`: El nombre de usuario del administrador
14. `MASTER_EMAIL`: El email del administrador
15. `MASTER_PASSWORD`: La contraseña del administrador

### Configuración de SSL con Let's Encrypt

Una vez que tu dominio esté apuntando a la IP de tu instancia EC2, puedes obtener un certificado SSL:

```bash
# En tu instancia EC2
~/get-ssl-cert.sh
```

### Cómo funciona el pipeline de CI/CD

1. Cuando haces push a la rama principal (main o master), se activa el workflow de GitHub Actions
2. El workflow ejecuta los tests
3. Si los tests pasan, construye una imagen Docker
4. La imagen se sube a Amazon ECR
5. La imagen se despliega en tu instancia EC2 usando Docker Compose

## Diagnóstico y solución de problemas

### Scripts de diagnóstico

Este repositorio incluye varios scripts para diagnosticar problemas con el endpoint de login:

#### Para macOS

```bash
# Hacer el script ejecutable
chmod +x scripts/diagnose_macos.sh

# Ejecutar el script
./scripts/diagnose_macos.sh
```

Este script está diseñado específicamente para macOS y te guiará a través de varias pruebas para diagnosticar el problema del error 500 en el endpoint de login.

#### Para Linux/Ubuntu

```bash
# Hacer el script ejecutable
chmod +x scripts/diagnose_all.sh

# Ejecutar el script
./scripts/diagnose_all.sh
```

### Scripts individuales

También puedes ejecutar los scripts de diagnóstico individualmente:

```bash
# Probar el endpoint de login
./scripts/test_login.py --url https://wavestudio-backend.com/api/auth/login --verbose

# Probar la conexión a la base de datos
./scripts/test_db_connection.py --verbose

# Probar la generación de tokens JWT
./scripts/test_jwt.py --verbose

# Probar la configuración CORS
./scripts/test_cors.py --url https://wavestudio-backend.com/api/auth/login --verbose
```

### Solución de problemas comunes

#### Error 500 en el endpoint de login

Las causas más comunes del error 500 en el endpoint de login son:

1. **Problema de conexión a la base de datos**:
   - Verifica que la URL de conexión en `.env` sea correcta
   - Asegúrate de que la base de datos esté accesible desde la instancia EC2
   - Comprueba que las credenciales de la base de datos sean correctas

2. **Configuración CORS incorrecta**:
   - Si estás usando credenciales en la solicitud fetch, asegúrate de que:
     - `allow_origins` no incluya el comodín "*"
     - `allow_credentials` esté configurado como `True`
     - El origen exacto esté incluido en `allow_origins`

3. **Problema con la clave secreta JWT**:
   - Asegúrate de que la clave secreta en `.env` sea válida
   - Verifica que la clave secreta sea consistente en todos los entornos

4. **Logs del servidor**:
   - Verifica los logs del servidor para obtener más detalles sobre el error:
     ```bash
     # Si estás usando Docker
     docker logs wavestudio_api
     
     # Si estás conectado a la instancia EC2
     ssh ubuntu@tu-instancia-ec2 'docker logs wavestudio_api'
     ```

## Desarrollo local

### Con Docker Compose

```bash
# Construir y ejecutar los contenedores
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener los contenedores
docker-compose down
```

### Sin Docker

```bash
# Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Estructura del proyecto

```
wavestudio-backend/
├── .github/
│   └── workflows/
│       └── deploy.yml      # Configuración de GitHub Actions
├── alembic/                # Migraciones de base de datos
├── db/                     # Configuración de base de datos
│   ├── CRUD/               # Operaciones CRUD
│   └── database.py         # Configuración de conexión
├── JWT/                    # Autenticación JWT
├── models/                 # Modelos SQLAlchemy
├── nginx/                  # Configuración de Nginx
├── routers/                # Endpoints de la API
├── schemas/                # Esquemas Pydantic
├── scripts/                # Scripts de utilidad
│   ├── diagnose_all.sh     # Script de diagnóstico completo (Linux)
│   ├── diagnose_macos.sh   # Script de diagnóstico para macOS
│   ├── setup-ec2.sh        # Script para configurar EC2 (Ubuntu)
│   ├── setup-github-secrets.sh # Script para configurar GitHub Secrets
│   ├── test_cors.py        # Script para probar CORS
│   ├── test_db_connection.py # Script para probar la conexión a la BD
│   ├── test_jwt.py         # Script para probar JWT
│   └── test_login.py       # Script para probar el endpoint de login
├── utils/                  # Utilidades
├── .env                    # Variables de entorno (no incluir en git)
├── .gitignore              # Archivos a ignorar por git
├── alembic.ini             # Configuración de Alembic
├── docker-compose.yml      # Configuración de Docker Compose
├── Dockerfile              # Configuración de Docker
├── main.py                 # Punto de entrada de la aplicación
├── README.md               # Documentación
└── requirements.txt        # Dependencias
