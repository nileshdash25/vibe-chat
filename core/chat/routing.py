from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Ab ye kisi bhi room name ko accept karega (jese 'global' ya 'user_nilesh')
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
]