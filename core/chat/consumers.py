import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import sanitize_message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Global chat group
        await self.channel_layer.group_add(
            "global_chat",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "global_chat",
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        # --- MESSAGE ---
        if msg_type == "chat_message":
            raw_message = data.get("message", "")
            user = data.get("user", "Anonymous")

            clean_message = sanitize_message(raw_message)

            payload = {
                "type": "chat_message",
                "message": clean_message,
                "user": user,
            }

            await self.channel_layer.group_send(
                "global_chat",
                payload
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
