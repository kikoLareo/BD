#!/bin/bash
# Script para desplegar los cambios en el servidor

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Despliegue de cambios en el servidor ===${NC}"
echo -e "Este script desplegará los cambios en el servidor y reiniciará la aplicación."
echo

# Verificar si se proporcionó el host del servidor
if [ $# -lt 1 ]; then
    echo -e "${YELLOW}Uso: $0 <usuario@host> [ruta_del_proyecto]${NC}"
    echo -e "Ejemplo: $0 ubuntu@tu-instancia-ec2.amazonaws.com /home/ubuntu/wavestudio-backend"
    
    # Preguntar por el host del servidor
    echo -e "${BLUE}Ingresa el host del servidor (usuario@host):${NC}"
    read -p "> " SERVER_HOST
    
    if [ -z "$SERVER_HOST" ]; then
        echo -e "${RED}Error: No se proporcionó el host del servidor.${NC}"
        exit 1
    fi
else
    SERVER_HOST=$1
fi

# Verificar si se proporcionó la ruta del proyecto
if [ $# -lt 2 ]; then
    # Preguntar por la ruta del proyecto
    echo -e "${BLUE}Ingresa la ruta del proyecto en el servidor (por defecto: /home/ubuntu/BD):${NC}"
    read -p "> " PROJECT_PATH
    
    # Usar valor por defecto si no se proporciona
    PROJECT_PATH=${PROJECT_PATH:-"/home/ubuntu/BD"}
else
    PROJECT_PATH=$2
fi

echo -e "${BLUE}Host del servidor: ${SERVER_HOST}${NC}"
echo -e "${BLUE}Ruta del proyecto: ${PROJECT_PATH}${NC}"
echo

# Confirmar antes de continuar
echo -e "${YELLOW}¿Deseas continuar con el despliegue? (s/n)${NC}"
read -p "> " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo -e "${RED}Operación cancelada.${NC}"
    exit 1
fi

# Verificar conexión SSH
echo -e "${BLUE}Verificando conexión SSH...${NC}"
if ! ssh -o BatchMode=yes -o ConnectTimeout=5 $SERVER_HOST "echo 'Conexión exitosa'"; then
    echo -e "${RED}Error: No se pudo conectar al servidor.${NC}"
    echo -e "${YELLOW}Verifica que:${NC}"
    echo -e "  - La dirección del servidor sea correcta"
    echo -e "  - Tengas acceso SSH al servidor"
    echo -e "  - La clave SSH esté configurada correctamente"
    exit 1
fi

# Desplegar los cambios
echo -e "${BLUE}Desplegando cambios...${NC}"

# Crear un script temporal para ejecutar en el servidor
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << EOL
#!/bin/bash
set -e

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "\${BLUE}=== Desplegando cambios en el servidor ===${NC}"

# Verificar si el directorio del proyecto existe
if [ ! -d "$PROJECT_PATH" ]; then
    echo -e "\${RED}Error: El directorio del proyecto no existe: $PROJECT_PATH${NC}"
    exit 1
fi

# Ir al directorio del proyecto
cd "$PROJECT_PATH"
echo -e "\${BLUE}Directorio actual: \$(pwd)${NC}"

# Verificar si es un repositorio git
if [ ! -d ".git" ]; then
    echo -e "\${YELLOW}Advertencia: El directorio no es un repositorio git.${NC}"
    echo -e "\${YELLOW}No se pueden actualizar los cambios automáticamente.${NC}"
else
    # Guardar cambios locales si los hay
    if [ -n "\$(git status --porcelain)" ]; then
        echo -e "\${YELLOW}Hay cambios locales en el servidor. Guardándolos...${NC}"
        git stash
        STASHED=true
    fi
    
    # Actualizar el repositorio
    echo -e "\${BLUE}Actualizando el repositorio...${NC}"
    git fetch
    git pull
    
    # Restaurar cambios locales si los había
    if [ "\$STASHED" = true ]; then
        echo -e "\${BLUE}Restaurando cambios locales...${NC}"
        git stash pop
    fi
fi

# Verificar si existe el archivo .env
if [ ! -f ".env" ]; then
    echo -e "\${YELLOW}Advertencia: No se encontró el archivo .env${NC}"
    echo -e "\${YELLOW}Creando archivo .env con valores por defecto...${NC}"
    
    cat > .env << EOF
# Variables de entorno para la aplicación

# Configuración de la base de datos
DATABASE_URL=postgresql://kiko:.,Franlareo1701_.,@wavestudio.cwzqig2qy005.us-east-1.rds.amazonaws.com:5432/wavestudio

# Configuración de JWT
SECRET_KEY=your_secret_key_here_change_this_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración del usuario Master inicial
MASTER_USERNAME=admin
MASTER_EMAIL=admin@wavestudio.com
MASTER_PASSWORD=admin123

# Configuración general
DEBUG=False
EOF
fi

# Verificar si el usuario admin existe y crearlo si no existe
echo -e "\${BLUE}Verificando si el usuario admin existe...${NC}"
python3 scripts/ensure_admin_user.py --force

# Verificar si la aplicación está corriendo con Docker
if docker ps | grep -q "wavestudio_api"; then
    echo -e "\${BLUE}Reiniciando la aplicación con Docker...${NC}"
    docker-compose down
    docker-compose up -d
else
    # Verificar si hay un proceso uvicorn corriendo
    PID=\$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print \$2}')
    
    if [ -n "\$PID" ]; then
        echo -e "\${BLUE}Reiniciando el proceso uvicorn (PID: \$PID)...${NC}"
        kill -15 \$PID
        sleep 2
        
        # Verificar si el proceso sigue corriendo
        if ps -p \$PID > /dev/null; then
            echo -e "\${YELLOW}El proceso no se detuvo correctamente. Forzando cierre...${NC}"
            kill -9 \$PID
        fi
    fi
    
    # Iniciar la aplicación con uvicorn
    echo -e "\${BLUE}Iniciando la aplicación con uvicorn...${NC}"
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
fi

echo -e "\${GREEN}¡Despliegue completado exitosamente!${NC}"
EOL

# Copiar el script al servidor
echo -e "${BLUE}Copiando script al servidor...${NC}"
scp "$TMP_SCRIPT" $SERVER_HOST:/tmp/deploy.sh

# Ejecutar el script en el servidor
echo -e "${BLUE}Ejecutando script en el servidor...${NC}"
ssh $SERVER_HOST "chmod +x /tmp/deploy.sh && /tmp/deploy.sh"

# Eliminar el script temporal
rm "$TMP_SCRIPT"

echo -e "${GREEN}¡Despliegue completado exitosamente!${NC}"
echo -e "${BLUE}Puedes verificar el estado de la aplicación con:${NC}"
echo -e "  ssh $SERVER_HOST 'docker logs wavestudio_api' # Si usas Docker"
echo -e "  ssh $SERVER_HOST 'tail -f uvicorn.log' # Si usas uvicorn directamente"
