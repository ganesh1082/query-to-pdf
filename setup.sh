#!/bin/bash

echo "🚀 Setting up Deep Research Report Generator Environment"
echo "================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "✅ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - FIRECRAWL_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Create assets directory
echo "📁 Creating assets directory..."
mkdir -p assets

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "3. Run the report generator:"
echo "   python index.py"
echo ""
echo "🎉 Happy researching!" 