import os
import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATH = Path.home() / ".ufc_fetcher" / "config.json"

class Settings:
    def __init__(self, config_path: Path = DEFAULT_CONFIG_PATH):
        self.config_path = config_path
        self._data: Dict[str, Any] = {
            "prowlarr_url": "http://localhost:9696",
            "prowlarr_api_key": "",
            "qbittorrent_host": "localhost",
            "qbittorrent_port": 8080,
            "qbittorrent_username": "admin",
            "qbittorrent_password": "",
            "qbittorrent_category": "UFC",
            "library_path": "", # User must set this
            "downloads_path": "", # User must set this
            "sports_db_url": "https://www.thesportsdb.com/api/v1/json/123", # default public key
            "language_preference": "en", # 'en', 'ru', etc.
            "quality_preference": 1080,
            "codec_preference": "x265",
            "event_types": "all", # 'all' or 'no_fightnights'
            "full_or_main": "full", # 'full' or 'main_only'
        }
        self.load()

    def load(self):
        # 1. Load from file
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    file_data = json.load(f)
                    self._data.update(file_data)
            except Exception as e:
                print(f"Error loading config from {self.config_path}: {e}")

        # 2. Overwrite from environment variables (UFC_FETCHER_*)
        for key in self._data.keys():
            env_key = f"UFC_FETCHER_{key.upper()}"
            env_val = os.getenv(env_key)
            if env_val:
                # Basic type casting
                current_val = self._data[key]
                if isinstance(current_val, bool):
                    self._data[key] = env_val.lower() in ("true", "1", "yes")
                elif isinstance(current_val, int):
                    self._data[key] = int(env_val)
                else:
                    self._data[key] = env_val

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    @property
    def prowlarr_url(self) -> str: return self.get("prowlarr_url")
    @property
    def prowlarr_api_key(self) -> str: return self.get("prowlarr_api_key")
    @property
    def sports_db_url(self) -> str: return self.get("sports_db_url")
    @property
    def qbittorrent_conn(self) -> dict:
        return {
            "host": self.get("qbittorrent_host"),
            "port": self.get("qbittorrent_port"),
            "username": self.get("qbittorrent_username"),
            "password": self.get("qbittorrent_password"),
        }
    @property
    def library_path(self) -> Path: return Path(self.get("library_path"))
    @property
    def downloads_path(self) -> Path: return Path(self.get("downloads_path"))
    @property
    def qbittorrent_category(self) -> str: return self.get("qbittorrent_category")
    @property
    def language_preference(self) -> str: return self.get("language_preference")
    @property
    def quality_preference(self) -> str: return self.get("quality_preference")
    @property
    def codec_preference(self) -> str: return self.get("codec_preference")
    @property
    def event_types(self) -> str: return self.get("event_types", "all")
    @property
    def full_or_main(self) -> str: return self.get("full_or_main", "full")

settings = Settings()
