#!/bin/bash
echo "--------------------------------------------------"
echo "     🕵️ DataHunter OSINT Installer v4.0"
echo "--------------------------------------------------"
echo -e "\033[1;33m⚠️  IMPORTANT: High-Precision Tracking Requires API Keys!\033[0m"
echo "For Real-Time GPS (50m accuracy) & HLR Lookups,"
echo "ensure you have keys for:"
echo " - IPQualityScore (HLR)"
echo " - NumVerify (Identity)"
echo " - Google Maps (Cell Towers)"
echo "--------------------------------------------------"
echo ""
echo -e "🚀 Setting up DataHunter environment..."

# Initialize .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "✅ Created .env from template."
fi

# Termux / Android Detection
if [ -d "/data/data/com.termux/files/home" ]; then
    echo "📱 Termux detected! Installing system dependencies..."
    pkg update && pkg upgrade -y
    pkg install python libxml2 libxslt python-venv -y
else
    # Linux dependency check
    if ! command -v python3-venv &> /dev/null; then
        echo "📦 Installing python3-venv..."
        sudo apt update && sudo apt install python3-venv -y
    fi
fi

# Create Virtual Environment
if [ ! -d ".venv" ]; then
    echo -e "📦 Creating Virtual Environment (.venv)..."
    python3 -m venv .venv || { echo "❌ Failed to create venv. Try: sudo apt install python3-venv"; exit 1; }
fi

echo -e "⚡ Activating Environment & Installing Dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Local installation logic
mkdir -p ~/.local/bin
cp main.py ~/.local/bin/datahunter.py
chmod +x ~/.local/bin/datahunter.py

# Create global wrappers that use the .venv
VENV_PATH=$(pwd)/.venv/bin/python3
SCRIPT_PATH=~/.local/bin/datahunter.py

echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type username" > ~/.local/bin/nuser
echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type phone" > ~/.local/bin/nphone
echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type ip" > ~/.local/bin/nip
echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type trace" > ~/.local/bin/ntrace
echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type phone-owner" > ~/.local/bin/nowner
echo -e "#!/bin/bash\n$VENV_PATH $SCRIPT_PATH \"\$@\" --type truecaller" > ~/.local/bin/ntrue

chmod +x ~/.local/bin/nuser ~/.local/bin/nphone ~/.local/bin/nip ~/.local/bin/ntrace ~/.local/bin/nowner ~/.local/bin/ntrue

# Create local shortcuts in bin folder
mkdir -p bin
VENV_LOCAL=$(pwd)/.venv/bin/python3
MAIN_LOCAL=$(pwd)/main.py

echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type username" > bin/nuser
echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type phone" > bin/nphone
echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type ip" > bin/nip
echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type trace" > bin/ntrace
echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type phone-owner" > bin/nowner
echo -e "#!/bin/bash\n$VENV_LOCAL $MAIN_LOCAL \"\$@\" --type truecaller" > bin/ntrue

chmod +x bin/nuser bin/nphone bin/nip bin/ntrace bin/nowner bin/ntrue

echo -e "✅ Installed! All dependencies from requirements.txt are ready."
echo -e "\n\033[1;33m⚠️  [IMPORTANT] LIVE PHONE TRACKING SETUP ⚠️\033[0m"
echo -e "To enable 50m Real GPS Accuracy & HLR Lookups, export your API keys:"
echo -e "export IPQS_KEY='your_key'"
echo -e "export NUMVERIFY_KEY='your_key'"
echo -e "export GOOGLE_MAPS_KEY='your_key'"
echo -e "\n💡 Usage: ./nuser, ./nphone, etc."
