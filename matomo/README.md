# Matomo Analytics Setup

This directory contains the configuration and deployment files for a Dockerized Matomo analytics installation, configured to work behind an nginx reverse proxy with SSL termination.

## Purpose

This Matomo setup provides web analytics capabilities for SkillSphere projects, allowing tracking of website visitors, page views, and user behavior while maintaining privacy compliance and data ownership.

## Architecture

```text
Internet → nginx (fenrir) → Docker Container (odin:8080) → Matomo
          SSL termination    Reverse proxy headers      Analytics
```

### Components

- **Matomo**: Open-source web analytics platform
- **MySQL Database**: Data storage for analytics
- **nginx Reverse Proxy**: SSL termination and request forwarding
- **Docker Compose**: Container orchestration

## Files Structure

```text
matomo/
├── README.md                    # This documentation
├── docker-compose.matomo.yml    # Docker services definition
├── matomo.config.ini           # Matomo configuration file
└── bak/
    └── matomo.config.ini       # Configuration backup
```

## Configuration Details

### Access URLs

- **Public URL**: `https://homeip.prager.ws/matomo/`
- **Direct URL**: `http://localhost:8080` (internal access)

### Key Configuration Settings

The `matomo.config.ini` file contains critical settings for proxy operation:

```ini
[General]
# Security salt (keep secret)
salt = "47b6db56363bb74e440249b9eee8a0f0"

# Trusted hosts configuration
trusted_hosts[] = "localhost:8080"
trusted_hosts[] = "homeip.prager.ws"
enable_trusted_host_check=0

# SSL and proxy configuration
assume_secure_protocol=1
force_ssl=1
proxy_client_headers[] = "HTTP_X_FORWARDED_FOR"
proxy_client_headers[] = "HTTP_X_REAL_IP"
proxy_host_headers[] = "HTTP_X_FORWARDED_HOST"
proxy_uri_header = "HTTP_X_FORWARDED_URI"
force_ssl_disabled = 0
proxy_ips[] = "*"
```

### Database Configuration

```ini
[database]
host = "db"
username = "matomo"
password = "matomo"
dbname = "matomo"
tables_prefix = "matomo_"
charset = "utf8mb4"
collation = "utf8mb4_0900_ai_ci"
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- nginx reverse proxy configured on the proxy server
- SSL certificate for the domain

### Deployment

1. **Start the containers**:

   ```bash
   cd /home/bernd/Projects/SkillSphere/matomo
   docker-compose -f docker-compose.matomo.yml up -d
   ```

2. **Verify container status**:

   ```bash
   docker-compose -f docker-compose.matomo.yml ps
   ```

3. **Check logs if needed**:

   ```bash
   docker-compose -f docker-compose.matomo.yml logs matomo
   docker-compose -f docker-compose.matomo.yml logs db
   ```

### Initial Setup

After deployment, access `https://homeip.prager.ws/matomo/` to complete the initial Matomo setup:

1. Follow the installation wizard
2. Configure your first website
3. Get the tracking code
4. Add the tracking code to your websites

## nginx Proxy Configuration

The nginx configuration on the proxy server (`fenrir`) should include:

```nginx
location /matomo/ {
    proxy_pass http://odin:8080/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-URI $request_uri;

    proxy_redirect off;
    proxy_buffering off;
}
```

## GeoIP Configuration

Matomo is configured to use local MaxMind GeoLite2 databases for enhanced geolocation tracking.

### Features

- **Enhanced location data**: Country, region, city, latitude, longitude
- **Local database**: Uses MaxMind GeoLite2-City database from host system
- **No external dependencies**: Database is mounted from `/var/lib/GeoIP/`
- **Automatic updates disabled**: Database updates handled by host system

### Configuration

The following GeoIP settings are configured in `matomo.config.ini`:

```ini
[geoip2]
loc_db_url = "/var/lib/GeoIP/GeoLite2-City.mmdb"
auto_update = 0
```

### Database Information

- **Database Path**: `/var/lib/GeoIP/GeoLite2-City.mmdb`
- **Provider**: `geoip2php` (MaxMind GeoIP2 PHP library)
- **Host Mount**: `/var/lib/GeoIP:/var/lib/GeoIP:ro` (read-only)

### Maintenance

#### Re-attribute Existing Visits

To update existing visits with enhanced geolocation data:

```bash
# Re-attribute visits for a specific date range
docker-compose -f docker-compose.matomo.yml exec matomo php /var/www/html/console usercountry:attribute 2025-07-01,2025-07-03 --provider=geoip2php

# Check provider status
docker-compose -f docker-compose.matomo.yml exec matomo php /var/www/html/console usercountry:attribute --help
```

#### Verify GeoIP Functionality

```bash
# Check database availability
docker-compose -f docker-compose.matomo.yml exec matomo ls -la /var/lib/GeoIP/

# Test location data
docker-compose -f docker-compose.matomo.yml exec db mysql -u matomo -pmatomo matomo -e "SELECT idvisit, location_country, location_region, location_city, location_latitude, location_longitude FROM matomo_log_visit WHERE location_latitude IS NOT NULL LIMIT 5;"
```

#### Database Updates

MaxMind databases are updated on the host system. After updates, restart Matomo:

```bash
# Restart to pick up database changes
docker-compose -f docker-compose.matomo.yml restart matomo
```

### GeoIP Maintenance

#### Host Database Updates

MaxMind databases are updated on the host system. After updates, restart Matomo:

```bash
# Restart to pick up database changes
docker-compose -f docker-compose.matomo.yml restart matomo
```

## General Maintenance

### Updating Configuration

1. **Edit the config file**:

   ```bash
   nano /home/bernd/Projects/SkillSphere/matomo/matomo.config.ini
   ```

2. **Restart containers to apply changes**:

   ```bash
   docker-compose -f docker-compose.matomo.yml restart
   ```

3. **Verify config is applied**:

   ```bash
   docker exec matomo_matomo_1 cat /var/www/html/config/config.ini.php
   ```

### Backup

- **Database backup**: Use Matomo's built-in backup features or MySQL dump
- **Configuration backup**: The `bak/` directory contains configuration backups

### Updates

1. **Update Docker images**:

   ```bash
   docker-compose -f docker-compose.matomo.yml pull
   docker-compose -f docker-compose.matomo.yml up -d
   ```

2. **Run Matomo updates**: Access the admin interface for automatic updates

## Troubleshooting

### Common Issues

1. **Host mismatch warnings**:
   - Resolved by configuring `trusted_hosts[]` and disabling `enable_trusted_host_check`

2. **SSL/HTTPS issues**:
   - Ensure `assume_secure_protocol=1` and `force_ssl=1` are set
   - Verify nginx proxy headers are configured correctly

3. **Container connectivity**:
   - Check Docker network configuration
   - Verify port mappings in docker-compose.yml

4. **Cache directory permissions error**:
   - **Error**: "Unable to write in the cache directory (/var/www/html/tmp/templates_c/XX)"
   - **Cause**: Incorrect ownership of cache subdirectories
   - **Fix**: Run the following commands:

     ```bash
     # Fix ownership of the entire templates_c directory
     docker-compose -f docker-compose.matomo.yml exec matomo chown -R www-data:www-data /var/www/html/tmp/templates_c/

     # Ensure proper permissions
     docker-compose -f docker-compose.matomo.yml exec matomo chmod -R 755 /var/www/html/tmp/templates_c/
     ```

### Useful Commands

```bash
# Check container status
docker-compose -f docker-compose.matomo.yml ps

# View logs
docker-compose -f docker-compose.matomo.yml logs -f matomo

# Access container shell
docker exec -it matomo_matomo_1 bash

# Test proxy headers
curl -H "Host: homeip.prager.ws" http://localhost:8080/

# Check configuration inside container
docker exec matomo_matomo_1 cat /var/www/html/config/config.ini.php
```

## Security Considerations

- **Database credentials**: Change default credentials in production
- **Salt value**: Keep the salt value secret and unique
- **Proxy IPs**: Consider restricting `proxy_ips[]` to specific IP ranges
- **SSL**: Ensure HTTPS is enforced (handled by nginx proxy)
- **Updates**: Regularly update Matomo and Docker images

## Privacy & GDPR Compliance

Matomo includes built-in privacy features:

- IP anonymization options
- Cookie-less tracking capabilities
- Data retention controls
- User opt-out mechanisms
- GDPR compliance tools

Configure these features through the Matomo admin interface under Privacy settings.

## Support

- **Matomo Documentation**: <https://matomo.org/docs/>
- **Docker Compose Reference**: <https://docs.docker.com/compose/>
- **Project Repository**: SkillSphere/matomo

## Version History

- **Initial Setup**: July 2025 - Docker-based deployment with nginx proxy
- **Host Warning Fix**: July 2025 - Resolved trusted hosts configuration
- **SSL Configuration**: July 2025 - Enabled SSL and proxy headers
- **Enhanced GeoIP**: July 2025 - Configured MaxMind GeoLite2-City database for detailed geolocation

---

**Last updated**: July 2, 2025
