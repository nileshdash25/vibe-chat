import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import sanitize_message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL se Room Name nikalo (Jo routing.py ne pakda hai)
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Group mein add karo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Group se remove karo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get("type")

        # --- MESSAGE ---
        if msg_type == "chat_message":
            raw_message = data.get("message", "")
            user = data.get("user", "Anonymous")

            # XSS attack se bachne ke liye sanitize
            clean_message = sanitize_message(raw_message)

            payload = {
                "type": "chat_message",
                "message": clean_message,
                "user": user,
            }

            # Sirf usi room mein bhejo jahan user hai
            await self.channel_layer.group_send(
                self.room_group_name,
                payload
            )

    async def chat_message(self, event):
        # Frontend ko wapas bhejo
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "user": event["user"]
        }))