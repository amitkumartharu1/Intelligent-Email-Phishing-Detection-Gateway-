# #Intelligent Email Phishing Detection Gateway

A full production-style Gmail-like webmail system with real-time phishing detection,
built as a final-year project. Uses **MailHog** as the local mail server, **Flask** for
the backend, **SQLite** for storage, and a multi-layered phishing detection engine
combining rule-based scoring, ML classification, and Kaggle dataset matching.

---

## Features

| Area | Capability |
|---|---|
| **Webmail** | Register, login, compose, send, receive, read, reply, search, filter |
| **Folders** | Inbox, Sent, Safe Folder, Quarantine, Trash |
| **Scanning** | SPF / DKIM / DMARC, sender mismatch, URL extraction, WHOIS, VirusTotal, social engineering patterns |
| **ML Model** | RandomForest trained on Kaggle phishing CSV — re-trained automatically at startup |
| **Clone Detection** | TF-IDF cosine similarity vs known phishing templates |
| **Dataset Matching** | O(1) lookup against malicious URL / domain / sender / keyword sets |
| **Attachments** | SHA-256 hash, dangerous extension block, CSV content scan, VirusTotal hash lookup |
| **Auto-routing** | High Risk & Critical emails → Quarantine (TTL auto-delete after 30 days) |
| **Reports** | Risk distribution chart, folder stats, top triggered rules, scan history |
| **Diagnostics** | MailHog status, dataset stats, ML model state, optional PyShark capture |
| **Admin** | Dashboard, user management, whitelist/blacklist, audit logs, force rescan |
| **Security** | bcrypt passwords, CSRF protection, secure sessions, safe file uploads |
| **Optional** | VirusTotal API, Nmap port scan, Wireshark/PyShark capture, Scapy fallback |

---

## Project Structure

```
phishing-email-detection-system/
├── run.py                         # Entry-point: python run.py
├── config.py                      # All configuration + scoring weights
├── requirements.txt
├── .env                           # Runtime secrets (do NOT commit)
├── .env.example                   # Template for environment variables
├── .gitignore
│
├── app/
│   ├── __init__.py                # Flask application factory
│   ├── extensions.py              # SQLAlchemy, LoginManager, Bcrypt, CSRF, Scheduler
│   ├── models.py                  # ORM: User, Email, Attachment, ScanResult, etc.
│   │
│   ├── blueprints/
│   │   ├── auth/routes.py         # Register, Login, Logout
│   │   ├── mail/routes.py         # Inbox, Sent, Safe, Quarantine, Compose, Read,
│   │   │                          #   Search, Reports, Diagnostics, Settings
│   │   ├── admin/routes.py        # Dashboard, Users, Lists, Emails, Audit Logs
│   │   └── api/routes.py          # JSON REST API (AJAX, unread count, rescan)
│   │
│   ├── services/
│   │   ├── mailhog.py             # SMTP send + MailHog API fetch + MIME parser
│   │   ├── scanner.py             # Full phishing detection engine (11-step pipeline)
│   │   ├── dataset_loader.py      # Kaggle CSV loader + O(1) lookup sets
│   │   ├── whois_service.py       # Domain age / privacy checks (python-whois)
│   │   ├── virustotal.py          # VirusTotal API v3 (URL scan + hash lookup)
│   │   ├── nmap_service.py        # Nmap port scan + socket fallback
│   │   └── scheduler.py           # APScheduler: fetch emails, auto-delete, reload dataset
│   │
│   ├── templates/
│   │   ├── base.html              # Gmail-like shell (topbar + sidebar + content)
│   │   ├── auth/{login,register}.html
│   │   ├── mail/{inbox,sent,safe,quarantine,compose,read,
│   │   │        search,reports,diagnostics,settings}.html
│   │   └── admin/{dashboard,users,edit_user,emails,whitelist,logs}.html
│   │
│   └── static/
│       ├── css/main.css           # Full Gmail-style responsive stylesheet
│       └── js/{main,compose,inbox}.js
│
├── data/
│   ├── phishing_dataset.csv       # Sample Kaggle-format malicious URL dataset
│   ├── models/                    # Auto-generated ML model files (joblib)
│   └── samples/
│       ├── safe_email.eml
│       ├── phishing_email.eml
│       └── malicious_attachment.csv
│
├── instance/                      # SQLite DB lives here (auto-created)
├── uploads/                       # Attachment files (auto-created)
└── logs/                          # Application logs (auto-created)
```

---

## Quick Start

### 1. Prerequisites

| Tool | Purpose | Install |
|---|---|---|
| **Python 3.10+** | Backend runtime | [python.org](https://www.python.org) |
| **MailHog** | Local SMTP + mail viewer | See below |
| **Nmap** *(optional)* | Network diagnostics | [nmap.org](https://nmap.org) |
| **Wireshark** *(optional)* | Packet capture | [wireshark.org](https://www.wireshark.org) |

### 2. Install MailHog

**Windows (recommended for this project):**
```powershell
# Download MailHog binary from https://github.com/mailhog/MailHog/releases
# Place MailHog.exe somewhere on your PATH, then run:
MailHog.exe
```

**macOS:**
```bash
brew install mailhog
mailhog
```

**Linux:**
```bash
go install github.com/mailhog/MailHog@latest
~/go/bin/MailHog
```

MailHog listens on:
- **SMTP**: `localhost:1025`
- **Web UI / API**: `http://localhost:8025`



### 5. Run the Application

```bash
# Start MailHog first (in a separate terminal)
MailHog.exe     # Windows
# or: mailhog  # macOS/Linux

# Then start the application:
python run.py
```

Open your browser: **http://localhost:5000**

### 6. Default Admin Account

| Field | Value |
|---|---|
| Email | `admin@ipedg.local` |
| Password | `Admin@123` |

---

## Sending Test Emails

### Via the Web UI
1. Log in → click **Compose**
2. Send to any address (e.g. `admin@ipedg.local`)
3. Email goes through MailHog SMTP → fetched back → scanned → appears in Inbox

### Via MailHog Web UI
Open **http://localhost:8025** → use the built-in send feature

### Via Python script
```python
import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg["From"] = "test@example.com"
msg["To"]   = "admin@ipedg.local"
msg["Subject"] = "Test email"
msg.set_content("Hello from test script!")

with smtplib.SMTP("localhost", 1025) as smtp:
    smtp.send_message(msg)
```

### Load sample phishing email
```bash
python -c "
import smtplib
with open('data/samples/phishing_email.eml', 'rb') as f:
    raw = f.read()
with smtplib.SMTP('localhost', 1025) as s:
    s.sendmail('security@paypal-secure-verify.xyz',
               ['admin@ipedg.local'], raw)
print('Sent phishing sample.')
"
```

---

## Phishing Detection Engine

### Pipeline (11 steps)

```
1. SPF / DKIM / DMARC header authentication
2. Sender display-name vs actual address mismatch
3. URL extraction (text + HTML body) & suspicious pattern check
4. VirusTotal URL scan (if API key set)
5. WHOIS domain age & privacy check on sender domain
6. Social engineering pattern matching (20 regex rules)
7. Clone detection (SequenceMatcher vs known phishing templates)
8. Kaggle dataset keyword / sender match
9. Attachment scanning (dangerous ext, CSV content, VT hash)
10. ML model scoring (RandomForest, TF-IDF features)
11. Weighted score aggregation → risk classification
```

### Scoring Weights (configurable in config.py)

| Check | Weight |
|---|---|
| SPF fail | +15 |
| DKIM fail | +10 |
| DMARC fail | +10 |
| Missing subject | +5 |
| Sender mismatch | +20 |
| Clone similarity | +25 |
| Suspicious links | +15 (cap 30) |
| WHOIS new domain | +15 |
| WHOIS hidden | +10 |
| VirusTotal hit | +30 |
| Malicious attachment | +40 |
| Kaggle URL match | +50 |
| Kaggle CSV attachment | +60 → **Critical** |
| Social engineering | +20 |
| ML model | +20 |

### Risk Classification

| Score | Level | Auto-action |
|---|---|---|
| 0 – 25 | **Safe** | → Inbox |
| 26 – 50 | **Medium** | → Inbox (warning shown) |
| 51 – 75 | **High** | → Quarantine |
| 76+ | **Critical** | → Quarantine |

---

## Optional Services

### VirusTotal (free tier)
1. Register at https://www.virustotal.com/gui/join-us
2. Copy your API key to `.env`: `VIRUSTOTAL_API_KEY=your_key`
3. Free tier: 4 requests/minute — the scanner auto-throttles

### Nmap
Install Nmap system-wide, then the Diagnostics page will show live port scan results for sender domains.

### Wireshark / PyShark
1. Install Wireshark (includes `tshark`)
2. Set `ENABLE_CAPTURE=1` and `CAPTURE_INTERFACE=eth0` (or your interface) in `.env`
3. The **Diagnostics** page will have a "Run Packet Capture" button
4. Note: requires admin/root privileges for live capture

---

## API Endpoints (JSON)

| Method | URL | Description |
|---|---|---|
| GET | `/api/v1/emails?folder=inbox` | Paginated email list |
| GET | `/api/v1/emails/<id>` | Single email + scan result |
| PATCH | `/api/v1/emails/<id>/read` | Mark read/unread |
| PATCH | `/api/v1/emails/<id>/star` | Toggle star |
| POST | `/api/v1/emails/<id>/rescan` | Re-run phishing scan |
| GET | `/api/v1/unread_count` | Inbox + quarantine counts |
| POST | `/api/v1/fetch` | Trigger MailHog fetch manually |

All write endpoints require `X-CSRFToken` header.

---

## Database Schema (SQLite)

| Table | Purpose |
|---|---|
| `users` | Accounts (bcrypt passwords, roles) |
| `user_settings` | Per-user preferences |
| `emails` | Full email storage (MIME, risk, folder) |
| `attachments` | Attachment metadata + SHA-256 + file path |
| `extracted_urls` | All URLs found in each email |
| `scan_results` | Per-scan history with triggered rules |
| `list_entries` | Whitelist / blacklist (email, domain, IP) |
| `audit_logs` | All user actions with IP + timestamp |
| `phishing_templates` | Known phishing templates for clone detection |

---

## Security Measures

- **bcrypt** password hashing (cost factor 12)
- **Flask-WTF CSRF** protection on all forms
- **Secure session cookies** (HttpOnly, SameSite=Lax)
- **File upload validation** — extension allow-list + MIME check
- **SHA-256** attachment hashing
- **Access control** — users only see their own emails; admin role required for admin routes
- **Input sanitisation** — all user input goes through WTForms validators
- **SQL injection prevention** — SQLAlchemy ORM parameterised queries
- **XSS protection** — Jinja2 auto-escaping; HTML body rendered in sandboxed iframe context

---

## Running with a Real Kaggle Dataset

1. Download a phishing dataset from Kaggle (e.g. *"Web page Phishing Detection Dataset"* or *"Phishing Site URLs"*)
2. Place the CSV in `data/phishing_dataset.csv`
3. The dataset loader auto-detects common column names (`url`, `domain`, `label`, `type`, etc.)
4. Restart the app — the ML model will auto-retrain on the new data

---

## Troubleshooting

| Problem | Fix |
|---|---|
| "MailHog API unavailable" | Start MailHog before running the app |
| Emails not appearing | Click **Fetch** button or wait 30 seconds for auto-poll |
| ML model not loading | Delete `data/models/` — it will retrain on next start |
| CSRF token error | Clear browser cookies and log in again |
| `ModuleNotFoundError: scapy` | `pip install scapy` or set `ENABLE_CAPTURE=0` |
| `ModuleNotFoundError: pyshark` | `pip install pyshark` and install Wireshark |
| VirusTotal 204 / quota | Free tier is 4 req/min — the scanner throttles automatically |
| SQLite locked error | Ensure only one process runs at a time in development |

---

---

## License

MIT License — free to use and modify for academic and personal projects.

---

*Built for Final Year Project — Phishing Email Detection System*
