# ChatAPI CLI Tool

A powerful command-line interface for interacting with OpenAI's ChatGPT API and Perplexity API. Features an interactive chat mode, conversation history, configuration management, and beautiful output formatting with support for multiple AI providers.

## Features

- 🚀 **Interactive Chat Mode** - Start a conversation session with ChatGPT or Perplexity
- 💬 **Single Message Mode** - Send one-off messages directly from command line
- 📝 **Conversation History** - Automatically saves and loads conversation history
- ⚙️ **Configuration Management** - Easy setup and customization of settings
- 🎨 **Rich Output** - Beautiful formatting with markdown support and syntax highlighting
- 🔧 **Command Completion** - Tab completion for commands in interactive mode
- 📊 **Token Usage** - Optional display of token usage for each request
- 🗂️ **History Management** - View and clear conversation history
- 🔄 **Multi-Provider Support** - Switch between OpenAI and Perplexity APIs

## Installation

1. **Clone or download the project:**
   ```bash
   git clone <repository-url>
   cd chatapi-cli
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API keys:**
   
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

## Usage

### Interactive Chat Mode

Start an interactive chat session:

```bash
./chatapi_cli.py chat
# or
python chatapi_cli.py chat
```

In interactive mode, you can:
- Type your message and press Enter to chat
- Use commands like `help`, `clear`, `history`, `config`
- Type `quit`, `exit`, or `q` to exit

### Single Message Mode

Send a single message and get a response:

```bash
./chatapi_cli.py chat "What is the capital of France?"
# or
python chatapi_cli.py chat "What is the capital of France?"
```

### Configuration Management

**Show current configuration:**
```bash
./chatapi_cli.py config show
# or
python chatapi_cli.py config show
```

**Set configuration values:**
```bash
./chatapi_cli.py config set model gpt-4
./chatapi_cli.py config set temperature 0.8
./chatapi_cli.py config set max_tokens 2000
# or
python chatapi_cli.py config set model gpt-4
python chatapi_cli.py config set temperature 0.8
python chatapi_cli.py config set max_tokens 2000
```

### Provider Management

**Show current provider:**
```bash
./chatapi_cli.py provider show
# or
python chatapi_cli.py provider show
```

**Switch between providers:**
```bash
# Switch to OpenAI
./chatapi_cli.py provider set openai
# or
python chatapi_cli.py provider set openai

# Switch to Perplexity
./chatapi_cli.py provider set perplexity
# or
python chatapi_cli.py provider set perplexity
```

### History Management

**View conversation history:**
```bash
./chatapi_cli.py history
# or
python chatapi_cli.py history
```

**Clear conversation history:**
```bash
./chatapi_cli.py clear
# or
python chatapi_cli.py clear
```

## Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `provider` | `openai` | AI provider to use (openai, perplexity) |
| `openai_api_key` | (from env) | Your OpenAI API key |
| `perplexity_api_key` | (from env) | Your Perplexity API key |
| `model` | `gpt-3.5-turbo` | The model to use (varies by provider) |
| `max_tokens` | `1000` | Maximum tokens in response |
| `temperature` | `0.7` | Response creativity (0.0-1.0) |
| `system_prompt` | `You are a helpful assistant.` | System prompt for the model |
| `save_history` | `true` | Whether to save conversation history |
| `show_tokens` | `false` | Whether to show token usage |

## Interactive Mode Commands

When in interactive mode, you can use these commands:

- `help` - Show available commands
- `quit` / `exit` / `q` - Exit the program
- `clear` - Clear conversation history
- `history` - Show conversation history
- `config` - Show current configuration
- `provider show` - Show current AI provider
- `provider set <provider>` - Switch between openai/perplexity

## Examples

### Basic Usage

```bash
# Start interactive chat
./chatapi_cli.py chat
# or
python chatapi_cli.py chat

# Send a single message
./chatapi_cli.py chat "Write a Python function to calculate fibonacci numbers"
# or
python chatapi_cli.py chat "Write a Python function to calculate fibonacci numbers"
```

### Configuration Examples

```bash
# Set up for GPT-4 with higher creativity
./chatapi_cli.py config set model gpt-4
./chatapi_cli.py config set temperature 0.9
./chatapi_cli.py config set max_tokens 2000
# or
python chatapi_cli.py config set model gpt-4
python chatapi_cli.py config set temperature 0.9
python chatapi_cli.py config set max_tokens 2000

# Set a custom system prompt
./chatapi_cli.py config set system_prompt "You are a Python programming expert. Provide code examples and explanations."
# or
python chatapi_cli.py config set system_prompt "You are a Python programming expert. Provide code examples and explanations."

# Enable token usage display
./chatapi_cli.py config set show_tokens true
# or
python chatapi_cli.py config set show_tokens true
```

### Provider Examples

```bash
# Switch to Perplexity
./chatapi_cli.py provider set perplexity
# or
python chatapi_cli.py provider set perplexity

# Switch back to OpenAI
./chatapi_cli.py provider set openai
# or
python chatapi_cli.py provider set openai

# Check current provider
./chatapi_cli.py provider show
# or
python chatapi_cli.py provider show
```

## File Structure

The tool creates the following files in your home directory:

- `~/.chatapi-cli/config.yaml` - Configuration settings
- `~/.chatapi-cli/history.json` - Conversation history

## Requirements

- Python 3.7+
- OpenAI API key (for OpenAI provider)
- Perplexity API key (for Perplexity provider)
- Internet connection

## Dependencies

- `openai` - OpenAI API client
- `perplexity` - Perplexity API client
- `click` - Command-line interface creation
- `rich` - Rich text and beautiful formatting
- `pyyaml` - YAML configuration file handling
- `python-dotenv` - Environment variable loading
- `prompt-toolkit` - Advanced command-line interface
- `colorama` - Cross-platform colored terminal text

## Troubleshooting

### API Key Issues

If you get an error about the API key:

1. Make sure you have set your API keys:
   ```bash
   # For OpenAI
   ./chatapi_cli.py config set openai_api_key "your-openai-api-key"
   # or
   python chatapi_cli.py config set openai_api_key "your-openai-api-key"
   
   # For Perplexity
   ./chatapi_cli.py config set perplexity_api_key "your-perplexity-api-key"
   # or
   python chatapi_cli.py config set perplexity_api_key "your-perplexity-api-key"
   ```

2. Or set the environment variables:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-openai-api-key"
   
   # For Perplexity
   export PERPLEXITY_API_KEY="your-perplexity-api-key"
   ```

### Network Issues

If you're having network connectivity issues:

1. Check your internet connection
2. Verify that you can access OpenAI's API
3. Check if your API key has sufficient credits

### Configuration Issues

If the tool isn't working as expected:

1. Check your configuration:
   ```bash
   ./chatapi_cli.py config show
   # or
   python chatapi_cli.py config show
   ```

2. Reset to defaults by deleting the config file:
   ```bash
   rm ~/.chatapi-cli/config.yaml
   ```

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool!

## License

This project is open source and available under the MIT License. 