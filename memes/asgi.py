"""
ASGI config for memes project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.routing import URLRouter

from django.urls import path

import os
from django.core.asgi import get_asgi_application

from general.consumers import WebConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memes.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter([
            path('ws', WebConsumer.as_asgi())
        ])
    )
})
