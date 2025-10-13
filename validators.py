#!/usr/bin/env python3
"""
Input validation and security utilities for ChatAPI CLI.
"""

import re
import os
from typing import Optional, List, Dict, Any
from cryptography.fernet import Fernet
import base64
import hashlib


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class SecurityValidator:
    """Handles input validation and security checks."""
    
    # Maximum message length to prevent abuse
    MAX_MESSAGE_LENGTH = 10000
    
    # API key patterns for validation
    OPENAI_API_KEY_PATTERN = r'^sk-[a-zA-Z0-9]{48}$'
    PERPLEXITY_API_KEY_PATTERN = r'^pplx-[a-zA-Z0-9]{40}$'
    
    # Allowed model names
    ALLOWED_OPENAI_MODELS = [
        'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k',
        'gpt-4-turbo', 'gpt-4o', 'gpt-4o-mini'
    ]
    
    ALLOWED_PERPLEXITY_MODELS = [
        'llama-3.1-sonar-small-128k-online',
        'llama-3.1-sonar-large-128k-online',
        'llama-3.1-sonar-huge-128k-online',
        'llama-3.1-sonar-small-128k-chat',
        'llama-3.1-sonar-large-128k-chat',
        'llama-3.1-sonar-huge-128k-chat'
    ]
    
    @staticmethod
    def validate_api_key(api_key: str, provider: str) -> bool:
        """Validate API key format."""
        if not api_key or not isinstance(api_key, str):
            return False
            
        api_key = api_key.strip()
        
        if provider == 'openai':
            return bool(re.match(SecurityValidator.OPENAI_API_KEY_PATTERN, api_key))
        elif provider == 'perplexity':
            return bool(re.match(SecurityValidator.PERPLEXITY_API_KEY_PATTERN, api_key))
        
        return False
    
    @staticmethod
    def validate_message(message: str) -> str:
        """Validate and sanitize user message."""
        if not message:
            raise ValidationError("Message cannot be empty")
        
        if not isinstance(message, str):
            raise ValidationError("Message must be a string")
        
        # Remove potential security issues
        message = message.strip()
        
        if len(message) > SecurityValidator.MAX_MESSAGE_LENGTH:
            raise ValidationError(f"Message too long (max {SecurityValidator.MAX_MESSAGE_LENGTH} characters)")
        
        # Check for potentially harmful patterns
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html',
            r'vbscript:',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                raise ValidationError("Message contains potentially unsafe content")
        
        return message
    
    @staticmethod
    def validate_model(model: str, provider: str) -> bool:
        """Validate model name."""
        if not model or not isinstance(model, str):
            return False
        
        if provider == 'openai':
            return model in SecurityValidator.ALLOWED_OPENAI_MODELS
        elif provider == 'perplexity':
            return model in SecurityValidator.ALLOWED_PERPLEXITY_MODELS
        
        return False
    
    @staticmethod
    def validate_temperature(temperature: Any) -> float:
        """Validate temperature parameter."""
        try:
            temp = float(temperature)
            if not 0.0 <= temp <= 2.0:
                raise ValidationError("Temperature must be between 0.0 and 2.0")
            return temp
        except (ValueError, TypeError):
            raise ValidationError("Temperature must be a number")
    
    @staticmethod
    def validate_max_tokens(max_tokens: Any) -> int:
        """Validate max_tokens parameter."""
        try:
            tokens = int(max_tokens)
            if not 1 <= tokens <= 100000:
                raise ValidationError("Max tokens must be between 1 and 100000")
            return tokens
        except (ValueError, TypeError):
            raise ValidationError("Max tokens must be an integer")


class ConfigValidator:
    """Validates configuration settings."""
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> List[str]:
        """Validate entire configuration and return list of errors."""
        errors = []
        
        # Validate provider
        if 'provider' not in config:
            errors.append("Provider not specified")
        elif config['provider'] not in ['openai', 'perplexity']:
            errors.append("Provider must be 'openai' or 'perplexity'")
        
        # Validate API keys
        provider = config.get('provider', 'openai')
        if provider == 'openai':
            api_key = config.get('openai_api_key', '')
            if not api_key:
                errors.append("OpenAI API key not set")
            elif not SecurityValidator.validate_api_key(api_key, 'openai'):
                errors.append("Invalid OpenAI API key format")
        elif provider == 'perplexity':
            api_key = config.get('perplexity_api_key', '')
            if not api_key:
                errors.append("Perplexity API key not set")
            elif not SecurityValidator.validate_api_key(api_key, 'perplexity'):
                errors.append("Invalid Perplexity API key format")
        
        # Validate model
        model = config.get('model')
        if model and not SecurityValidator.validate_model(model, provider):
            errors.append(f"Invalid model '{model}' for provider '{provider}'")
        
        # Validate temperature
        try:
            SecurityValidator.validate_temperature(config.get('temperature', 0.7))
        except ValidationError as e:
            errors.append(str(e))
        
        # Validate max_tokens
        try:
            SecurityValidator.validate_max_tokens(config.get('max_tokens', 1000))
        except ValidationError as e:
            errors.append(str(e))
        
        return errors


class SecureStorage:
    """Handles secure storage of sensitive data."""
    
    def __init__(self, key_file: str):
        self.key_file = key_file
        self._fernet = None
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key or create a new one."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            os.chmod(os.path.dirname(self.key_file), 0o700)
            with open(self.key_file, 'wb') as f:
                f.write(key)
            os.chmod(self.key_file, 0o600)
            return key
    
    def _get_fernet(self) -> Fernet:
        """Get Fernet instance for encryption."""
        if self._fernet is None:
            key = self._get_or_create_key()
            self._fernet = Fernet(key)
        return self._fernet
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        fernet = self._get_fernet()
        encrypted_data = fernet.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        fernet = self._get_fernet()
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode()
    
    def hash_api_key(self, api_key: str) -> str:
        """Create a hash of API key for validation purposes."""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
