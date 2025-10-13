#!/usr/bin/env python3
"""
Unit tests for ChatAPI CLI tool.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import os

from chatapi_cli import ChatAPICLI
from validators import SecurityValidator, ConfigValidator, ValidationError


class TestSecurityValidator:
    """Test security validation functionality."""
    
    def test_validate_openai_api_key_valid(self):
        """Test valid OpenAI API key."""
        valid_key = "sk-1234567890abcdef1234567890abcdef1234567890abcdef"
        assert SecurityValidator.validate_api_key(valid_key, 'openai') is True
    
    def test_validate_openai_api_key_invalid(self):
        """Test invalid OpenAI API key."""
        invalid_keys = [
            "invalid-key",
            "sk-invalid",
            "sk-1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",  # Too long
            "sk-1234567890abcdef1234567890abcdef1234567890abcde",  # Too short
            ""
        ]
        for key in invalid_keys:
            assert SecurityValidator.validate_api_key(key, 'openai') is False
    
    def test_validate_perplexity_api_key_valid(self):
        """Test valid Perplexity API key."""
        valid_key = "pplx-1234567890abcdef1234567890abcdef12345678"
        assert SecurityValidator.validate_api_key(valid_key, 'perplexity') is True
    
    def test_validate_perplexity_api_key_invalid(self):
        """Test invalid Perplexity API key."""
        invalid_keys = [
            "invalid-key",
            "pplx-invalid",
            "pplx-1234567890abcdef1234567890abcdef1234567890123456789",  # Too long
            "pplx-1234567890abcdef1234567890abcdef1234567",  # Too short
            ""
        ]
        for key in invalid_keys:
            assert SecurityValidator.validate_api_key(key, 'perplexity') is False
    
    def test_validate_message_valid(self):
        """Test valid message validation."""
        valid_messages = [
            "Hello, world!",
            "What is the capital of France?",
            "Can you help me with Python programming?",
            "A" * 1000  # Long but valid message
        ]
        for message in valid_messages:
            validated = SecurityValidator.validate_message(message)
            assert validated == message.strip()
    
    def test_validate_message_invalid(self):
        """Test invalid message validation."""
        invalid_messages = [
            "",  # Empty message
            None,  # None message
            "A" * 10001,  # Too long
            "<script>alert('xss')</script>",  # XSS attempt
            "javascript:alert('xss')",  # JavaScript URL
            "data:text/html,<script>alert('xss')</script>"  # Data URL with script
        ]
        for message in invalid_messages:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_message(message)
    
    def test_validate_model_valid(self):
        """Test valid model validation."""
        valid_openai_models = SecurityValidator.ALLOWED_OPENAI_MODELS
        valid_perplexity_models = SecurityValidator.ALLOWED_PERPLEXITY_MODELS
        
        for model in valid_openai_models:
            assert SecurityValidator.validate_model(model, 'openai') is True
        
        for model in valid_perplexity_models:
            assert SecurityValidator.validate_model(model, 'perplexity') is True
    
    def test_validate_model_invalid(self):
        """Test invalid model validation."""
        invalid_models = [
            "invalid-model",
            "gpt-5",  # Non-existent OpenAI model
            "llama-4",  # Non-existent Perplexity model
            "",
            None
        ]
        for model in invalid_models:
            assert SecurityValidator.validate_model(model, 'openai') is False
            assert SecurityValidator.validate_model(model, 'perplexity') is False
    
    def test_validate_temperature_valid(self):
        """Test valid temperature validation."""
        valid_temperatures = [0.0, 0.5, 1.0, 1.5, 2.0]
        for temp in valid_temperatures:
            assert SecurityValidator.validate_temperature(temp) == temp
    
    def test_validate_temperature_invalid(self):
        """Test invalid temperature validation."""
        invalid_temperatures = [-0.1, 2.1, "invalid", None, -1, 3]
        for temp in invalid_temperatures:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_temperature(temp)
    
    def test_validate_max_tokens_valid(self):
        """Test valid max_tokens validation."""
        valid_tokens = [1, 100, 1000, 50000, 100000]
        for tokens in valid_tokens:
            assert SecurityValidator.validate_max_tokens(tokens) == tokens
    
    def test_validate_max_tokens_invalid(self):
        """Test invalid max_tokens validation."""
        invalid_tokens = [0, 100001, -1, "invalid", None, 1.5]
        for tokens in invalid_tokens:
            with pytest.raises(ValidationError):
                SecurityValidator.validate_max_tokens(tokens)


class TestConfigValidator:
    """Test configuration validation functionality."""
    
    def test_validate_config_valid_openai(self):
        """Test valid OpenAI configuration."""
        config = {
            'provider': 'openai',
            'openai_api_key': 'sk-1234567890abcdef1234567890abcdef1234567890abcdef',
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        errors = ConfigValidator.validate_config(config)
        assert len(errors) == 0
    
    def test_validate_config_valid_perplexity(self):
        """Test valid Perplexity configuration."""
        config = {
            'provider': 'perplexity',
            'perplexity_api_key': 'pplx-1234567890abcdef1234567890abcdef12345678',
            'model': 'llama-3.1-sonar-small-128k-online',
            'temperature': 0.7,
            'max_tokens': 1000
        }
        errors = ConfigValidator.validate_config(config)
        assert len(errors) == 0
    
    def test_validate_config_missing_provider(self):
        """Test configuration with missing provider."""
        config = {
            'openai_api_key': 'sk-1234567890abcdef1234567890abcdef1234567890abcdef'
        }
        errors = ConfigValidator.validate_config(config)
        assert "Provider not specified" in errors
    
    def test_validate_config_invalid_provider(self):
        """Test configuration with invalid provider."""
        config = {
            'provider': 'invalid_provider',
            'openai_api_key': 'sk-1234567890abcdef1234567890abcdef1234567890abcdef'
        }
        errors = ConfigValidator.validate_config(config)
        assert "Provider must be 'openai' or 'perplexity'" in errors
    
    def test_validate_config_missing_api_key(self):
        """Test configuration with missing API key."""
        config = {
            'provider': 'openai'
        }
        errors = ConfigValidator.validate_config(config)
        assert "OpenAI API key not set" in errors
    
    def test_validate_config_invalid_api_key(self):
        """Test configuration with invalid API key."""
        config = {
            'provider': 'openai',
            'openai_api_key': 'invalid-key'
        }
        errors = ConfigValidator.validate_config(config)
        assert "Invalid OpenAI API key format" in errors


class TestChatAPICLI:
    """Test ChatAPICLI functionality."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_cli(self, temp_dir):
        """Create ChatAPICLI instance with temporary directory."""
        with patch('chatapi_cli.Path.home') as mock_home:
            mock_home.return_value = temp_dir
            cli = ChatAPICLI()
            yield cli
    
    def test_initialization(self, mock_cli):
        """Test ChatAPICLI initialization."""
        assert mock_cli.config_dir.exists()
        assert mock_cli.config_file.exists()
        assert 'provider' in mock_cli.config
        assert mock_cli.config['provider'] == 'openai'
    
    def test_load_config_default(self, mock_cli):
        """Test loading default configuration."""
        config = mock_cli.load_config()
        assert config['provider'] == 'openai'
        assert config['model'] == 'gpt-3.5-turbo'
        assert config['temperature'] == 0.7
        assert config['max_tokens'] == 1000
    
    def test_save_config(self, mock_cli):
        """Test saving configuration."""
        test_config = {
            'provider': 'openai',
            'openai_api_key': 'test-key',
            'model': 'gpt-4',
            'temperature': 0.9,
            'max_tokens': 2000
        }
        mock_cli.save_config(test_config)
        
        # Verify config was saved
        with open(mock_cli.config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config['provider'] == 'openai'
        assert saved_config['model'] == 'gpt-4'
        assert saved_config['temperature'] == 0.9
        assert saved_config['max_tokens'] == 2000
    
    def test_add_to_history(self, mock_cli):
        """Test adding messages to history."""
        mock_cli.add_to_history('user', 'Hello')
        mock_cli.add_to_history('assistant', 'Hi there!')
        
        assert len(mock_cli.conversation_history) == 2
        assert mock_cli.conversation_history[0]['role'] == 'user'
        assert mock_cli.conversation_history[0]['content'] == 'Hello'
        assert mock_cli.conversation_history[1]['role'] == 'assistant'
        assert mock_cli.conversation_history[1]['content'] == 'Hi there!'
    
    def test_get_messages(self, mock_cli):
        """Test getting messages for API call."""
        mock_cli.add_to_history('user', 'Hello')
        mock_cli.add_to_history('assistant', 'Hi!')
        
        messages = mock_cli.get_messages()
        
        assert len(messages) == 3  # system + 2 conversation messages
        assert messages[0]['role'] == 'system'
        assert messages[1]['role'] == 'user'
        assert messages[2]['role'] == 'assistant'
    
    @patch('chatapi_cli.openai.OpenAI')
    def test_initialize_client_openai(self, mock_openai_class, mock_cli):
        """Test initializing OpenAI client."""
        mock_cli.config['provider'] = 'openai'
        mock_cli.config['openai_api_key'] = 'sk-1234567890abcdef1234567890abcdef1234567890abcdef'
        
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        
        mock_cli.initialize_client()
        
        assert mock_cli.openai_client == mock_client
        mock_openai_class.assert_called_once_with(api_key='sk-1234567890abcdef1234567890abcdef1234567890abcdef')
    
    @patch('chatapi_cli.perplexity.Client')
    def test_initialize_client_perplexity(self, mock_perplexity_class, mock_cli):
        """Test initializing Perplexity client."""
        mock_cli.config['provider'] = 'perplexity'
        mock_cli.config['perplexity_api_key'] = 'pplx-1234567890abcdef1234567890abcdef12345678'
        
        mock_client = Mock()
        mock_perplexity_class.return_value = mock_client
        
        mock_cli.initialize_client()
        
        assert mock_cli.perplexity_client == mock_client
        mock_perplexity_class.assert_called_once_with(api_key='pplx-1234567890abcdef1234567890abcdef12345678')
    
    def test_chat_input_validation(self, mock_cli):
        """Test chat method input validation."""
        # Test with invalid input (empty message)
        result = mock_cli.chat("")
        assert "Input validation error" in result
        
        # Test with potentially malicious input
        result = mock_cli.chat("<script>alert('xss')</script>")
        assert "Input validation error" in result
    
    @patch('chatapi_cli.openai.OpenAI')
    def test_chat_success(self, mock_openai_class, mock_cli):
        """Test successful chat interaction."""
        # Setup mock client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_response.usage.total_tokens = 50
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Setup config
        mock_cli.config['provider'] = 'openai'
        mock_cli.config['openai_api_key'] = 'sk-1234567890abcdef1234567890abcdef1234567890abcdef'
        mock_cli.config['show_tokens'] = True
        
        result = mock_cli.chat("Hello")
        
        assert result == "Hello! How can I help you?"
        assert len(mock_cli.conversation_history) == 2  # user + assistant message
        mock_client.chat.completions.create.assert_called_once()


class TestIntegration:
    """Integration tests."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_full_config_cycle(self, temp_dir):
        """Test complete configuration save/load cycle."""
        with patch('chatapi_cli.Path.home') as mock_home:
            mock_home.return_value = temp_dir
            
            # Create CLI instance
            cli1 = ChatAPICLI()
            
            # Modify configuration
            cli1.config['provider'] = 'perplexity'
            cli1.config['model'] = 'llama-3.1-sonar-large-128k-online'
            cli1.config['temperature'] = 0.9
            cli1.save_config(cli1.config)
            
            # Create new CLI instance and verify config was saved
            cli2 = ChatAPICLI()
            assert cli2.config['provider'] == 'perplexity'
            assert cli2.config['model'] == 'llama-3.1-sonar-large-128k-online'
            assert cli2.config['temperature'] == 0.9
    
    def test_history_persistence(self, temp_dir):
        """Test conversation history persistence."""
        with patch('chatapi_cli.Path.home') as mock_home:
            mock_home.return_value = temp_dir
            
            # Create CLI instance and add history
            cli1 = ChatAPICLI()
            cli1.add_to_history('user', 'Test message 1')
            cli1.add_to_history('assistant', 'Test response 1')
            
            # Create new CLI instance and verify history was saved
            cli2 = ChatAPICLI()
            cli2.load_history()
            
            assert len(cli2.conversation_history) == 2
            assert cli2.conversation_history[0]['content'] == 'Test message 1'
            assert cli2.conversation_history[1]['content'] == 'Test response 1'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
