import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import sanitize_message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL se 'room_name' uthany ke liye ye zaroori hai
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Dynamic group mein add karo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        if msg_type == "chat_message":
            raw_message = data.get("message", "")
            user = data.get("user", "Anonymous")
            clean_message = sanitize_message(raw_message)

            payload = {
                "type": "chat_message",
                "message": clean_message,
                "user": user,
            }

            # Ab ye sirf usi specific room mein message bhejega
            await self.channel_layer.group_send(
                self.room_group_name,
                payload
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))