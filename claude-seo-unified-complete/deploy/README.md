# Deployment Options

## 🚀 Quick Deploy

### Option 1: One-Click Script (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/claude-seo-unified/main/deploy/vps-deploy.sh | sudo bash
```

### Option 2: Docker Compose
```bash
git clone https://github.com/YOUR_USERNAME/claude-seo-unified.git
cd claude-seo-unified
cp config/.env.example .env
# Edit .env with your API keys
docker-compose -f deploy/docker-compose.yml up -d
```

### Option 3: Manual VPS
See [VPS_DEPLOYMENT_GUIDE.md](../VPS_DEPLOYMENT_GUIDE.md)

---

## 📋 Files

- `vps-deploy.sh` - One-click Ubuntu/Debian deployment
- `docker-compose.yml` - Docker multi-container setup
- `Dockerfile` - API server container
- `nginx.conf` - Nginx reverse proxy config
- `systemd/` - Systemd service files
- `README.md` - This file

---

## 🔧 Configuration

1. Set API keys in `.env`
2. Update domain in deployment script
3. Run deployment command
4. Test with `curl https://your-domain.com/api/v1/health`

---

## 📚 Documentation

- [VPS Deployment Guide](../VPS_DEPLOYMENT_GUIDE.md) - Complete manual
- [Installation](../docs/INSTALLATION.md) - Local setup
- [Commands](../docs/COMMANDS.md) - API reference
