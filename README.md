# 🕵️ DataHunter OSINT Framework v4.0

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/badge/version-4.0.0--stable-red.svg)

DataHunter is a powerful, multi-threaded OSINT tool designed for rapid reconnaissance across social media, phone intelligence, and global IP networks. It aggregates data from 100+ platforms and uses advanced HLR/Cell-Triangulation for high-precision tracking.

### ⚙️ Configuration (.env)
DataHunter now uses a `.env` file for secure API key management. Open the `.env` file in the root directory and add your keys:

```bash
# --- Enhanced Intel Keys ---
IPQS_KEY="your_ipqualityscore_key"   # For HLR & Risk
GOOGLE_MAPS_KEY="your_google_key"    # For GPS Mapping
NUMVERIFY_KEY="your_numverify_key"   # For Fallback
IPINFO_TOKEN="your_ipinfo_token"     # For IP Intel
```

---

## 🚀 Features

- **👤 Username Recon**: Search 100+ global platforms (GitHub, Instagram, Twitter, etc.) simultaneously.
- **📱 Phone Tracker Pro**: 
  - Real-time HLR lookups for carrier & country status.
  - Cell Tower Triangulation (accurate within 50m-500m).
  - Interactive Map generation via Folium.
- **🌍 Multi-Source IP Intel**:
  - Queries 7+ independent APIs concurrently.
  - Datacenter, VPN, and Proxy detection.
  - Hop-by-hop Traceroute mapping.
- **📊 Automated Reporting**: Every search creates a structured JSON report and a visual HTML map.

---

## 🛠️ Installation

### Windows
```powershell
# Clone the repository and run:
.\install.bat
```

### Linux / Termux (Android)
```bash
# For Termux, just run:
pkg install git -y
git clone <repository_url>
cd SPY
pkg install python -y
bash install.sh
```

---

## 🔑 API Configuration (Optional but Recommended)

For **Real-Time GPS Tracking** and **Identity Lookups**, you need to set your API keys as environment variables:

| Service | Feature | Key Source |
| :--- | :--- | :--- |
| **IPQualityScore** | HLR / SIM Status | [ipqualityscore.com](https://www.ipqualityscore.com/) |
| **NumVerify** | Caller Identification | [numverify.com](https://numverify.com/) |
| **Google Maps** | Cell Triangulation | [cloud.google.com/maps](https://cloud.google.com/) |

### Setting Keys:
**Windows:**
```powershell
setx IPQS_KEY "your_key"
setx NUMVERIFY_KEY "your_key"
setx GOOGLE_MAPS_KEY "your_key"
```
**Linux:**
```bash
export IPQS_KEY="your_key"
export NUMVERIFY_KEY="your_key"
export GOOGLE_MAPS_KEY="your_key"
```

---

## 📖 Quick Start Commands

Once installed, use these shortcuts from the `bin/` folder (or globally after restart):

| Command | Usage | Description |
| :--- | :--- | :--- |
| `nuser` | `.\bin\nuser "username"` | Global social media search |
| `nphone` | `.\bin\nphone "+91..."` | Live phone tracker & HLR |
| `nip` | `.\bin\nip "8.8.8.8"` | Multi-API IP Geolocation |
| `ntrace` | `.\bin\ntrace "8.8.8.8"` | Network path tracking & mapping |
| `nowner` | `.\bin\nowner "+91..."` | Detailed phone owner lookup (Name/Address) |

**Private IP Adress can't be tracked only Public IP Adress can be tracked**
---

## 📁 Project Structure
```text
DataHunter/
├── bin/            # Command shortcuts (Global access)
├── modules/        # Intelligence core & site databases
├── results/        # JSON Reports & HTML Maps
├── install.bat     # Windows Automated Installer
├── install.sh      # Linux/Termux Automated Installer
└── main.py         # Entry point
```

---

## ⚠️ Disclaimer
This tool is for authorized security research and educational purposes only. Users are responsible for complying with local laws and platform Terms of Service.

"Created by Black Zone"
