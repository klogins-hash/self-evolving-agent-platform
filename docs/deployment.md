# Deployment Guide

## Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- Git
- Docker (optional)

### Setup Steps

1. **Clone and Setup**
```bash
git clone <repository-url>
cd self-evolving-agent-platform/mvp
chmod +x scripts/setup.sh
./scripts/setup.sh
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Start Services**

**Option A: Manual Start**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
source venv/bin/activate
chainlit run app.py
```

**Option B: Docker Compose**
```bash
docker-compose up --build
```

### Access Points
- Frontend UI: http://localhost:8001
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Production Deployment

### Environment Variables

Required for production:
```bash
# API Keys
OPENAI_API_KEY=your_production_key
ANTHROPIC_API_KEY=your_production_key

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security
SECRET_KEY=your_super_secure_secret_key
DEBUG=false

# CORS (restrict to your domain)
CORS_ORIGINS=["https://yourdomain.com"]
```

### Docker Production Setup

1. **Build Images**
```bash
docker build -t agent-platform-backend ./backend
docker build -t agent-platform-frontend ./frontend
```

2. **Production Docker Compose**
```yaml
version: '3.8'
services:
  backend:
    image: agent-platform-backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    ports:
      - "8000:8000"
    
  frontend:
    image: agent-platform-frontend
    environment:
      - BACKEND_URL=https://api.yourdomain.com
    ports:
      - "8001:8001"
    depends_on:
      - backend
```

### Cloud Deployment Options

#### Option 1: Railway/Render
1. Connect your Git repository
2. Set environment variables
3. Deploy backend and frontend as separate services

#### Option 2: AWS/GCP/Azure
1. Use container services (ECS, Cloud Run, Container Instances)
2. Set up load balancer
3. Configure database (RDS, Cloud SQL, etc.)

#### Option 3: DigitalOcean App Platform
1. Create new app from Git
2. Configure services and environment
3. Set up managed database

### Database Migration

For production PostgreSQL:

1. **Update DATABASE_URL**
```bash
DATABASE_URL=postgresql://user:password@host:5432/agents_db
```

2. **Install PostgreSQL adapter**
```bash
pip install psycopg2-binary
```

3. **Update docker-compose.yml**
Uncomment PostgreSQL service section.

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=false
- [ ] Configure CORS_ORIGINS properly
- [ ] Use HTTPS in production
- [ ] Secure database credentials
- [ ] Set up monitoring and logging
- [ ] Configure rate limiting
- [ ] Regular security updates

### Monitoring and Logging

#### Health Checks
- Backend: `GET /health`
- Monitor response time and availability

#### Logging
```python
# Add to production config
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/platform.log'),
        logging.StreamHandler()
    ]
)
```

### Scaling Considerations

#### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use shared database for state
- Consider Redis for session management

#### Performance Optimization
- Enable database connection pooling
- Implement caching (Redis/Memcached)
- Use CDN for static assets
- Monitor and optimize database queries

### Backup Strategy

#### Database Backups
```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Automated backups (cron)
0 2 * * * pg_dump $DATABASE_URL > /backups/agents_$(date +\%Y\%m\%d).sql
```

#### Configuration Backups
- Store environment configurations in secure vault
- Version control infrastructure as code
- Regular backup of logs and data

### Troubleshooting

#### Common Issues

**Backend won't start:**
- Check Python version (3.11+ required)
- Verify all dependencies installed
- Check environment variables
- Review logs for specific errors

**Frontend can't connect:**
- Verify BACKEND_URL is correct
- Check CORS configuration
- Ensure backend is running and accessible

**Database connection issues:**
- Verify DATABASE_URL format
- Check database server status
- Confirm credentials and permissions

#### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true
```

### Support and Maintenance

#### Regular Tasks
- Monitor system health and performance
- Update dependencies regularly
- Review and rotate API keys
- Backup data and configurations
- Monitor resource usage and costs

#### Updates and Patches
- Test updates in staging environment
- Follow semantic versioning
- Maintain changelog
- Plan maintenance windows for major updates

This deployment guide provides a foundation for both development and production environments, with room for customization based on specific infrastructure needs.
