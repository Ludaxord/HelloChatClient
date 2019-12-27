from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from HelloChatClient.channels_app import consumers

websocket_pattern = [
    url(r'^ws/chat$', consumers.ChatConsumer)
]

application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(URLRouter(websocket_pattern))
})
