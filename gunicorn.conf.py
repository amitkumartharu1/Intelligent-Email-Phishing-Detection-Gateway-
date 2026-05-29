"""
gunicorn.conf.py — Production Gunicorn configuration for IPEDG.

Run:
    gunicorn --config gunicorn.conf.py "run:app"

References:
    Twelve-Factor App (Factor XI — Logs): stdout logging, no file handles
    OWASP: worker count tuned to (2 × CPU) + 1 for CPU-bound ML workloads
"""
import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────────────
bind = os.environ.get("GUNICORN_BIND", "0.0.0.0:5000")

# ── Workers ───────────────────────────────────────────────────────────────────
# (2 × CPU) + 1 is the standard formula; ML inference is CPU-heavy
workers = int(os.environ.get("GUNICORN_WORKERS",
                             (2 * multiprocessing.cpu_count()) + 1))
worker_class = "sync"          # ML inference is not I/O-bound → sync workers
threads = 1                    # one thread per sync worker

# ── Timeouts ─────────────────────────────────────────────────────────────────
timeout = 120          # allow 2 min for heavy ML + API calls
graceful_timeout = 30  # wait 30 s for in-flight requests on SIGTERM
keepalive = 5

# ── Logging (Twelve-Factor stdout) ───────────────────────────────────────────
accesslog = "-"       # → stdout
errorlog  = "-"       # → stderr
loglevel  = os.environ.get("GUNICORN_LOG_LEVEL", "info")
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" '
    '"%(a)s" %(D)sμs'
)

# ── Process name ─────────────────────────────────────────────────────────────
proc_name = "ipedg"

# ── Security ─────────────────────────────────────────────────────────────────
# Reload workers after N requests to prevent memory leaks from large ML models
max_requests = 1000
max_requests_jitter = 100   # randomise so workers don't all restart at once

# Preload the app before forking workers (saves memory via copy-on-write)
preload_app = True
