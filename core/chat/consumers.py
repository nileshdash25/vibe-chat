import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import OnlineUser, ChatMessage
from .utils import sanitize_message  # 🔥 Import Filter Logic

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        # Disconnect hone par user ko remove karo aur list update karo
        await self.remove_online_user()
        await self.broadcast_online_users()

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        # --- 1. SETUP (USER JOIN) ---
        if msg_type == 'setup':
            self.user_name = data.get('user_name')
            self.user_age = data.get('user_age', 'N/A')
            self.user_gender = data.get('user_gender', 'N/A')
            
            # Personal group (Private chat ke liye)
            self.personal_group = f"user_{self.user_name.replace(' ', '_')}"
            
            # Global Chat Group Join
            await self.channel_layer.group_add("global_chat", self.channel_name)
            # Personal Group Join
            await self.channel_layer.group_add(self.personal_group, self.channel_name)
            
            # DB mein add karo
            await self.add_online_user(self.user_name, self.user_age, self.user_gender, self.channel_name)
            
            # Sabko batao ki naya banda aaya hai
            await self.broadcast_online_users()

        # --- 2. MESSAGE HANDLING (GLOBAL & PRIVATE) ---
        elif msg_type == 'chat_message' or msg_type == 'private_message':
            raw_message = data.get('message', '')
            
            # 🔥 STEP 1: Message ko Sanitize (Clean) karo 🔥
            clean_message = sanitize_message(raw_message)
            
            target_group = "global_chat"
            is_private = False
            
            if msg_type == 'private_message':
                target_user = data.get('target_user')
                if target_user:
                    target_group = f"user_{target_user.replace(' ', '_')}"
                    is_private = True

            # 🔥 STEP 2: Database mein Clean Message Save karo
            await self.save_message(self.user_name, clean_message, is_private)

            payload = {
                'type': 'chat_message',
                'message': clean_message, # Clean message bhejo
                'user': self.user_name,
                'is_private': is_private
            }
            
            # 🔥 STEP 3: Target Group ko bhejo
            await self.channel_layer.group_send(target_group, payload)
            
            # Agar private hai, toh sender ko bhi dikhna chahiye (echo)
            if is_private:
                await self.channel_layer.group_send(self.personal_group, payload)

    # --- HANDLERS (Events receive karne ke liye) ---

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def send_user_list(self, event):
        await self.send(text_data=json.dumps(event))

    async def broadcast_online_users(self):
        users_data = await self.get_online_users()
        count = len(users_data)
        await self.channel_layer.group_send(
            "global_chat", 
            {
                'type': 'send_user_list', 
                'users': users_data,
                'count': count
            }
        )

    # --- DATABASE OPERATIONS (Async) ---

    @database_sync_to_async
    def add_online_user(self, name, age, gender, channel):
        # Purana record hatao taaki duplicate na ho
        OnlineUser.objects.filter(guest_name=name).delete()
        OnlineUser.objects.create(guest_name=name, age=age, gender=gender, channel_name=channel)

    @database_sync_to_async
    def remove_online_user(self):
        if hasattr(self, 'user_name'):
            OnlineUser.objects.filter(guest_name=self.user_name).delete()

    @database_sync_to_async
    def get_online_users(self):
        return list(OnlineUser.objects.values('guest_name', 'age', 'gender'))

    @database_sync_to_async
    def save_message(self, username, message, is_private):
        # Message History Save karne ke liye
        # Agar user registered hai toh User object link kar sakte ho, 
        # filhal string username save kar rahe hain simple rakhne ke liye.
        ChatMessage.objects.create(
            sender=username, # Yahan guest name ya username aayega
            message=message,
            room_name="private" if is_private else "global",
            timestamp=timezone.now()
        )