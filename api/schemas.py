from dataclasses import dataclass
from enum import Enum
from typing import List

class ServiceStatus(Enum):
    ALL = 'all'
    RUNNING = 'running'
    DOWN = 'down'

class ServiceImage(Enum):
    GO_WPP_WITH_PROXY = 'go-whatsapp-proxy'
    GO_WPP_ORIGINAL = 'aldinokemal2104/go-whatsapp-web-multidevice:latest'

@dataclass
class Service:
    image: str
    name: str
    main_external_port: int
    nickname: str = ''
    main_internal_port: int = 8080
    env: dict = None
    image_aliases: List[str] = None

    @property
    def ports(self):
        return {
            f'{self.main_internal_port}/tcp': self.main_external_port,
        }