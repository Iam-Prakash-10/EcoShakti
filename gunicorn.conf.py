# Gunicorn configuration for EcoShakti
import multiprocessing

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 1  # Must be 1 for Socket.IO
worker_class = "eventlet"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
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