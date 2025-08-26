"""
Cloud Utils Common Settings Module

Provides configuration loading from environment variables, configuration files,
and dictionaries.
"""

import os
from typing import Any, Dict, Optional, Union

from ..exceptions import ConfigError


class Settings:
    """Cloud Utils settings management class"""
    
    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize settings
        
        Args:
            **kwargs: Initial configuration values
        """
        self._settings: Dict[str, Any] = {}
        self._load_from_dict(kwargs)
        self._load_from_env()
    
    def _load_from_dict(self, config: Dict[str, Any]) -> None:
        """Load settings from dictionary"""
        for key, value in config.items():
            self._settings[key.upper()] = value
    
    def _load_from_env(self) -> None:
        """Load settings from environment variables"""
        for key, value in os.environ.items():
            if key.startswith('CLOUD_UTILS_'):
                # Remove CLOUD_UTILS_ prefix
                clean_key = key[13:]  # len('CLOUD_UTILS_') = 13
                self._settings[clean_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Configuration value or default value
        """
        return self._settings.get(key.upper(), default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._settings[key.upper()] = value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get boolean configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Boolean configuration value
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get integer configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Integer configuration value
        """
        value = self.get(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get float configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Float configuration value
        """
        value = self.get(key, default)
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: Optional[list] = None) -> list:
        """
        Get list configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            List configuration value
        """
        value = self.get(key, default)
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return default or []
    
    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get dictionary configuration value
        
        Args:
            key: Configuration key
            default: Default value
            
        Returns:
            Dictionary configuration value
        """
        value = self.get(key, default)
        if isinstance(value, dict):
            return value
        return default or {}
    
    def has(self, key: str) -> bool:
        """
        Check if configuration key exists
        
        Args:
            key: Configuration key
            
        Returns:
            True if key exists, False otherwise
        """
        return key.upper() in self._settings
    
    def all(self) -> Dict[str, Any]:
        """
        Get all configuration values
        
        Returns:
            Dictionary of all configuration values
        """
        return self._settings.copy()
    
    def update(self, config: Dict[str, Any]) -> None:
        """
        Update configuration
        
        Args:
            config: Configuration dictionary to update with
        """
        self._load_from_dict(config)


# Default settings instance
settings = Settings()

# AWS related default settings
AWS_DEFAULT_REGION = settings.get('AWS_DEFAULT_REGION', 'us-east-1')
AWS_PROFILE = settings.get('AWS_PROFILE')
AWS_ACCESS_KEY_ID = settings.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = settings.get('AWS_SECRET_ACCESS_KEY')

# Common settings
LOG_LEVEL = settings.get('LOG_LEVEL', 'INFO')
DEBUG = settings.get_bool('DEBUG', False)
TIMEOUT = settings.get_int('TIMEOUT', 30)
MAX_RETRIES = settings.get_int('MAX_RETRIES', 3)
