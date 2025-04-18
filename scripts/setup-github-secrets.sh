#!/bin/bash
# Script para ayudar a configurar los secrets de GitHub para CI/CD

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Configuración de Secrets para GitHub Actions ===${NC}"
echo -e "Este script te guiará para configurar los secrets necesarios para el pipeline de CI/CD."
echo -e "Necesitarás tener instalado el CLI de GitHub (gh) y estar autenticado."
echo

# Detectar el sistema operativo
OS="$(uname -s)"
case "${OS}" in
    Darwin*)    
        echo -e "${GREEN}Sistema detectado: macOS${NC}"
        ;;
    Linux*)     
        echo -e "${GREEN}Sistema detectado: Linux${NC}"
        ;;
    CYGWIN*|MINGW*|MSYS*) 
        echo -e "${YELLOW}Sistema detectado: Windows${NC}"
        echo -e "${YELLOW}Este script puede no funcionar correctamente en Windows.${NC}"
        echo -e "${YELLOW}Se recomienda usar WSL (Windows Subsystem for Linux) o Git Bash.${NC}"
        ;;
    *)          
        echo -e "${YELLOW}Sistema operativo desconocido: ${OS}${NC}"
        ;;
esac
echo

# Verificar si gh está instalado
if ! command -v gh &> /dev/null; then
    echo -e "${RED}Error: GitHub CLI (gh) no está instalado.${NC}"
    echo -e "Por favor, instálalo desde: https://cli.github.com/"
    exit 1
fi

# Verificar si el usuario está autenticado
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}No estás autenticado en GitHub CLI.${NC}"
    echo -e "Por favor, ejecuta 'gh auth login' primero."
    exit 1
fi

# Obtener el nombre del repositorio
echo -e "${BLUE}Paso 1: Identificar el repositorio${NC}"
echo -e "Ingresa el nombre del repositorio en formato 'usuario/repo':"
read -p "> " REPO_NAME

# Verificar si el repositorio existe
if ! gh repo view "$REPO_NAME" &> /dev/null; then
    echo -e "${RED}Error: El repositorio $REPO_NAME no existe o no tienes acceso.${NC}"
    exit 1
fi

echo -e "${GREEN}Repositorio $REPO_NAME encontrado.${NC}"
echo

# Configurar AWS credentials
echo -e "${BLUE}Paso 2: Configurar credenciales de AWS${NC}"
echo -e "Ingresa el AWS Access Key ID:"
read -p "> " AWS_ACCESS_KEY_ID

echo -e "Ingresa el AWS Secret Access Key:"
read -s -p "> " AWS_SECRET_ACCESS_KEY
echo

echo -e "Ingresa la región de AWS (por ejemplo, us-east-1):"
read -p "> " AWS_REGION

echo -e "Ingresa el nombre del repositorio ECR:"
read -p "> " ECR_REPOSITORY

# Configurar EC2 credentials
echo -e "${BLUE}Paso 3: Configurar credenciales de EC2${NC}"
echo -e "Ingresa la dirección IP pública o el nombre de dominio de tu instancia EC2:"
read -p "> " EC2_HOST

echo -e "Ingresa el nombre de usuario para SSH (normalmente 'ubuntu' para instancias Ubuntu):"
read -p "> " EC2_USERNAME

echo -e "Ingresa la ruta al archivo de clave SSH privada:"
read -p "> " SSH_KEY_PATH

# Verificar si el archivo de clave SSH existe
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo -e "${RED}Error: El archivo de clave SSH $SSH_KEY_PATH no existe.${NC}"
    exit 1
fi

# Leer el contenido de la clave SSH
EC2_SSH_KEY=$(cat "$SSH_KEY_PATH")

# Configurar variables de base de datos
echo -e "${BLUE}Paso 4: Configurar variables de base de datos${NC}"
echo -e "Ingresa el host de la base de datos:"
read -p "> " DB_HOST

echo -e "Ingresa el nombre de la base de datos:"
read -p "> " DB_NAME

echo -e "Ingresa el usuario de la base de datos:"
read -p "> " DB_USER

echo -e "Ingresa la contraseña de la base de datos:"
read -s -p "> " DB_PASSWORD
echo

# Configurar variables de aplicación
echo -e "${BLUE}Paso 5: Configurar variables de aplicación${NC}"
echo -e "Ingresa la clave secreta para JWT:"
read -s -p "> " SECRET_KEY
echo

echo -e "Ingresa el nombre de usuario del administrador:"
read -p "> " MASTER_USERNAME

echo -e "Ingresa el email del administrador:"
read -p "> " MASTER_EMAIL

echo -e "Ingresa la contraseña del administrador:"
read -s -p "> " MASTER_PASSWORD
echo

# Confirmar antes de crear los secrets
echo -e "${YELLOW}Estás a punto de crear los siguientes secrets en el repositorio $REPO_NAME:${NC}"
echo -e "- AWS_ACCESS_KEY_ID"
echo -e "- AWS_SECRET_ACCESS_KEY"
echo -e "- AWS_REGION"
echo -e "- ECR_REPOSITORY"
echo -e "- EC2_HOST"
echo -e "- EC2_USERNAME"
echo -e "- EC2_SSH_KEY"
echo -e "- DB_HOST"
echo -e "- DB_NAME"
echo -e "- DB_USER"
echo -e "- DB_PASSWORD"
echo -e "- SECRET_KEY"
echo -e "- MASTER_USERNAME"
echo -e "- MASTER_EMAIL"
echo -e "- MASTER_PASSWORD"

echo -e "${YELLOW}¿Deseas continuar? (s/n)${NC}"
read -p "> " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
    echo -e "${RED}Operación cancelada.${NC}"
    exit 1
fi

# Crear los secrets
echo -e "${BLUE}Creando secrets...${NC}"

create_secret() {
    local name=$1
    local value=$2
    echo -e "Creando secret $name..."
    if echo "$value" | gh secret set "$name" --repo "$REPO_NAME"; then
        echo -e "${GREEN}Secret $name creado correctamente.${NC}"
    else
        echo -e "${RED}Error al crear el secret $name.${NC}"
        return 1
    fi
}

create_secret "AWS_ACCESS_KEY_ID" "$AWS_ACCESS_KEY_ID" || exit 1
create_secret "AWS_SECRET_ACCESS_KEY" "$AWS_SECRET_ACCESS_KEY" || exit 1
create_secret "AWS_REGION" "$AWS_REGION" || exit 1
create_secret "ECR_REPOSITORY" "$ECR_REPOSITORY" || exit 1
create_secret "EC2_HOST" "$EC2_HOST" || exit 1
create_secret "EC2_USERNAME" "$EC2_USERNAME" || exit 1
create_secret "EC2_SSH_KEY" "$EC2_SSH_KEY" || exit 1
create_secret "DB_HOST" "$DB_HOST" || exit 1
create_secret "DB_NAME" "$DB_NAME" || exit 1
create_secret "DB_USER" "$DB_USER" || exit 1
create_secret "DB_PASSWORD" "$DB_PASSWORD" || exit 1
create_secret "SECRET_KEY" "$SECRET_KEY" || exit 1
create_secret "MASTER_USERNAME" "$MASTER_USERNAME" || exit 1
create_secret "MASTER_EMAIL" "$MASTER_EMAIL" || exit 1
create_secret "MASTER_PASSWORD" "$MASTER_PASSWORD" || exit 1

echo -e "${GREEN}¡Todos los secrets han sido creados correctamente!${NC}"
echo -e "${BLUE}Ahora puedes hacer push a tu repositorio para activar el pipeline de CI/CD.${NC}"
