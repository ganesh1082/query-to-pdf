@echo off
echo 🚀 Setting up Deep Research Report Generator Environment
echo =================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected

:: Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

:: Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

:: Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

:: Create .env file if it doesn't exist
if not exist .env (
    echo ⚙️  Creating .env file from template...
    copy .env.example .env
    echo ✅ Created .env file. Please edit it with your API keys:
    echo    - OPENAI_API_KEY
    echo    - FIRECRAWL_API_KEY
) else (
    echo ✅ .env file already exists
)

:: Create assets directory
echo 📁 Creating assets directory...
if not exist assets mkdir assets

echo.
echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Edit the .env file with your API keys:
echo    notepad .env
echo.
echo 2. Activate the virtual environment:
echo    venv\Scripts\activate
echo.
echo 3. Run the report generator:
echo    python index.py
echo.
echo 🎉 Happy researching!
pause 