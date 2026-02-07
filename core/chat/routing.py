from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Ye change zaroori hai taaki 'global' ya kisi bhi room name ko server samajh sake
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]