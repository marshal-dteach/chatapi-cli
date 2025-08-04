# Quick Start Guide

Get up and running with ChatAPI CLI in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Your API Keys

**Option A: Environment Variables (Recommended)**
```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# For Perplexity
export PERPLEXITY_API_KEY="your-perplexity-api-key-here"
```

**Option B: Using the CLI**
```bash
# Set OpenAI API key
python chatapi_cli.py config set openai_api_key "your-openai-api-key-here"

# Set Perplexity API key
python chatapi_cli.py config set perplexity_api_key "your-perplexity-api-key-here"
```

## Step 3: Start Chatting!

**Interactive Mode:**
```bash
./chatapi_cli.py chat
# or
python chatapi_cli.py chat
```

**Single Message:**
```bash
./chatapi_cli.py chat "What is the capital of France?"
# or
python chatapi_cli.py chat "What is the capital of France?"
```

## That's it! 🎉

You're now ready to use ChatAPI CLI from your terminal!

### Quick Commands

- `./chatapi_cli.py --help` - Show all commands
- `./chatapi_cli.py config show` - View current settings
- `./chatapi_cli.py history` - View chat history
- `./chatapi_cli.py clear` - Clear chat history
- `./chatapi_cli.py provider show` - Show current provider
- `./chatapi_cli.py provider set openai` - Switch to OpenAI
- `./chatapi_cli.py provider set perplexity` - Switch to Perplexity
- `python chatapi_cli.py --help` - Show all commands (alternative)
- `python chatapi_cli.py config show` - View current settings (alternative)
- `python chatapi_cli.py history` - View chat history (alternative)
- `python chatapi_cli.py clear` - Clear chat history (alternative)

### Interactive Mode Commands

When in interactive mode, you can use:
- `help` - Show available commands
- `quit` / `exit` / `q` - Exit
- `clear` - Clear history
- `history` - Show history
- `config` - Show configuration
- `provider show` - Show current provider
- `provider set <provider>` - Switch providers

### Need Help?

- Check the full [README.md](README.md) for detailed documentation
- Run `./chatapi_cli.py --help` for command help
- Make sure your API keys are valid and have credits

Happy chatting! 🚀 