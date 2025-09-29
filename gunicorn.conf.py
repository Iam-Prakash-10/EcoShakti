# Gunicorn configuration for EcoShakti
import multiprocessing
import os

# Server socket - Use PORT environment variable for cloud deployment
port = os.environ.get('PORT', '5000')
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Use sync worker to avoid eventlet issues
workers = 1
worker_class = "gevent"  # Use gevent instead of eventlet for better compatibility
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
# Create logs directory if it doesn't exist
try:
    import os
    if not os.path.exists('logs'):
        os.makedirs('logs')
except:
    pass

accesslog = "-"  # Log to stdout for cloud platforms
errorlog = "-"   # Log to stderr for cloud platforms
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'ecoshakti'

# Daemon mode
daemon = False
pidfile = 'ecoshakti.pid'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190