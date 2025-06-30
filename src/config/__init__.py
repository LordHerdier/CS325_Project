# src/config/__init__.py
# Configuration services for the application

from dotenv import load_dotenv
import os
from typing import Optional, Dict, Any, Union

class Config:
    def __init__(self):
        """Initialize configuration service"""
        load_dotenv()
        self._config = {}
        self._runtime_overrides = {}
        self.load_config()
        self.required_keys = ["OPENAI_API_KEY"]
        self.validate_config()
    
    def load_config(self):
        """Load the configuration from the .env file with defaults"""
        self._config = {
            # Required configuration
            "OPENAI_API_KEY": self._get_str("OPENAI_API_KEY"),
            
            # Optional configuration with defaults
            "DEBUG": self._get_bool("DEBUG", False),
            "USER_LOCATION": self._get_str("USER_LOCATION"),  # Can be None
            "JOB_BOARDS": self._get_list("JOB_BOARDS", ["indeed"]),
            "MAX_JOBS": self._get_int("MAX_JOBS", 500),
            "STORAGE_PATH": self._get_str("STORAGE_PATH", "storage"),
        }
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with optional default
        
        Priority: runtime_override > config > default
        """
        # Check runtime overrides first (highest priority)
        if key in self._runtime_overrides:
            return self._runtime_overrides[key]
            
        # Check loaded config
        if key in self._config:
            value = self._config[key]
            if value is not None:
                return value
                
        # Return default if provided
        return default
    
    def set_runtime_override(self, key: str, value: Any) -> None:
        """Set a runtime override for a configuration value"""
        self._runtime_overrides[key] = value
        
    def update_from_args(self, **kwargs) -> None:
        """Update configuration from runtime arguments"""
        for key, value in kwargs.items():
            if value is not None:  # Only override if value was actually provided
                self.set_runtime_override(key.upper(), value)
    
    def get_required(self, key: str) -> Any:
        """Get a required configuration value, raise error if missing"""
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required configuration '{key}' is missing")
        return value
    
    def validate_config(self) -> None:
        """Validate that all required configuration is present"""
        for key in self.required_keys:
            self.get_required(key)
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean value from environment variable"""
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in ('true', '1', 'yes', 'on')

    def _get_int(self, key: str, default: int = 0) -> int:
        """Get integer value from environment variable"""
        value = os.getenv(key)
        if value is None:
            return default
        return int(value)

    def _get_list(self, key: str, default: list = []) -> list:
        """Get list value from environment variable (comma-separated)"""
        value = os.getenv(key)
        if value is None:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]
    
    def _get_str(self, key: str, default: str = "") -> str:
        """Get string value from environment variable"""
        value = os.getenv(key)
        if value is None:
            return default
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return current configuration as dictionary"""
        result = self._config.copy()
        result.update(self._runtime_overrides)
        return result

config = Config()