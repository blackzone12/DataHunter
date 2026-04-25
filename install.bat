@echo off
echo --------------------------------------------------
echo      🕵️ DataHunter OSINT Installer v4.0
echo --------------------------------------------------
echo ⚠️  IMPORTANT: High-Precision Tracking Requires API Keys!
echo For Real-Time GPS (50m accuracy) ^& HLR Lookups, 
echo ensure you have keys for:
echo - IPQualityScore (HLR)
echo - NumVerify (Identity)
echo - Google Maps (Cell Towers)
echo --------------------------------------------------
echo.
echo � Initializing Config...
if not exist ".env" (
    copy .env.example .env >nul
    echo ✅ Created .env file from template.
)

echo �🔍 Detecting Python...
where python >nul 2>nul
if %errorlevel% == 0 (
    set PY_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% == 0 (
        set PY_CMD=py
    ) else (
        echo ❌ Python not found! Please install it from python.org
        pause
        exit /b 1
    )
)

echo 🛠️ Setting up environment using %PY_CMD%...
if not exist ".venv" (
    echo 📦 Creating Virtual Environment (.venv)...
    %PY_CMD% -m venv .venv
)

echo ⚡ Activating Environment & Installing Dependencies...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Create global shortcuts (Optional: Add to PATH)
if not exist "%USERPROFILE%\.local\bin" mkdir "%USERPROFILE%\.local\bin"
copy main.py "%USERPROFILE%\.local\bin\datahunter.py" /Y
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* > "%USERPROFILE%\.local\bin\datahunter.bat"
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* --type username > "%USERPROFILE%\.local\bin\nuser.bat"
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* --type phone > "%USERPROFILE%\.local\bin\nphone.bat"
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* --type ip > "%USERPROFILE%\.local\bin\nip.bat"
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* --type trace > "%USERPROFILE%\.local\bin\ntrace.bat"
echo @"%~dp0.venv\Scripts\python.exe" "%USERPROFILE%\.local\bin\datahunter.py" %%* --type phone-owner > "%USERPROFILE%\.local\bin\nowner.bat"

:: Create local shortcuts in bin/ folder for a clean root
if not exist "bin" mkdir "bin"
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* > bin\datahunter.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type username > bin\nuser.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type phone > bin\nphone.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type ip > bin\nip.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type trace > bin\ntrace.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type phone-owner > bin\nowner.bat
echo @"%%~dp0..\.venv\Scripts\python.exe" "%%~dp0..\main.py" %%* --type truecaller > bin\ntrue.bat

echo ✅ Installed! All dependencies from requirements.txt are ready.
echo.
echo ⚠️  [IMPORTANT] LIVE PHONE TRACKING SETUP ⚠️
echo To enable 50m Real GPS Accuracy ^& HLR Lookups, set your API keys:
echo setx IPQS_KEY "your_key"
echo setx NUMVERIFY_KEY "your_key"
echo setx GOOGLE_MAPS_KEY "your_key"
echo.
echo 💡 Local Commands: .\bin\nuser, .\bin\nphone, etc.
echo 💡 Global Commands: nuser, nphone (after terminal restart)
