"""Prometheus metrics."""
from prometheus_client import Counter, Gauge, Histogram
from app.core.config import get_settings

settings = get_settings()

# Chat metrics
chat_requests_total = Counter(
    'chat_requests_total',
    'Total number of chat requests',
    ['session_id']
)

chat_errors_total = Counter(
    'chat_errors_total',
    'Total number of chat errors',
    ['error_type']
)

chat_response_time = Histogram(
    'chat_response_time_seconds',
    'Chat response time in seconds',
    ['session_id']
)

# User metrics
active_users = Gauge('active_users', 'Number of active users')
total_users = Gauge('total_users', 'Total number of users')

# System metrics
system_cpu_load = Gauge('system_cpu_load', 'CPU load average', ['period'])
system_memory_used = Gauge('system_memory_used_bytes', 'Memory used in bytes')
system_memory_total = Gauge('system_memory_total_bytes', 'Total memory in bytes')
system_disk_used = Gauge('system_disk_used_bytes', 'Disk used in bytes')
system_disk_total = Gauge('system_disk_total_bytes', 'Total disk space in bytes')

# Network metrics
network_rx_bytes = Gauge('network_rx_bytes_total', 'Network RX bytes')
network_tx_bytes = Gauge('network_tx_bytes_total', 'Network TX bytes')
network_rx_mbps = Gauge('network_rx_mbps', 'Network RX Mbps')
network_tx_mbps = Gauge('network_tx_mbps', 'Network TX Mbps')
network_connections_total = Gauge('network_connections_total', 'Total network connections')

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint']
)

# Authentication metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['status']  # success, failure
)

auth_failures_total = Counter(
    'auth_failures_total',
    'Total authentication failures',
    ['reason']  # invalid_credentials, expired_token, etc.
)

