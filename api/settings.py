from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime as dt
from hashlib import sha256
import os
import logging


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    HOST: str = '127.0.0.1'
    PROXY_PREFIX: str = ''
    SSL_VERIFY: str = ''
    LOCALE: str = 'pt_BR.UTF-8'
    PIDIGITAL_URL: str = ''
    BASE_URL: str = ''
    PROJECT_NAME: str = "WhatApp API Multi-instance docker manager"
    MODE: str = 'dev'
    APP_PORT: int = 8000
    VERSION: str = '0.1.0'
    CORS_ALLOW_ORIGINS: str = '*'
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = 'GET, POST, PUT, DELETE, OPTIONS'
    CORS_ALLOW_HEADERS: str = '*'
    SECURITY_TOKEN: str = '123'

    def __init__(self, **data):
        super().__init__(**data)

    @property
    def mode(self):
        return '' if self.MODE == 'prod' else f'-{self.MODE}'.upper()

    @property
    def title(self):
        return self.PROJECT_NAME.upper()

    @property
    def version(self):
        return self.VERSION

    def generate_description(self, description: str = None) -> str:
        if not description:
            description = ""
        return description

    def generate_openapi_tags(self, openapi_tags: List[dict] = None) -> List[dict]:
        if openapi_tags:
            return openapi_tags

        return []

    @property
    def license(self):
        return {
            'name': 'Apache 2.0',
            'url': 'https://www.apache.org/licenses/LICENSE-2.0.html',
        }

    @property
    def contact(self):
        return {}

    @property
    def root_path(self):
        return self.PROXY_PREFIX if self.MODE != 'dev' else ''

    @property
    def docs_url(self):
        return '/api/docs'

    @property
    def redoc_url(self):
        return '/api/redoc'

    @property
    def allowed_origins(self):
        return self.CORS_ALLOW_ORIGINS.split(',')

    @property
    def allowed_credentials(self):
        return self.CORS_ALLOW_CREDENTIALS

    @property
    def allowed_methods(self):
        return self.CORS_ALLOW_METHODS.split(',')

    @property
    def allowed_headers(self):
        return self.CORS_ALLOW_HEADERS.split(',')
    
    @property
    def security_token(self):
        token = sha256(self.SECURITY_TOKEN.encode()).hexdigest()
        return token

app_settings = AppSettings()

class LoggerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    LOGS_DIR: str = "logs"
    LOG_LEVEL: str = "INFO" # For console
    IS_UNIFIED_LOG: bool = True
    LOG_FILE: str = "application_{time}.log"
    ROTATION: str = "200 MB"

    @property
    def log_dir(self) -> str:
        return self.LOGS_DIR
    
    @property
    def name(self) -> str:
        return __name__
    
    @property
    def level(self) -> int:
        return getattr(logging, self.LOG_LEVEL)
    
    @property
    def is_unified(self) -> bool:
        return self.IS_UNIFIED_LOG
    
    @property
    def rotation(self) -> str:
        return self.ROTATION
    
    @property
    def log_filename(self) -> str:
        alternative_name_format = f"{dt.now().strftime('%Y%m%d')}_{dt.now().strftime('%H%M%S')}_{self.iteration}.log"
        return self.LOG_FILE if self.is_unified else alternative_name_format
    
    @property
    def log_file(self) -> str:
        return os.path.join(self.log_dir, self.log_filename)
    
    @property
    def existing_logs_files(self) -> list:
        return os.listdir(self.log_dir)
    
    @property
    def iteration(self) -> int:
        return len(self.existing_logs_files()) + 1
    
    @property
    def format(self) -> str:
        return '%(asctime)s - %(levelname)s - %(message)s'
    
    @property
    def format_loguru(self) -> str:
        return "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra[task]} | {name} | {extra[args]}"
    
    def ensure_dir(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

logger_settings = LoggerSettings()