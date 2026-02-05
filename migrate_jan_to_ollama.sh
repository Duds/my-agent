#!/bin/bash
# Migration script: Import Jan.ai models into Ollama (Fixed)

JAN_MODELS_DIR="$HOME/Library/Application Support/jan/data/llamacpp/models"

echo "🔄 Migrating Jan.ai models to Ollama..."

# 1. CodeLlama
echo "📦 Importing codellama-7b-instruct..."
cat > /tmp/Modelfile.codellama << EOF
FROM $JAN_MODELS_DIR/codellama-7b-instruct.Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF
ollama create codellama-instruct -f /tmp/Modelfile.codellama

# 2. Llama 3.2 3B
echo "📦 Importing llama3.2-3b-instruct..."
cat > /tmp/Modelfile.llama32 << EOF
FROM $JAN_MODELS_DIR/Llama-3.2-3B-Instruct-Q4_K_M.gguf
PARAMETER temperature 0.7
EOF
ollama create llama32-instruct -f /tmp/Modelfile.llama32

# 3. Mistral 7B Instruct
echo "📦 Importing mistral-7b-instruct..."
cat > /tmp/Modelfile.mistral << EOF
FROM $JAN_MODELS_DIR/mistral-7b-instruct-v0.1.Q4_K_M.gguf
PARAMETER temperature 0.7
EOF
ollama create mistral-instruct -f /tmp/Modelfile.mistral

# 4. Roleplay Hermes (for NSFW/Private)
echo "📦 Importing roleplay-hermes-3..."
cat > /tmp/Modelfile.hermes << EOF
FROM $JAN_MODELS_DIR/roleplay-hermes-3-llama-3.1-8b-q4_k_m/Roleplay-Hermes-3-Llama-3.1-8B.Q4_K_M.gguf
PARAMETER temperature 0.8
PARAMETER top_p 0.95
EOF
ollama create hermes-roleplay -f /tmp/Modelfile.hermes

# 5. DeepSeek Coder
echo "📦 Importing deepseek-coder..."
cat > /tmp/Modelfile.deepseek << EOF
FROM $JAN_MODELS_DIR/deepseek-coder-6.7b-instruct-q4_k_m.gguf
PARAMETER temperature 0.3
EOF
ollama create deepseek-coder -f /tmp/Modelfile.deepseek

# 6. Vicuna
echo "📦 Importing vicuna-7b..."
cat > /tmp/Modelfile.vicuna << EOF
FROM $JAN_MODELS_DIR/vicuna-7b-v1.5.Q4_K_M.gguf
PARAMETER temperature 0.7
EOF
ollama create vicuna -f /tmp/Modelfile.vicuna

echo ""
echo "✅ Migration complete! Listing Ollama models:"
ollama list

echo ""
echo "📝 Next steps:"
echo "   1. Verify models above"
echo "   2. Delete Jan.ai: rm -rf ~/Library/Application\ Support/jan"
echo "   3. Delete Jan.app: rm -rf /Applications/Jan.app"
