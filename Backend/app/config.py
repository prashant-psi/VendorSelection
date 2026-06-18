"""Backward-compatible config re-exports."""

from app.core.config import ENV_FILE, Settings, database_url, settings

AppSettings = Settings
vendor_connection_url = database_url
dbSettings = settings

__all__ = ["AppSettings", "ENV_FILE", "dbSettings", "settings", "vendor_connection_url"]
