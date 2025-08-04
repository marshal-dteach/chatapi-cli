#!/bin/bash

# ChatAPI CLI Installation Script

echo "🚀 Installing ChatAPI CLI Tool..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python version $python_version is too old. Please install Python 3.7+."
    exit 1
fi

echo "✅ Python $python_version detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make the script executable
chmod +x chatapi_cli.py

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📝 Next steps:"
echo "1. Set your API keys:"
echo "   # For OpenAI:"
echo "   export OPENAI_API_KEY='your-openai-api-key-here'"
echo "   OR"
echo "   python3 chatapi_cli.py config set openai_api_key 'your-openai-api-key-here'"
echo ""
echo "   # For Perplexity:"
echo "   export PERPLEXITY_API_KEY='your-perplexity-api-key-here'"
echo "   OR"
echo "   python3 chatapi_cli.py config set perplexity_api_key 'your-perplexity-api-key-here'"
echo ""
echo "2. Switch providers (optional):"
echo "   python3 chatapi_cli.py provider set openai    # Use OpenAI"
echo "   python3 chatapi_cli.py provider set perplexity  # Use Perplexity"
echo ""
echo "3. Start chatting:"
echo "   python3 chatapi_cli.py chat"
echo ""
echo "4. For help:"
echo "   python3 chatapi_cli.py --help"
echo ""
echo "Happy chatting! 🚀" 