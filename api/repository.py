
from .schemas import Service

SERVICES = [
    Service(
        nickname='go-whatsapp-web-multidevice',
        image='aldinokemal2104/go-whatsapp-web-multidevice:latest',
        name='go-whatsapp-web-multidevice',
        main_internal_port=3000,
        main_external_port=8080,
        env={
                'OS_NAME': 'Chrome',
                'PORT': 3000,
                'DEBUG': 'False',
                'AUTOREPLY': 'Obrigado por enviar mensagem.',
            },
        image_aliases=['go-whatsapp, aldinokemal2104/go-whatsapp-web-multidevice:latest, go-whatsapp-web-multidevice'],
    ),
    Service(
        nickname='go-whatsapp-proxy',
        image='go-whatsapp-proxy',
        name='go-whatsapp-proxy',
        main_internal_port=3000,
        main_external_port=8080,
        env={
                'OS_NAME': 'Chrome',
                'PORT': 3000,
                'DEBUG': 'False',
            },
        image_aliases=['go-whatsapp-proxy'],
    ),
]

