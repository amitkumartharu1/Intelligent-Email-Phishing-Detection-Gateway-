# Packet Capture – Full Guide for IPEDG Mail

This document explains:
1. What the packet capture feature does in this project
2. Why you were seeing errors
3. Exactly what code was added/changed
4. How to install PyShark and Scapy for full packet capture
5. Step-by-step installation process

---

## 1. What Is Packet Capture in This Project?

The Diagnostics page (`/mail/diagnostics`) has a **"Run Packet Capture"** button.

When clicked it calls `POST /mail/diagnostics/capture` which runs `_do_capture()` inside
`app/blueprints/mail/routes.py`.

The purpose is to **monitor live TCP traffic on MailHog's two ports**:

| Port | Service |
|------|---------|
| 1025 | MailHog SMTP (receives outgoing emails) |
| 8025 | MailHog HTTP API (used to fetch/read emails) |

This lets you see real-time email packet flow between your Flask app and MailHog.

---

## 2. Why Were You Getting Errors?

```
Error: PyShark: No module named 'pyshark'
Error: Scapy: No module named 'scapy'
```

The original code tried to import two optional libraries:

- **PyShark** – a Python wrapper around Wireshark's `tshark.exe` command-line tool
- **Scapy** – a powerful Python packet manipulation library

Both were listed as **comments** in `requirements.txt` (not installed):

```
# scapy>=2.5.0        # pip install scapy
# pyshark>=0.6.0      # pip install pyshark  (requires Wireshark)
```

Since neither was installed, both `import pyshark` and `from scapy.all import sniff`
threw `ModuleNotFoundError`, and the function had no fallback — it just returned an error.

---

## 3. What Code Was Changed

### File: `app/blueprints/mail/routes.py`

The function `_do_capture()` previously had two backends (PyShark → Scapy) and then
returned an error if both failed. A **third fallback** was added using only Python
standard library modules — no external packages required.

#### Before (end of `_do_capture()`):

```python
    except Exception as exc:
        errors.append(f"Scapy: {exc}")

    return {
        "packets": [],
        "interface": iface,
        "method": "none",
        "error": "; ".join(errors) or "Capture failed – Wireshark/TShark not installed or insufficient privileges.",
        "available_interfaces": _list_capture_interfaces(),
    }
```

#### After (new third fallback added before the final return):

```python
    # ── Fallback: pure-Python socket probe (no external libs needed) ─────────
    try:
        import socket as _socket
        import subprocess as _subprocess
        import platform as _platform

        probe_ports = [
            (1025, "SMTP (MailHog)"),
            (8025, "HTTP API (MailHog)"),
        ]
        port_status = []
        for port, desc in probe_ports:
            try:
                s = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
                s.settimeout(1)
                rc = s.connect_ex(("127.0.0.1", port))
                s.close()
                port_status.append({
                    "port": port,
                    "description": desc,
                    "status": "OPEN" if rc == 0 else "CLOSED",
                })
            except Exception:
                port_status.append({"port": port, "description": desc, "status": "UNKNOWN"})

        # Grab active connections to those ports via netstat / ss
        active_conns: list[str] = []
        try:
            if _platform.system() == "Windows":
                out = _subprocess.check_output(
                    ["netstat", "-ano"], timeout=5,
                    stderr=_subprocess.DEVNULL,
                ).decode(errors="ignore")
            else:
                out = _subprocess.check_output(
                    ["ss", "-tnp"], timeout=5,
                    stderr=_subprocess.DEVNULL,
                ).decode(errors="ignore")
            for line in out.splitlines():
                if any(f":{p}" in line or f".{p}" in line for p in ["1025", "8025"]):
                    stripped = line.strip()
                    if stripped:
                        active_conns.append(stripped)
        except Exception:
            pass

        now = datetime.now(timezone.utc).isoformat()
        packets_info = [
            {
                "time": now,
                "length": 0,
                "summary": f"Port {ps['port']} ({ps['description']}): {ps['status']}",
                "source": "socket-probe",
            }
            for ps in port_status
        ]
        for conn in active_conns[:20]:
            packets_info.append({
                "time": now,
                "length": 0,
                "summary": conn,
                "source": "netstat",
            })

        return {
            "packets": packets_info,
            "interface": "localhost (socket probe)",
            "method": "socket-probe",
            "port_status": port_status,
            "active_connections": active_conns,
            "note": (
                "PyShark and Scapy are not installed. "
                "Showing port-probe results and active netstat connections. "
                "Install Wireshark + pyshark for full packet capture."
            ),
            "errors": errors,
        }
    except Exception as exc:
        errors.append(f"Socket probe: {exc}")

    return {
        "packets": [],
        "interface": iface,
        "method": "none",
        "error": "; ".join(errors) or "Capture failed – no capture backend available.",
        "available_interfaces": _list_capture_interfaces(),
    }
```

### How the Three-Level Fallback Works

```
Run Packet Capture clicked
         │
         ▼
  ┌─────────────────────────────────────┐
  │  Level 1: PyShark (TShark/Wireshark) │  ← Full deep packet capture
  │  Filters: tcp.port == 1025 or 8025   │    (requires Wireshark installed)
  └─────────────────────────────────────┘
         │ ImportError / TShark not found
         ▼
  ┌─────────────────────────────────────┐
  │  Level 2: Scapy                      │  ← Raw packet sniffing
  │  Filter: tcp, timeout=5s             │    (requires admin/root)
  └─────────────────────────────────────┘
         │ ImportError
         ▼
  ┌─────────────────────────────────────┐
  │  Level 3: socket + netstat (NEW)     │  ← Port probe (always works)
  │  • Probes ports 1025 & 8025          │    No external packages needed
  │  • Runs netstat -ano (Windows)        │
  │    or ss -tnp (Linux)                │
  └─────────────────────────────────────┘
```

### What Level 3 (Socket Probe) Shows

- **Port 1025 (SMTP):** OPEN = MailHog is running and accepting mail / CLOSED = MailHog is off
- **Port 8025 (HTTP API):** OPEN = MailHog API is available / CLOSED = MailHog is off
- **Active connections:** Any TCP connections currently using those ports (from `netstat`)

---

## 4. How to Install PyShark (Full Packet Capture)

PyShark is a Python wrapper around **Wireshark's TShark** command-line tool.
You must install Wireshark first, then the Python package.

### Step 1 – Install Wireshark

1. Go to: https://www.wireshark.org/download.html
2. Download the **Windows x64 Installer**
3. Run the installer
4. During installation:
   - **Check "Install TShark"** — this is the command-line tool PyShark uses
   - **Check "Install Npcap"** — this is the packet capture driver (required for live capture)
5. When asked about Npcap options, check:
   - "Install Npcap in WinPcap API-compatible Mode"
   - "Support raw 802.11 traffic (requires WinPcap/Npcap)" (optional)
6. Complete installation and **restart your computer**

### Step 2 – Install the pyshark Python Package

Open a terminal in your project directory:

```bash
# Activate your virtual environment first
.venv\Scripts\activate

# Install pyshark
pip install pyshark>=0.6.0
```

### Step 3 – Update requirements.txt

Uncomment the pyshark line in `requirements.txt`:

```
# Change this:
# pyshark>=0.6.0      # pip install pyshark  (requires Wireshark)

# To this:
pyshark>=0.6.0
```

### Step 4 – Verify Installation

```bash
python -c "import pyshark; print('PyShark OK')"
```

If TShark is installed correctly this will print `PyShark OK`.

### Step 5 – Run as Administrator

Live packet capture requires administrator privileges on Windows.

- Right-click your terminal → **"Run as administrator"**
- Then start the Flask app: `python run.py`

> **Note:** Without admin rights you will get a "permission denied" error even with
> Wireshark installed. The socket-probe fallback (Level 3) does NOT require admin.

---

## 5. How to Install Scapy (Alternative)

Scapy is a standalone packet library — it does NOT require Wireshark but still needs
the Npcap driver on Windows.

### Step 1 – Install Npcap (if not already installed with Wireshark)

Download from: https://npcap.com/#download
Run the installer with "WinPcap API-compatible Mode" checked.

### Step 2 – Install Scapy

```bash
# Activate your virtual environment first
.venv\Scripts\activate

# Install scapy
pip install scapy>=2.5.0
```

### Step 3 – Update requirements.txt

```
# Change this:
# scapy>=2.5.0        # pip install scapy

# To this:
scapy>=2.5.0
```

### Step 4 – Verify Installation

```bash
python -c "from scapy.all import sniff; print('Scapy OK')"
```

### Step 5 – Run as Administrator

Same requirement as PyShark — live sniffing needs admin rights on Windows.

---

## 6. Comparison: All Three Backends

| Feature | PyShark (Level 1) | Scapy (Level 2) | Socket Probe (Level 3) |
|---------|-------------------|-----------------|------------------------|
| Shows actual packets | Yes | Yes | No |
| Shows packet content/layers | Yes (deep inspect) | Yes | No |
| Filter by port | Yes (Wireshark filter) | Yes (BPF filter) | Yes (only 1025/8025) |
| Requires Wireshark | Yes | No | No |
| Requires Npcap driver | Yes | Yes | No |
| Requires admin/root | Yes | Yes | No |
| Works without any install | No | No | Yes (always works) |
| Shows if MailHog is running | Yes | Yes | Yes |
| Shows active connections | Yes | Yes | Yes (via netstat) |

---

## 7. Recommended Setup for Full Packet Capture

```
1. Install Wireshark (includes TShark + Npcap)
2. pip install pyshark>=0.6.0
3. Uncomment pyshark in requirements.txt
4. Run Flask app as Administrator
5. Click "Run Packet Capture" on the Diagnostics page
```

Once Wireshark + pyshark are installed and you run as admin, the app will
automatically use **Level 1 (PyShark)** and show real packet-level detail.

---

## 8. Config Settings (.env)

```ini
# Enable/disable the packet capture button on Diagnostics page
ENABLE_CAPTURE=1

# Network interface to capture on
# 'auto' = auto-detect (recommended)
# Or set a specific interface name, e.g. '\Device\NPF_{GUID}' on Windows
CAPTURE_INTERFACE=auto
```

To disable the capture button entirely, set `ENABLE_CAPTURE=0` in `.env`.

---

## 9. Files Changed Summary

| File | What Changed |
|------|-------------|
| `app/blueprints/mail/routes.py` | Added Level 3 socket-probe fallback in `_do_capture()` (lines ~704–790) |
| `requirements.txt` | No change — pyshark/scapy still listed as comments (optional) |

No new files were created for this fix. The fallback uses only Python stdlib:
`socket`, `subprocess`, `platform`, `datetime` — all built into Python.
