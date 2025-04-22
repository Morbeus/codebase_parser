import os
from typing import Dict, Any

# Basic settings
API_KEY = "test-api-key-123"
DEBUG = True
DATABASE_URL = "postgresql://user:pass@localhost:5432/db"

# Dynamic settings based on environment
ENV = os.getenv("ENV", "development")
SETTINGS: Dict[str, Any] = {
    "development": {
        "debug": True,
        "log_level": "DEBUG"
    },
    "production": {
        "debug": False,
        "log_level": "INFO"
    }
}

# Current environment settings
CURRENT_SETTINGS = SETTINGS[ENV]

# Dynamic configuration
def get_setting(key: str, default: Any = None) -> Any:
    """Dynamically get a setting value."""
    return CURRENT_SETTINGS.get(key, default) 