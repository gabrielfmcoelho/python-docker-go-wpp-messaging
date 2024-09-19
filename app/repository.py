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
                'BASIC_AUTH': 'disparador:2024',
                'PORT': 3000,
                'DEBUG': 'False',
                'AUTOREPLY': 'Obrigado por entrar em contato.',
                'WEBHOOK': 'http://localhost:3000',
                'WEBHOOK_SECRET': 'secret',
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
                'BASIC_AUTH': 'disparador:2024',
                'PORT': 3000,
                'DEBUG': 'False',
                'AUTOREPLY': 'Obrigado por entrar em contato.',
                'PROXY_URL': 'socks5://0b0a288b055c448171f1__cr.br:46ecbec34ae82226@gw.dataimpulse.com:823',
                'WEBHOOK': 'http://localhost:3000',
                'WEBHOOK_SECRET': 'secret',
            },
        image_aliases=['go-whatsapp-proxy'],
    ),
]