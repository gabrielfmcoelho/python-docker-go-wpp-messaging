import random

def generate_proxy_url():
    port = random.randint(10000, 11000)
    proxy_url = f"http://0b0a288b055c448171f1__cr.br;state.maranhao:46ecbec34ae82226@gw.dataimpulse.com:{port}"
    return proxy_url

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
                'AUTOREPLY': 'Obrigado por enviar mensagem.',
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
                'PORT': 3000,
                'DEBUG': 'False',
                'AUTOREPLY': 'Obrigado por enviar mensagem.',
                'PROXY_URL': generate_proxy_url(),
                'WEBHOOK': 'http://localhost:3000',
            },
        image_aliases=['go-whatsapp-proxy'],
    ),
]

