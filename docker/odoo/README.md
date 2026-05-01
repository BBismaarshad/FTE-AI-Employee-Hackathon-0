# Odoo Docker Setup - Gold Tier

This directory contains the Docker Compose configuration for running Odoo Community Edition 19 locally.

## Quick Start

### 1. Copy Environment File

```bash
cp .env.example .env
```

### 2. Start Odoo

```bash
docker compose up -d
```

### 3. Access Odoo

Open browser: http://localhost:8069

### 4. Initial Setup

1. **Create Database**
   - Database Name: `odoo`
   - Email: your email
   - Password: choose a secure password
   - Language: English
   - Country: Your country

2. **Install Accounting Module**
   - Go to Apps
   - Search "Accounting"
   - Click Install

## Services

### odoo-db (PostgreSQL)
- **Image:** postgres:16-alpine
- **Port:** Internal only (not exposed)
- **Data:** Persisted in Docker volume

### odoo (Odoo 19)
- **Image:** odoo:19.0
- **Port:** 8069 (web interface)
- **Data:** Persisted in Docker volume

### odoo-backup (Automatic Backups)
- **Schedule:** Daily at midnight
- **Retention:** 7 days
- **Location:** `./backups/`

## Management Commands

### Start Services

```bash
docker compose up -d
```

### Stop Services

```bash
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Odoo only
docker compose logs -f odoo

# Database only
docker compose logs -f odoo-db
```

### Restart Services

```bash
docker compose restart
```

### Check Status

```bash
docker compose ps
```

## Data Persistence

Data is stored in Docker volumes:

- `ai-employee-odoo-db-data` - PostgreSQL database
- `ai-employee-odoo-filestore` - Odoo attachments and files

### Backup Data

```bash
# Database backup
docker compose exec odoo-db pg_dump -U odoo odoo > backup_$(date +%Y%m%d).sql

# Automatic backups are in ./backups/
ls -lh backups/
```

### Restore Data

```bash
# Stop Odoo
docker compose stop odoo

# Restore database
cat backup_20260501.sql | docker compose exec -T odoo-db psql -U odoo odoo

# Start Odoo
docker compose start odoo
```

## Configuration

### Custom Modules

Place custom Odoo modules in `./extra-addons/`:

```bash
mkdir -p extra-addons/my_custom_module
# Add your module files
docker compose restart odoo
```

### Odoo Configuration

Place custom config in `./config/odoo.conf`:

```ini
[options]
admin_passwd = admin
db_host = odoo-db
db_port = 5432
db_user = odoo
db_password = odoo_db_secret_2026
```

## Troubleshooting

### Issue: Port 8069 already in use

**Solution:**
```bash
# Change port in .env
echo "ODOO_PORT=8070" >> .env
docker compose up -d
```

### Issue: Database connection failed

**Solution:**
```bash
# Check database is running
docker compose ps odoo-db

# Check database logs
docker compose logs odoo-db

# Restart database
docker compose restart odoo-db
```

### Issue: Odoo won't start

**Solution:**
```bash
# Check logs
docker compose logs odoo

# Common causes:
# 1. Database not ready - wait 30 seconds
# 2. Port conflict - change ODOO_PORT
# 3. Volume permissions - check Docker settings
```

### Issue: Can't access http://localhost:8069

**Solution:**
1. Check Odoo is running: `docker compose ps`
2. Check port mapping: `docker compose ps odoo`
3. Try: http://127.0.0.1:8069
4. Check firewall settings

## Integration with AI Employee

### Python Integration

```python
from skills.odoo_mcp import OdooMCP

odoo = OdooMCP(
    url='http://localhost:8069',
    db='odoo',
    username='admin',
    password='your_password',
    vault_path='./AI_Employee_Vault'
)

# List customers
partners = odoo.list_partners()
print(partners)
```

### Weekly Audit Integration

```bash
python skills/weekly_audit.py \
  --vault .\AI_Employee_Vault \
  --odoo-url http://localhost:8069 \
  --odoo-db odoo \
  --odoo-user admin \
  --odoo-password your_password
```

## Security Notes

- ⚠️ **Default passwords** - Change in production
- 🔒 **Network isolation** - Database not exposed externally
- 📝 **Audit logging** - All operations logged
- 💾 **Automatic backups** - Daily backups enabled

## Production Deployment

For production use:

1. **Use strong passwords**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Enable HTTPS**
   - Use reverse proxy (nginx, traefik)
   - Configure SSL certificates

3. **External database**
   - Use managed PostgreSQL
   - Configure connection in .env

4. **Regular backups**
   - Verify backup schedule
   - Test restore procedure
   - Store backups off-site

## Resources

- [Odoo Documentation](https://www.odoo.com/documentation/19.0/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Part of Gold Tier - FTE AI Employee Hackathon**
