# EcoShakti Deployment Guide

This guide provides multiple options to deploy your EcoShakti renewable energy monitoring system.

## 🚀 Quick Start (Local Production)

### Option 1: Windows Production Setup

1. **Run the deployment script:**
   ```bash
   # Simply double-click deploy.bat or run:
   .\deploy.bat
   ```

2. **Manual setup (if you prefer):**
   ```bash
   # Create virtual environment
   python -m venv venv
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn eventlet
   
   # Set environment variables
   set FLASK_ENV=production
   
   # Start with Gunicorn
   gunicorn --config gunicorn.conf.py app:app
   ```

3. **Access your application:**
   - Open: http://localhost:5000

## ☁️ Cloud Deployment

### Option 1: Heroku (Easiest)

1. **Install Heroku CLI** from https://devcenter.heroku.com/articles/heroku-cli

2. **Deploy to Heroku:**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create new app
   heroku create your-ecoshakti-app
   
   # Set environment variables
   heroku config:set FLASK_SECRET_KEY=your_secret_key_here
   heroku config:set FLASK_ENV=production
   
   # Deploy
   git init
   git add .
   git commit -m "Initial EcoShakti deployment"
   git push heroku main
   ```

3. **Access your app:**
   - URL: https://your-ecoshakti-app.herokuapp.com

### Option 2: Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   # Login to Railway
   railway login
   
   # Initialize project
   railway init
   
   # Set environment variables
   railway variables set FLASK_SECRET_KEY=your_secret_key_here
   railway variables set FLASK_ENV=production
   
   # Deploy
   railway up
   ```

### Option 3: Render

1. **Create account** at https://render.com
2. **Connect your GitHub repository**
3. **Create new Web Service:**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 app:app`
   - Environment Variables:
     - `FLASK_SECRET_KEY`: your_secret_key_here
     - `FLASK_ENV`: production

## 🐳 Docker Deployment

### Local Docker Setup

1. **Build and run with Docker Compose:**
   ```bash
   # Build and start
   docker-compose up -d
   
   # View logs
   docker-compose logs -f
   
   # Stop
   docker-compose down
   ```

2. **Access application:**
   - URL: http://localhost:5000

### Production Docker

1. **Build image:**
   ```bash
   docker build -t ecoshakti .
   ```

2. **Run container:**
   ```bash
   docker run -d \
     --name ecoshakti-app \
     -p 5000:5000 \
     -e FLASK_SECRET_KEY=your_secret_key_here \
     -e FLASK_ENV=production \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/logs:/app/logs \
     ecoshakti
   ```

## 🖥️ VPS/Server Deployment

### Complete Server Setup (Ubuntu/Debian)

1. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv nginx git
   ```

2. **Clone and setup application:**
   ```bash
   # Clone your repository
   git clone <your-repo-url> /var/www/ecoshakti
   cd /var/www/ecoshakti
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn eventlet
   ```

3. **Create system service:**
   ```bash
   sudo nano /etc/systemd/system/ecoshakti.service
   ```
   
   Add this content:
   ```ini
   [Unit]
   Description=EcoShakti Renewable Energy Monitor
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/ecoshakti
   Environment="PATH=/var/www/ecoshakti/venv/bin"
   ExecStart=/var/www/ecoshakti/venv/bin/gunicorn --worker-class eventlet -w 1 --bind 127.0.0.1:5000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Setup Nginx:**
   ```bash
   # Copy Nginx configuration
   sudo cp ecoshakti.nginx.conf /etc/nginx/sites-available/ecoshakti
   sudo ln -s /etc/nginx/sites-available/ecoshakti /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default
   
   # Test and restart Nginx
   sudo nginx -t
   sudo systemctl restart nginx
   ```

5. **Start services:**
   ```bash
   # Start and enable EcoShakti service
   sudo systemctl start ecoshakti
   sudo systemctl enable ecoshakti
   
   # Check status
   sudo systemctl status ecoshakti
   ```

6. **Setup SSL (Optional but recommended):**
   ```bash
   # Install Certbot
   sudo apt install certbot python3-certbot-nginx
   
   # Get SSL certificate
   sudo certbot --nginx -d your-domain.com
   ```

## 🔧 Environment Configuration

### Required Environment Variables

Create a `.env` file with these variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your_very_secure_secret_key_here
FLASK_ENV=production
FLASK_DEBUG=0

# Database (if using SQLite)
DATABASE_URL=sqlite:///energy_monitor.db

# ML Models
ML_MODEL_PATH=./ml_models

# Optional: Custom Port
PORT=5000
```

### Security Considerations

1. **Change default secret key**
2. **Use HTTPS in production**
3. **Set up firewall rules**
4. **Regular security updates**
5. **Monitor application logs**

## 📊 Monitoring & Maintenance

### Application Monitoring

1. **Health Check Endpoint:**
   - URL: `/api/health`
   - Returns system status and metrics

2. **Log Files:**
   - Application logs: `logs/error.log`
   - Access logs: `logs/access.log`
   - Nginx logs: `/var/log/nginx/`

3. **System Commands:**
   ```bash
   # Check application status
   sudo systemctl status ecoshakti
   
   # View application logs
   sudo journalctl -u ecoshakti -f
   
   # Restart application
   sudo systemctl restart ecoshakti
   ```

### Backup Strategy

1. **User Data:** Backup `users.json` file
2. **Alert Data:** Backup `alerts.json` file
3. **Configuration:** Backup `.env` file
4. **Application Code:** Keep in version control

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill process if needed
   kill -9 <PID>
   ```

2. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R www-data:www-data /var/www/ecoshakti
   ```

3. **SSL certificate issues:**
   ```bash
   # Renew certificate
   sudo certbot renew
   ```

4. **Application won't start:**
   ```bash
   # Check logs for errors
   sudo journalctl -u ecoshakti --no-pager
   ```

## 📞 Support

For deployment issues:
1. Check application logs
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Check firewall and port settings

Your EcoShakti renewable energy monitoring system should now be successfully deployed! 🌱⚡