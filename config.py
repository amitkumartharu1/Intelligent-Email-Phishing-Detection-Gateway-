"""
config.py – Application configuration for Intelligent Phishing Email Detection and Response System

"""
import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    # ── Flask core ────────────────────────────────────────────────────────────
    # SECURITY: No hardcoded fallback key. The app/__init__.py factory will
    # raise RuntimeError at startup if SECRET_KEY is missing from .env.
    # Generate: python -c "import secrets; print(secrets.token_hex(32))"
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "development")

    # ── Rate limiting (Flask-Limiter) ─────────────────────────────────────────
    # Default: in-memory store. Set RATELIMIT_STORAGE_URI=redis://localhost:6379/1
    # in .env to use Redis for distributed deployments.
    RATELIMIT_STORAGE_URI: str = os.environ.get(
        "RATELIMIT_STORAGE_URI", "memory://"
    )
    RATELIMIT_DEFAULT: str = os.environ.get("RATELIMIT_DEFAULT", "200 per minute")
    RATELIMIT_HEADERS_ENABLED = True    # adds X-RateLimit-* headers to responses

    # ── Caching (Flask-Caching) ───────────────────────────────────────────────
    # SimpleCache is used in dev/test; switch to "redis" + CACHE_REDIS_URL in prod.
    CACHE_TYPE: str = os.environ.get("CACHE_TYPE", "SimpleCache")
    CACHE_DEFAULT_TIMEOUT: int = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 300))
    CACHE_REDIS_URL: str = os.environ.get("CACHE_REDIS_URL", "redis://localhost:6379/0")

    # ── Database ──────────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'phishing_email_detection.db'}",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session / CSRF ────────────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"
    WTF_CSRF_ENABLED = os.environ.get("WTF_CSRF_ENABLED", "1") == "1"
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # ── File uploads ──────────────────────────────────────────────────────────
    MAX_CONTENT_LENGTH = int(os.environ.get("MAX_CONTENT_LENGTH_MB", 16)) * 1024 * 1024
    UPLOAD_FOLDER: Path = BASE_DIR / "uploads"

    # ── MailHog ───────────────────────────────────────────────────────────────
    MAILHOG_SMTP_HOST: str = os.environ.get("MAILHOG_SMTP_HOST", "localhost")
    MAILHOG_SMTP_PORT: int = int(os.environ.get("MAILHOG_SMTP_PORT", 1025))
    MAILHOG_API_HOST: str = os.environ.get("MAILHOG_API_HOST", "localhost")
    MAILHOG_API_PORT: int = int(os.environ.get("MAILHOG_API_PORT", 8025))

    # ── Mail domain ───────────────────────────────────────────────────────────
    MAIL_DOMAIN: str = os.environ.get("MAIL_DOMAIN", "ipedg.local")

    # ── Threat Intelligence API Keys ─────────────────────────────────────────

    # VirusTotal [25] – URL/domain/IP/file hash reputation
    VIRUSTOTAL_API_KEY: str = os.environ.get("VIRUSTOTAL_API_KEY", "")

    # Google Safe Browsing [26] – phishing/malware URL classification
    GOOGLE_SAFE_BROWSING_API_KEY: str = os.environ.get("GOOGLE_SAFE_BROWSING_API_KEY", "")

    # AbuseIPDB – IP abuse reputation scoring
    ABUSEIPDB_API_KEY: str = os.environ.get("ABUSEIPDB_API_KEY", "")

    # urlscan.io – URL/page content analysis
    URLSCAN_API_KEY: str = os.environ.get("URLSCAN_API_KEY", "")

    # AlienVault OTX – Indicators of Compromise (IOC) enrichment
    ALIENVAULT_OTX_API_KEY: str = os.environ.get("ALIENVAULT_OTX_API_KEY", "")

   
    # ── Detection engine config ───────────────────────────────────────────────
    # ML contributes ≤15 pts as a secondary signal when phishing probability > 0.55.
    ML_ENABLED_IN_VERDICT: bool = True

    # ── Nmap ──────────────────────────────────────────────────────────────────
    NMAP_PATH: str = os.environ.get("NMAP_PATH", "nmap")

    # ── PyShark / Wireshark ───────────────────────────────────────────────────
    ENABLE_CAPTURE: bool = os.environ.get("ENABLE_CAPTURE", "1") == "1"
    CAPTURE_INTERFACE: str = os.environ.get("CAPTURE_INTERFACE", "eth0")

    # ── Scheduler ─────────────────────────────────────────────────────────────
    FETCH_INTERVAL_SECONDS: int = int(os.environ.get("FETCH_INTERVAL_SECONDS", 30))
    QUARANTINE_TTL_DAYS: int = int(os.environ.get("QUARANTINE_TTL_DAYS", 30))
    SCHEDULER_API_ENABLED = False

    # ── Kaggle dataset (used for rule-engine lookup sets) ────────────────────
    PHISHING_DATASET_PATH: Path = BASE_DIR / os.environ.get(
        "PHISHING_DATASET_PATH", "data/phishing_dataset.csv"
    )
    PHISHING_SUPPLEMENTARY_DATASET: Optional[Path] = (
        BASE_DIR / os.environ.get("PHISHING_SUPPLEMENTARY_DATASET", "data/CEAS_08.csv")
        if os.environ.get("PHISHING_SUPPLEMENTARY_DATASET") else None
    )

    # ── ML training dataset (separate from rule-engine lookup set) ────────────
    PHISHING_ML_TRAINING_PATH: Path = BASE_DIR / os.environ.get(
        "PHISHING_ML_TRAINING_PATH", "data/phishing_email.csv"
    )

    # ── Admin bootstrap ───────────────────────────────────────────────────────
    # FIX V01: No hardcoded admin password. Set ADMIN_EMAIL + ADMIN_PASSWORD in .env.
    ADMIN_EMAIL: str = os.environ.get("ADMIN_EMAIL", "admin@ipedg.local")
    ADMIN_PASSWORD: str = os.environ.get("ADMIN_PASSWORD", "")

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_DIR: Path = BASE_DIR / "logs"


    SCORE_WEIGHTS = {
        # ── Dataset matching (highest-priority deterministic signals) ──────────
        "dataset_url_exact":    35,   # exact URL in phishing DB
        "dataset_domain_exact": 25,   # exact domain in phishing DB
        "dataset_subject_fuzzy": 20,  # fuzzy subject similarity ≥ 0.72
        "dataset_body_overlap":  10,  # keyword overlap with phishing texts
        "blacklist_hit":         15,  # exact sender in phishing DB

        # ── Header authentication (spoofing indicators, not phishing proof) ────
        "spf_fail":              8,   # reduced: auth fail alone ≠ phishing
        "dkim_fail":             6,
        "dmarc_fail":           10,   # higher: DMARC is more authoritative
        "reply_to_mismatch":     7,
        "domain_alignment_fail": 15,  # new: From/Reply-To/Return-Path mismatch

        # ── Sender identity ───────────────────────────────────────────────────
        "sender_mismatch":      12,   # display-name vs envelope spoofing

        # ── URL intelligence ──────────────────────────────────────────────────
        "suspicious_links":      8,   # pattern match (reduced; patterns alone are noisy)
        "virustotal_url_hit":   25,   # VT hit → high-confidence malicious URL

        # ── Content signals ───────────────────────────────────────────────────
        "social_engineering":   10,
        "missing_subject":       3,
        "html_only":             3,

        # ── Attachment intelligence ───────────────────────────────────────────
        "malicious_attachment":  25,  # dangerous ext or VT hash detection
        "kaggle_csv_attachment": 20,  # CSV attachment with phishing DB entries

        # ── Similarity matching ───────────────────────────────────────────────
        "clone_similarity":     18,
        "eml_similarity":       12,

        # ── WHOIS domain checks ───────────────────────────────────────────────
        "whois_new_domain":      8,
        "whois_hidden":          5,

        # ── ML model (secondary signal – Logistic Regression + TF-IDF) ───────
        "ml_model":             20,   # proportional; ML alone cannot quarantine
    }

    # ── Deterministic override thresholds ─────────────────────────────────────
    
    OVERRIDE_THRESHOLDS = {
        "malicious_attachment_score": 88,
        "malicious_url_score":        82,
        "dataset_exact_match_score":  92,
        "dataset_fuzzy_match_score":  78,
        "auth_spoofing_score":        76,
        "strong_similarity_score":    74,
    }

    # ── Risk thresholds (final score is 0–100) ────────────────────────────────
    # 0–29  → safe        (route to Inbox / Safe folder)
    # 30–59 → suspicious  (flag in Inbox for review)
    # 60–79 → high        (auto-quarantine)
    # 80+   → critical    (auto-quarantine, high-priority alert)
    RISK_THRESHOLDS = {
        "safe":       29,
        "suspicious": 59,
        "high":       79,
    }


class DevelopmentConfig(Config):
    DEBUG = True
    # Development provides a safe fallback key so the app starts without .env.
    # Production still requires SECRET_KEY in the environment (see ProductionConfig).
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY",
        "dev-only-insecure-key-NEVER-use-in-production-abc123",
    )
    CACHE_TYPE = "SimpleCache"          # no Redis required in dev


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = "Strict"

    def __init__(self) -> None:
        # OWASP A02 [37]: fail-fast if SECRET_KEY is not set in production.
        if not os.environ.get("SECRET_KEY"):
            raise ValueError(
                "SECRET_KEY environment variable must be set in production. "
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config() -> Config:
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)
