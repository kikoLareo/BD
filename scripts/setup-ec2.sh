#!/bin/bash
# Script to set up an EC2 instance for the WaveStudio backend deployment

# Colores para la salida
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Configuración de instancia EC2 para WaveStudio ===${NC}"
echo -e "Este script está diseñado para ejecutarse en una instancia EC2 con Ubuntu."
echo

# Verificar si estamos en un sistema Ubuntu/Debian
if [ ! -f /etc/debian_version ] && [ ! -f /etc/lsb-release ]; then
    echo -e "${RED}¡ADVERTENCIA! Este script está diseñado para ejecutarse en una instancia EC2 con Ubuntu.${NC}"
    echo -e "${RED}Parece que estás ejecutando este script en un sistema que no es Ubuntu/Debian.${NC}"
    echo -e "${YELLOW}Este script utiliza comandos específicos de Ubuntu como apt-get.${NC}"
    echo -e "${YELLOW}Si continúas, es probable que encuentres errores.${NC}"
    echo
    echo -e "${BLUE}¿Deseas continuar de todos modos? (s/n)${NC}"
    read -p "> " CONTINUE
    if [ "$CONTINUE" != "s" ] && [ "$CONTINUE" != "S" ]; then
        echo -e "${RED}Operación cancelada.${NC}"
        exit 1
    fi
fi

# Exit on error
set -e

# Update system packages
echo -e "${BLUE}Actualizando paquetes del sistema...${NC}"
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
echo "Installing Nginx..."
sudo apt-get install -y nginx

# Install Certbot for SSL
echo "Installing Certbot for SSL..."
sudo apt-get install -y certbot python3-certbot-nginx

# Create deployment directory
echo "Creating deployment directory..."
mkdir -p ~/wavestudio-deployment
mkdir -p ~/wavestudio-deployment/logs

# Copy Nginx configuration
echo "Setting up Nginx configuration..."
sudo cp nginx/wavestudio.conf /etc/nginx/sites-available/wavestudio
sudo ln -sf /etc/nginx/sites-available/wavestudio /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Install AWS CLI
echo "Installing AWS CLI..."
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
rm -rf aws awscliv2.zip

# Configure AWS CLI (this will prompt for credentials)
echo "Please configure AWS CLI with your credentials:"
aws configure

# Set up firewall
echo "Setting up firewall..."
sudo apt-get install -y ufw
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8000
sudo ufw --force enable

# Set up automatic security updates
echo "Setting up automatic security updates..."
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# Create a script to obtain SSL certificate
cat > ~/get-ssl-cert.sh << 'EOL'
#!/bin/bash
sudo certbot --nginx -d wavestudio-backend.com
EOL
chmod +x ~/get-ssl-cert.sh

echo "EC2 instance setup completed!"
echo "Next steps:"
echo "1. Run ~/get-ssl-cert.sh to obtain SSL certificate for your domain"
echo "2. Configure GitHub repository secrets for CI/CD"
echo "3. Push code to GitHub to trigger deployment"
