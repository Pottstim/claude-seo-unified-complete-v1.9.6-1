"""
Base provider class and configuration
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import os
import yaml
from pathlib import Path


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    model: Optional[str] = None
    timeout: int = 60
    retry_attempts: int = 3
    extra: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, name: str, data: Dict[str, Any]) -> "ProviderConfig":
        """Create config from dictionary, resolving environment variables"""
        def resolve_env(value):
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                # Handle default values: ${VAR:-default}
                if ":-" in env_var:
                    var_name, default = env_var.split(":-", 1)
                    return os.getenv(var_name, default)
                return os.getenv(env_var)
            return value
        
        resolved = {}
        for k, v in data.items():
            if isinstance(v, dict):
                resolved[k] = {kk: resolve_env(vv) for kk, vv in v.items()}
            else:
                resolved[k] = resolve_env(v)
        
        return cls(
            name=name,
            enabled=resolved.get("enabled", True),
            api_key=resolved.get("api_key"),
            api_base=resolved.get("api_base") or resolved.get("base_url"),
            model=resolved.get("model"),
            timeout=resolved.get("timeout", 60),
            retry_attempts=resolved.get("retry_attempts", 3),
            extra=resolved,
        )


class BaseProvider(ABC):
    """Abstract base class for all providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None
    
    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Return the provider type identifier"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available"""
        pass
    
    def validate_config(self) -> bool:
        """Validate the configuration"""
        if not self.config.enabled:
            return False
        return True
    
    def get_client(self) -> Any:
        """Get or create the provider client"""
        if self._client is None:
            self._client = self._create_client()
        return self._client
    
    @abstractmethod
    def _create_client(self) -> Any:
        """Create the provider client"""
        pass
    
    @staticmethod
    def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file"""
        path = Path(config_path)
        if not path.exists():
            # Try example config
            example_path = Path("config/config.example.yaml")
            if example_path.exists():
                path = example_path
            else:
                return {}
        
        with open(path) as f:
            return yaml.safe_load(f) or {}
