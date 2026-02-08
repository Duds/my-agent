#!/bin/bash
# Setup script for Secure Personal Agentic Platform

echo "🚀 Setting up Secure Personal Agentic Platform..."

# 1. Create Python virtual environment (venv/ inside project)
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 2. Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# 3. Check for Ollama
echo "🔍 Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Installing via Homebrew..."
    brew install ollama
else
    echo "✅ Ollama is already installed"
fi

# 4. Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Run ./manage.sh start  (or manually: ollama serve, then source venv/bin/activate && PYTHONPATH=. python3 -m core.main, then cd frontend && npm run dev)"
