#!/bin/bash
# Claude SEO Unified - One-Click VPS Deployment
# Usage: curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/claude-seo-unified/main/deploy/vps-deploy.sh | sudo bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Claude SEO Unified - VPS Deployment        ║${NC}"
echo -e "${GREEN}║   Version 1.9.6                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo -e "${RED}❌ Please run as root (use sudo)${NC}"
   exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., seo-api.yourcompany.com): " DOMAIN
read -p "Enter GitHub username for repo clone: " GH_USER

echo -e "\n${YELLOW}📋 Configuration:${NC}"
echo "  Domain: $DOMAIN"
echo "  GitHub: github.com/$GH_USER/claude-seo-unified"
echo ""
read -p "Proceed with installation? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

echo -e "\n${GREEN}🔄 Updating system...${NC}"
apt update && apt upgrade -y

echo -e "\n${GREEN}📦 Installing dependencies...${NC}"
apt install -y \
  python3.11 python3.11-venv python3-pip \
  nginx redis-server postgresql postgresql-contrib \
  git curl certbot python3-certbot-nginx \
  libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 \
  libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
  libgbm1 libpango-1.0-0 libcairo2 libasound2

echo -e "\n${GREEN}👤 Creating app user...${NC}"
useradd -m -s /bin/bash seoapp || true
usermod -aG www-data seoapp

echo -e "\n${GREEN}📥 Cloning repository...${NC}"
cd /home/seoapp
if [ -d "claude-seo-unified" ]; then
    sudo -u seoapp git -C claude-seo-unified pull
else
    sudo -u seoapp git clone https://github.com/$GH_USER/claude-seo-unified.git
fi
cd claude-seo-unified

echo -e "\n${GREEN}🐍 Setting up Python environment...${NC}"
sudo -u seoapp python3.11 -m venv venv
sudo -u seoapp venv/bin/pip install --upgrade pip
sudo -u seoapp venv/bin/pip install -r requirements.txt
sudo -u seoapp venv/bin/pip install gunicorn flask flask-cors celery redis psycopg2-binary

echo -e "\n${GREEN}🎭 Installing Playwright...${NC}"
sudo -u seoapp venv/bin/playwright install chromium
sudo -u seoapp venv/bin/playwright install-deps || true

echo -e "\n${GREEN}📁 Creating directories...${NC}"
sudo -u seoapp mkdir -p logs output .seo-cache config/credentials

echo -e "\n${GREEN}⚙️ Copying config templates...${NC}"
sudo -u seoapp cp config/config.example.yaml config/config.yaml
sudo -u seoapp cp config/.env.example .env

echo -e "\n${GREEN}🗄️ Setting up PostgreSQL...${NC}"
DB_PASSWORD=$(openssl rand -hex 16)
sudo -u postgres psql -c "CREATE DATABASE seo_production;" || true
sudo -u postgres psql -c "CREATE USER seoapp WITH PASSWORD '$DB_PASSWORD';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE seo_production TO seoapp;"

echo -e "\n${GREEN}🔧 Configuring environment...${NC}"
API_KEY=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)

cat > .env.production << ENVEOF
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=$SECRET_KEY
API_KEY=$API_KEY
DATABASE_URL=postgresql://seoapp:$DB_PASSWORD@localhost:5432/seo_production
REDIS_URL=redis://localhost:6379/0

# TODO: Add your API keys below
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
DATAFORSEO_USERNAME=
DATAFORSEO_PASSWORD=
GOOGLE_PAGESPEED_API_KEY=
ENVEOF

sudo -u seoapp mv .env.production .env

echo -e "\n${GREEN}🌐 Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/seo-api << NGINXEOF
server {
    listen 80;
    server_name $DOMAIN;
    client_max_body_size 10M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/seo-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo -e "\n${GREEN}🔐 Setting up SSL...${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --register-unsafely-without-email || \
  echo -e "${YELLOW}⚠️ SSL setup failed. Run manually: certbot --nginx -d $DOMAIN${NC}"

echo -e "\n${GREEN}🚀 Creating systemd service...${NC}"
cat > /etc/systemd/system/seo-api.service << SERVICEEOF
[Unit]
Description=Claude SEO API Server
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=seoapp
Group=www-data
WorkingDirectory=/home/seoapp/claude-seo-unified
Environment="PATH=/home/seoapp/claude-seo-unified/venv/bin"
ExecStart=/home/seoapp/claude-seo-unified/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:5000 \
    --timeout 300 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    api_server:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

systemctl daemon-reload
systemctl enable seo-api
systemctl start seo-api

echo -e "\n${GREEN}✅ Installation complete!${NC}"
echo ""
echo -e "${YELLOW}📋 IMPORTANT - Next Steps:${NC}"
echo ""
echo "1. Add API keys to environment file:"
echo "   nano /home/seoapp/claude-seo-unified/.env"
echo ""
echo "2. Restart service:"
echo "   systemctl restart seo-api"
echo ""
echo "3. Check status:"
echo "   systemctl status seo-api"
echo ""
echo "4. Test API:"
echo "   curl https://$DOMAIN/api/v1/health"
echo ""
echo -e "${YELLOW}🔑 Your API Key (save this):${NC}"
echo "   $API_KEY"
echo ""
echo -e "${YELLOW}🔒 Database Password:${NC}"
echo "   $DB_PASSWORD"
echo ""
echo -e "${GREEN}📖 Full documentation: /home/seoapp/claude-seo-unified/docs/${NC}"
echo ""
