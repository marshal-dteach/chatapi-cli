#!/usr/bin/env python3
"""
ChatAPI CLI Tool
A command-line interface for interacting with OpenAI's ChatGPT API and Perplexity API.
"""

import os
import sys
import json
import yaml
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

import click
import openai
from perplexity import Perplexity
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table
from rich.live import Live
from rich.spinner import Spinner
from dotenv import load_dotenv
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style

# Import our validation modules
from validators import (
    SecurityValidator, ConfigValidator, SecureStorage, ValidationError
)

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path.home() / '.chatapi-cli' / 'chatapi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

class ChatAPICLI:
    def __init__(self):
        self.config_dir = Path.home() / ".chatapi-cli"
        self.config_file = self.config_dir / "config.yaml"
        self.history_file = self.config_dir / "history.json"
        self.key_file = self.config_dir / ".encryption_key"
        
        # Initialize secure storage
        self.secure_storage = SecureStorage(str(self.key_file))
        
        # Initialize clients
        self.openai_client = None
        self.perplexity_client = None
        
        # Initialize session and history
        self.session = PromptSession()
        self.conversation_history = []
        
        # Load and validate configuration
        self.config = self.load_config()
        self._validate_and_fix_config()
    
    def _validate_and_fix_config(self):
        """Validate configuration and fix common issues."""
        try:
            errors = ConfigValidator.validate_config(self.config)
            if errors:
                logger.warning(f"Configuration validation errors: {errors}")
                console.print("[yellow]Configuration issues detected:[/yellow]")
                for error in errors:
                    console.print(f"  • {error}")
                console.print("[yellow]Some features may not work properly.[/yellow]")
        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            console.print(f"[red]Configuration validation failed: {e}[/red]")
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
                
                # Decrypt API keys if they're encrypted
                if 'openai_api_key' in config and config['openai_api_key'].startswith('encrypted:'):
                    try:
                        encrypted_key = config['openai_api_key'][10:]  # Remove 'encrypted:' prefix
                        config['openai_api_key'] = self.secure_storage.decrypt(encrypted_key)
                    except Exception as e:
                        logger.error(f"Failed to decrypt OpenAI API key: {e}")
                        config['openai_api_key'] = ''
                
                if 'perplexity_api_key' in config and config['perplexity_api_key'].startswith('encrypted:'):
                    try:
                        encrypted_key = config['perplexity_api_key'][10:]  # Remove 'encrypted:' prefix
                        config['perplexity_api_key'] = self.secure_storage.decrypt(encrypted_key)
                    except Exception as e:
                        logger.error(f"Failed to decrypt Perplexity API key: {e}")
                        config['perplexity_api_key'] = ''
                
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                console.print(f"[red]Error loading config: {e}[/red]")
                return {}
        
        # Create default config
        provider = os.getenv('CHATAPI_PROVIDER', 'openai')
        default_config = {
            'provider': provider,  # 'openai' or 'perplexity'
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'perplexity_api_key': os.getenv('PERPLEXITY_API_KEY', ''),
            'model': 'sonar' if provider == 'perplexity' else 'gpt-3.5-turbo',
            'max_tokens': 1000,
            'temperature': 0.7,
            'system_prompt': 'You are a helpful assistant.',
            'save_history': True,
            'show_tokens': False
        }
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file with encrypted API keys."""
        self.config_dir.mkdir(exist_ok=True, mode=0o700)  # Secure directory permissions
        
        # Create a copy of config for saving
        save_config = config.copy()
        
        # Encrypt API keys before saving
        if 'openai_api_key' in save_config and save_config['openai_api_key']:
            if not save_config['openai_api_key'].startswith('encrypted:'):
                try:
                    encrypted_key = self.secure_storage.encrypt(save_config['openai_api_key'])
                    save_config['openai_api_key'] = f'encrypted:{encrypted_key}'
                except Exception as e:
                    logger.error(f"Failed to encrypt OpenAI API key: {e}")
        
        if 'perplexity_api_key' in save_config and save_config['perplexity_api_key']:
            if not save_config['perplexity_api_key'].startswith('encrypted:'):
                try:
                    encrypted_key = self.secure_storage.encrypt(save_config['perplexity_api_key'])
                    save_config['perplexity_api_key'] = f'encrypted:{encrypted_key}'
                except Exception as e:
                    logger.error(f"Failed to encrypt Perplexity API key: {e}")
        
        # Save config file with secure permissions
        with open(self.config_file, 'w') as f:
            yaml.dump(save_config, f, default_flow_style=False)
        
        # Set secure file permissions (readable only by owner)
        os.chmod(self.config_file, 0o600)
        logger.info("Configuration saved with secure permissions")
    
    def initialize_client(self):
        """Initialize API client based on configured provider."""
        provider = self.config.get('provider', 'openai')
        
        if provider == 'openai':
            api_key = self.config.get('openai_api_key')
            if not api_key:
                console.print("[red]Error: OpenAI API key not found![/red]")
                console.print("Please set your OpenAI API key using:")
                console.print("  chatgpt-cli config set openai_api_key YOUR_API_KEY")
                console.print("Or set the OPENAI_API_KEY environment variable.")
                sys.exit(1)
            
            self.openai_client = openai.OpenAI(api_key=api_key)
            
        elif provider == 'perplexity':
            api_key = self.config.get('perplexity_api_key')
            if not api_key:
                console.print("[red]Error: Perplexity API key not found![/red]")
                console.print("Please set your Perplexity API key using:")
                console.print("  chatgpt-cli config set perplexity_api_key YOUR_API_KEY")
                console.print("Or set the PERPLEXITY_API_KEY environment variable.")
                sys.exit(1)
            
            self.perplexity_client = Perplexity(api_key=api_key)
            
        else:
            console.print(f"[red]Error: Unknown provider '{provider}'. Supported providers: openai, perplexity[/red]")
            sys.exit(1)
    
    def load_history(self):
        """Load conversation history."""
        if self.history_file.exists() and self.config.get('save_history', True):
            try:
                with open(self.history_file, 'r') as f:
                    self.conversation_history = json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load history: {e}[/yellow]")
                self.conversation_history = []
    
    def save_history(self):
        """Save conversation history."""
        if self.config.get('save_history', True):
            try:
                with open(self.history_file, 'w') as f:
                    json.dump(self.conversation_history, f, indent=2)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not save history: {e}[/yellow]")
    
    def add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        })
        self.save_history()
    
    def get_messages(self) -> List[Dict[str, str]]:
        """Get messages for API call."""
        messages = [{'role': 'system', 'content': self.config.get('system_prompt', 'You are a helpful assistant.')}]
        
        # Add conversation history (last 10 messages to avoid token limits)
        for msg in self.conversation_history[-10:]:
            messages.append({'role': msg['role'], 'content': msg['content']})
        
        return messages
    
    def chat(self, message: str) -> str:
        """Send message to ChatGPT/Perplexity and return response."""
        # Validate input message
        try:
            validated_message = SecurityValidator.validate_message(message)
        except ValidationError as e:
            error_msg = f"Input validation error: {e}"
            logger.error(error_msg)
            console.print(f"[red]{error_msg}[/red]")
            return error_msg
        
        if not self.openai_client and not self.perplexity_client:
            self.initialize_client()
        
        # Retry logic for API calls
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                messages = self.get_messages()
                messages.append({'role': 'user', 'content': validated_message})
                
                with console.status("[bold green]Thinking...", spinner="dots"):
                    if self.openai_client:
                        response = self.openai_client.chat.completions.create(
                            model=self.config.get('model', 'gpt-3.5-turbo'),
                            messages=messages,
                            max_tokens=self.config.get('max_tokens', 1000),
                            temperature=self.config.get('temperature', 0.7)
                        )
                        assistant_message = response.choices[0].message.content
                        
                        if self.config.get('show_tokens', False):
                            console.print(f"[dim]Tokens used: {response.usage.total_tokens}[/dim]")
                            
                    elif self.perplexity_client:
                        response = self.perplexity_client.chat.completions.create(
                            model=self.config.get('model', 'sonar'),
                            messages=messages,
                            max_tokens=self.config.get('max_tokens', 1000),
                            temperature=self.config.get('temperature', 0.7)
                        )
                        assistant_message = response.choices[0].message.content
                        
                        if self.config.get('show_tokens', False):
                            console.print(f"[dim]Tokens used: {response.usage.total_tokens}[/dim]")
                
                # Add to history
                self.add_to_history('user', validated_message)
                self.add_to_history('assistant', assistant_message)
                
                logger.info(f"Successful API call (attempt {attempt + 1})")
                return assistant_message
                
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                if attempt < max_retries - 1:
                    console.print(f"[yellow]Retrying in {retry_delay} seconds...[/yellow]")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    provider = self.config.get('provider', 'openai')
                    error_msg = f"Error communicating with {provider.title()} after {max_retries} attempts: {e}"
                    logger.error(error_msg)
                    console.print(f"[red]{error_msg}[/red]")
                    return error_msg
    
    def display_response(self, response: str):
        """Display response with rich formatting."""
        if response.startswith("Error communicating with"):
            console.print(Panel(response, title="Error", border_style="red"))
        else:
            # Try to render as markdown, fallback to plain text
            try:
                md = Markdown(response)
                console.print(md)
            except:
                console.print(response)
    
    def interactive_mode(self):
        """Start interactive chat mode."""
        provider = self.config.get('provider', 'openai')
        console.print(Panel.fit(
            f"[bold blue]ChatAPI CLI - {provider.title()}[/bold blue]\n"
            "Type your message and press Enter. Type 'quit', 'exit', or 'q' to exit.\n"
            "Type 'help' for available commands.\n"
            f"Current provider: [bold]{provider.title()}[/bold]",
            title="Welcome",
            border_style="blue"
        ))
        
        # Create command completer
        commands = ['help', 'quit', 'exit', 'clear', 'history', 'config', 'save']
        completer = WordCompleter(commands, ignore_case=True)
        
        while True:
            try:
                # Use Rich Prompt for styling but add completion support
                console.print("\n[bold cyan]You:[/bold cyan] \n", end="")
                user_input = self.session.prompt(
                    "",
                    completer=completer
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    console.print("[yellow]Goodbye![/yellow]")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    self.save_history()
                    console.print("[green]Conversation history cleared.[/green]")
                    continue
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                elif user_input.lower() == 'config':
                    self.show_config()
                    continue
                
                # Send message to ChatGPT
                response = self.chat(user_input)
                console.print("\n[bold green]Assistant:[/bold green]")
                self.display_response(response)
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
            except EOFError:
                console.print("\n[yellow]Goodbye![/yellow]")
                break
    
    def show_help(self):
        """Show help information."""
        help_text = """
[bold]Available Commands:[/bold]
• help - Show this help message
• quit/exit/q - Exit the program
• clear - Clear conversation history
• history - Show conversation history
• config - Show current configuration

[bold]Provider Management:[/bold]
• provider show - Show current AI provider
• provider set <provider> - Switch between openai/perplexity

[bold]Usage:[/bold]
Just type your message and press Enter to chat with your configured AI provider!
        """
        console.print(Panel(help_text, title="Help", border_style="green"))
    
    def show_history(self):
        """Show conversation history."""
        if not self.conversation_history:
            console.print("[yellow]No conversation history.[/yellow]")
            return
        
        table = Table(title="Conversation History")
        table.add_column("Time", style="cyan")
        table.add_column("Role", style="magenta")
        table.add_column("Message", style="white")
        
        for msg in self.conversation_history[-10:]:  # Show last 10 messages
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime("%H:%M:%S")
            role = msg['role'].title()
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            table.add_row(timestamp, role, content)
        
        console.print(table)
    
    def show_config(self):
        """Show current configuration."""
        config_table = Table(title="Current Configuration")
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="white")
        
        for key, value in self.config.items():
            if key in ['openai_api_key', 'perplexity_api_key']:
                display_value = value[:10] + "..." if value else "Not set"
            else:
                display_value = str(value)
            config_table.add_row(key, display_value)
        
        console.print(config_table)

@click.group()
def cli():
    """ChatAPI CLI - A command-line interface for multiple AI providers."""
    pass

@cli.command()
@click.argument('message', required=False)
def chat(message):
    """Start a chat session with your configured AI provider."""
    cli_tool = ChatAPICLI()
    cli_tool.load_history()
    
    if message:
        # Single message mode
        cli_tool.initialize_client()
        response = cli_tool.chat(message)
        cli_tool.display_response(response)
    else:
        # Interactive mode
        cli_tool.interactive_mode()

@cli.group()
def provider():
    """Manage AI providers."""
    pass

@provider.command()
def show():
    """Show current provider."""
    cli_tool = ChatAPICLI()
    provider = cli_tool.config.get('provider', 'openai')
    console.print(f"[green]Current provider: {provider.title()}[/green]")

@provider.command()
@click.argument('provider_name')
def set(provider_name):
    """Set the AI provider (openai or perplexity)."""
    if provider_name.lower() not in ['openai', 'perplexity']:
        console.print("[red]Error: Provider must be 'openai' or 'perplexity'[/red]")
        return
    
    cli_tool = ChatAPICLI()
    cli_tool.config['provider'] = provider_name.lower()
    cli_tool.save_config(cli_tool.config)
    console.print(f"[green]Provider set to {provider_name.title()}[/green]")

@cli.group()
def config():
    """Manage configuration settings."""
    pass

@config.command()
def show():
    """Show current configuration."""
    cli_tool = ChatAPICLI()
    cli_tool.show_config()

@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set a configuration value."""
    cli_tool = ChatAPICLI()
    cli_tool.config[key] = value
    cli_tool.save_config(cli_tool.config)
    console.print(f"[green]Set {key} = {value}[/green]")

@cli.command()
def history():
    """Show conversation history."""
    cli_tool = ChatAPICLI()
    cli_tool.load_history()
    cli_tool.show_history()

@cli.command()
def clear():
    """Clear conversation history."""
    cli_tool = ChatAPICLI()
    cli_tool.conversation_history.clear()
    cli_tool.save_history()
    console.print("[green]Conversation history cleared.[/green]")

if __name__ == '__main__':
    cli() 