#!/bin/bash
# Setup script for Secure Personal Agentic Platform

echo "🚀 Setting up Secure Personal Agentic Platform..."

# 1. Create Python virtual environment
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
echo "2. In Terminal Tab 1: ollama serve"
echo "3. In Terminal Tab 2: ollama pull llama3 && ollama pull mistral"
echo "4. In Terminal Tab 3: source venv/bin/activate && PYTHONPATH=. python3 core/main.py"
echo "5. In Terminal Tab 4: cd frontend && npm run dev"
