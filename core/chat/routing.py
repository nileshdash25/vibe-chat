from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 'as_view()' ki jagah 'as_asgi()' likho
    re_path(r'ws/chat/$', consumers.ChatConsumer.as_asgi()), 
]