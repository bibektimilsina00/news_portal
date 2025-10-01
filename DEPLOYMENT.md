# 🚀 News Portal API - Deployment Guide

This guide covers the comple## 🔐 GitHub Secrets Setup

Before deploying, you need to configure GitHub secrets. See [`.github/SECRETS.md`](.github/SECRETS.md) for a complete guide on required secrets.

### Quick Setup

In your GitHub repository → Settings → Secrets and variables → Actions, add these secrets:

**Required for Deployment:**
```
VPS_HOST=your-vps-ip-or-domain
VPS_USER=your-ssh-username
VPS_SSH_KEY=your-private-ssh-key
VPS_PORT=22
```

**Optional for CI/Testing:**
```
SECRET_KEY=your-jwt-secret
FIRST_SUPERUSER=admin@yourdomain.com
FIRST_SUPERUSER_PASSWORD=secure-password
PROJECT_NAME=News Portal
```etup and deployment process for the News Portal API to a Linux VPS.

## 📋 Prerequisites

- Linux VPS with Ubuntu 20.04+ or similar
- SSH access to your VPS
- Domain name (optional but recommended)
- GitHub repository access

## 🔧 CI/CD Pipeline Overview

The CI/CD pipeline includes:

1. **Continuous Integration (CI)**:
   - Code linting and formatting
   - Type checking with MyPy
   - Security scanning with Bandit
   - Unit and integration tests
   - Docker image building

2. **Continuous Deployment (CD)**:
   - Automated deployment to VPS on main branch pushes
   - Docker container orchestration
   - Health checks and rollbacks

## 🚀 Quick Deployment

### 1. VPS Setup

```bash
# On your VPS, run the deployment script
curl -fsSL https://raw.githubusercontent.com/bibektimilsina00/news-portal/main/deploy.sh | bash
```

Or manually:

```bash
# Clone and run the deployment script
git clone https://github.com/bibektimilsina00/news-portal.git
cd news-portal
chmod +x deploy.sh
./deploy.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.prod.example .env.prod

# Edit with your values
nano .env.prod
```

Required environment variables:
```bash
ENVIRONMENT=production
PROJECT_NAME=News Portal
DOMAIN=yourdomain.com
SECRET_KEY=your-super-secret-key-here
POSTGRES_USER=news_portal
POSTGRES_PASSWORD=your-secure-db-password
POSTGRES_DB=news_portal_prod
FIRST_SUPERUSER=admin@yourdomain.com
FIRST_SUPERUSER_PASSWORD=your-secure-admin-password
```

### 3. GitHub Secrets Setup

In your GitHub repository, go to Settings → Secrets and variables → Actions and add:

```
VPS_HOST=your-vps-ip-or-domain
VPS_USER=your-ssh-username
VPS_SSH_KEY=your-private-ssh-key
VPS_PORT=22  # Optional, defaults to 22
```

### 4. Deploy

The deployment happens automatically when you push to the `main` branch. To deploy manually:

```bash
# On your VPS
cd /opt/news-portal
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web uv run alembic upgrade head
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Actions │    │  Container      │    │   Linux VPS     │
│   CI/CD Pipeline │───▶│  Registry       │───▶│                 │
│                 │    │                 │    │  ┌─────────────┐ │
└─────────────────┘    └─────────────────┘    │  │  Nginx      │ │
                                              │  │  Reverse    │ │
                                              │  │  Proxy      │ │
                                              │  └─────────────┘ │
                                              │  ┌─────────────┐ │
                                              │  │  FastAPI     │ │
                                              │  │  Application │ │
                                              │  └─────────────┘ │
                                              │  ┌─────────────┐ │
                                              │  │ PostgreSQL   │ │
                                              │  │  Database    │ │
                                              │  └─────────────┘ │
                                              │  ┌─────────────┐ │
                                              │  │   Redis      │ │
                                              │  │   Cache      │ │
                                              │  └─────────────┘ │
                                              └─────────────────┘
```

## 📁 File Structure

```
/opt/news-portal/
├── docker-compose.prod.yml    # Production Docker Compose
├── nginx.conf                 # Nginx configuration
├── .env.prod                  # Production environment variables
├── media/                     # User uploaded media files
├── logs/                      # Application logs
├── ssl/                       # SSL certificates
└── backup.sh                  # Database backup script
```

## 🔍 Health Checks

The application includes health check endpoints:

- `GET /api/v1/health` - General application health
- `GET /api/v1/health/db` - Database connectivity check

## 🔄 Database Migrations

Database migrations run automatically during deployment:

```bash
docker-compose -f docker-compose.prod.yml exec web uv run alembic upgrade head
```

## 📊 Monitoring & Logs

### Application Logs
```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f web

# View nginx logs
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### System Monitoring
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# Check resource usage
docker stats

# Check nginx status
sudo systemctl status nginx
```

## 🔐 SSL Configuration

### Automatic (Let's Encrypt)
```bash
sudo certbot --nginx -d yourdomain.com --email admin@yourdomain.com
```

### Manual SSL
1. Place your certificates in `/opt/news-portal/ssl/`
2. Uncomment the HTTPS server block in `nginx.conf`
3. Restart nginx: `docker-compose -f docker-compose.prod.yml restart nginx`

## 💾 Backup & Recovery

### Automated Backups
Backups run daily at 2 AM via cron job. Files are stored in `/opt/news-portal/backups/`

### Manual Backup
```bash
cd /opt/news-portal
./backup.sh
```

### Restore from Backup
```bash
# Restore database
docker-compose -f docker-compose.prod.yml exec -T db psql -U $POSTGRES_USER -d $POSTGRES_DB < backups/db_backup_DATE.sql

# Restore media files
tar -xzf backups/media_backup_DATE.tar.gz
```

## 🚨 Troubleshooting

### Common Issues

1. **Container fails to start**
   ```bash
   docker-compose -f docker-compose.prod.yml logs web
   ```

2. **Database connection issues**
   ```bash
   docker-compose -f docker-compose.prod.yml exec db pg_isready -U $POSTGRES_USER -d $POSTGRES_DB
   ```

3. **Permission issues**
   ```bash
   sudo chown -R $USER:$USER /opt/news-portal
   ```

4. **Port conflicts**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :8000
   ```

### Rollback Deployment

```bash
# Stop current deployment
docker-compose -f docker-compose.prod.yml down

# Pull previous image (if using tags)
docker pull ghcr.io/bibektimilsina00/news-portal:previous-tag

# Update docker-compose.prod.yml with previous tag
# Then restart
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 Maintenance

### Update Application
```bash
cd /opt/news-portal
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml exec web uv run alembic upgrade head
```

### Update SSL Certificate
```bash
sudo certbot renew
docker-compose -f docker-compose.prod.yml restart nginx
```

### Scale Services
```bash
# Scale web service
docker-compose -f docker-compose.prod.yml up -d --scale web=3
```

## 📞 Support

For issues or questions:
1. Check the logs: `docker-compose -f docker-compose.prod.yml logs`
2. Verify environment variables in `.env.prod`
3. Test locally with `docker-compose -f docker-compose.prod.yml up`
4. Check GitHub Actions logs for CI/CD issues

## 🔒 Security Considerations

- Change default passwords immediately
- Use strong, unique SECRET_KEY
- Keep dependencies updated
- Monitor logs for suspicious activity
- Use firewall rules appropriately
- Regularly update SSL certificates
- Backup data regularly