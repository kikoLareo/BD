#!/bin/bash
# Script para ejecutar todos los diagnósticos y encontrar el problema con el endpoint de login

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Diagnóstico completo del endpoint de login ===${NC}"
echo -e "Este script ejecutará todas las pruebas de diagnóstico para identificar el problema con el endpoint de login."
echo

# Verificar que todos los scripts de diagnóstico existen
if [ ! -f "scripts/test_login.py" ] || [ ! -f "scripts/test_db_connection.py" ] || [ ! -f "scripts/test_jwt.py" ] || [ ! -f "scripts/test_cors.py" ]; then
    echo -e "${RED}Error: No se encontraron todos los scripts de diagnóstico.${NC}"
    echo -e "Asegúrate de estar en el directorio raíz del proyecto."
    exit 1
fi

# Verificar que los scripts tienen permisos de ejecución
if [ ! -x "scripts/test_login.py" ] || [ ! -x "scripts/test_db_connection.py" ] || [ ! -x "scripts/test_jwt.py" ] || [ ! -x "scripts/test_cors.py" ]; then
    echo -e "${YELLOW}Algunos scripts no tienen permisos de ejecución. Añadiendo permisos...${NC}"
    chmod +x scripts/test_login.py scripts/test_db_connection.py scripts/test_jwt.py scripts/test_cors.py
fi

# Obtener la URL del endpoint de login
echo -e "${BLUE}Paso 1: Configurar la URL del endpoint de login${NC}"
echo -e "Ingresa la URL completa del endpoint de login (por defecto: http://localhost:8000/api/auth/login):"
read -p "> " LOGIN_URL
LOGIN_URL=${LOGIN_URL:-"http://localhost:8000/api/auth/login"}

# Obtener el origen para las pruebas CORS
echo -e "${BLUE}Paso 2: Configurar el origen para las pruebas CORS${NC}"
echo -e "Ingresa el origen desde el que se realizan las solicitudes (por defecto: derivado de la URL):"
read -p "> " ORIGIN
ORIGIN=${ORIGIN:-""}

# Obtener las credenciales de la base de datos
echo -e "${BLUE}Paso 3: Configurar las credenciales de la base de datos${NC}"
echo -e "Ingresa el host de la base de datos (por defecto: valor de DB_HOST o localhost):"
read -p "> " DB_HOST
DB_HOST=${DB_HOST:-"$(grep -oP 'DB_HOST=\K[^"]+' .env 2>/dev/null || echo 'localhost')"}

echo -e "Ingresa el puerto de la base de datos (por defecto: 5432):"
read -p "> " DB_PORT
DB_PORT=${DB_PORT:-"5432"}

echo -e "Ingresa el nombre de la base de datos (por defecto: valor de DB_NAME o wavestudio_db):"
read -p "> " DB_NAME
DB_NAME=${DB_NAME:-"$(grep -oP 'DB_NAME=\K[^"]+' .env 2>/dev/null || echo 'wavestudio_db')"}

echo -e "Ingresa el usuario de la base de datos (por defecto: valor de DB_USER o kiko):"
read -p "> " DB_USER
DB_USER=${DB_USER:-"$(grep -oP 'DB_USER=\K[^"]+' .env 2>/dev/null || echo 'kiko')"}

echo -e "Ingresa la contraseña de la base de datos (por defecto: valor de DB_PASSWORD):"
read -s -p "> " DB_PASSWORD
echo
DB_PASSWORD=${DB_PASSWORD:-"$(grep -oP 'DB_PASSWORD=\K[^"]+' .env 2>/dev/null || echo '')"}

# Obtener la clave secreta para JWT
echo -e "${BLUE}Paso 4: Configurar la clave secreta para JWT${NC}"
echo -e "Ingresa la clave secreta para JWT (por defecto: valor de SECRET_KEY):"
read -s -p "> " SECRET_KEY
echo
SECRET_KEY=${SECRET_KEY:-"$(grep -oP 'SECRET_KEY=\K[^"]+' .env 2>/dev/null || echo 'your_secret_key_here_change_this_in_production')"}

# Crear un archivo .env temporal para las pruebas
echo -e "${BLUE}Creando archivo .env temporal para las pruebas...${NC}"
TMP_ENV=$(mktemp)
cat > "$TMP_ENV" << EOL
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
SECRET_KEY=$SECRET_KEY
API_URL=$LOGIN_URL
EOL

# Función para ejecutar un script de diagnóstico
run_diagnostic() {
    local script=$1
    local title=$2
    local args=$3
    
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}=== $title ===${NC}"
    echo -e "${BLUE}======================================${NC}"
    
    # Ejecutar el script con el archivo .env temporal
    DOTENV_PATH="$TMP_ENV" "$script" $args
    
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo -e "\n${GREEN}✅ $title completado exitosamente.${NC}"
    else
        echo -e "\n${RED}❌ $title falló con código de salida $exit_code.${NC}"
    fi
    
    # Preguntar si se desea continuar
    echo -e "\n${YELLOW}¿Deseas continuar con el siguiente diagnóstico? (s/n)${NC}"
    read -p "> " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        echo -e "${RED}Diagnóstico interrumpido por el usuario.${NC}"
        exit 1
    fi
}

# Ejecutar los diagnósticos
run_diagnostic "scripts/test_login.py" "Prueba de login" "--url $LOGIN_URL --username admin@wavestudio.com --password admin123 --verbose"
run_diagnostic "scripts/test_db_connection.py" "Prueba de conexión a la base de datos" "--host $DB_HOST --port $DB_PORT --dbname $DB_NAME --user $DB_USER --password $DB_PASSWORD --verbose"
run_diagnostic "scripts/test_jwt.py" "Prueba de generación y validación de tokens JWT" "--secret-key \"$SECRET_KEY\" --verbose"

if [ -n "$ORIGIN" ]; then
    run_diagnostic "scripts/test_cors.py" "Prueba de configuración CORS" "--url $LOGIN_URL --origin $ORIGIN --verbose"
else
    run_diagnostic "scripts/test_cors.py" "Prueba de configuración CORS" "--url $LOGIN_URL --verbose"
fi

# Limpiar el archivo .env temporal
rm "$TMP_ENV"

echo -e "\n${GREEN}=== Diagnóstico completo finalizado ===${NC}"
echo -e "Revisa los resultados de cada prueba para identificar el problema con el endpoint de login."
echo -e "Recuerda que el problema podría estar en múltiples áreas, así que es importante revisar todos los resultados."
