from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from .models import Profile

class UpdateLastSeenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 🔥 FIX 1: In pages ko ignore karo (Bawasir Prevention) 🔥
        # Agar user register ya login kar raha hai, toh middleware beech mein nahi aayega
        exempt_urls = [
            '/admin/', 
            '/chat/login/', 
            '/chat/register/', 
            '/chat/logout/', 
            '/chat/get-name/'
        ]
        
        # Agar current URL inmein se koi hai, toh seedha aage badho
        if any(request.path.startswith(url) for url in exempt_urls):
            return self.get_response(request)

        # --- Normal Logic (Sirf Chatting ke liye) ---
        if request.user.is_authenticated:
            # Profile safety check
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            last_activity = profile.last_seen
            now = timezone.now()

            # Session Timeout Logic (10 Mins)
            if last_activity:
                diff = (now - last_activity).total_seconds()
                if diff > 600:
                    logout(request)
                    messages.error(request, "⚠️ Session Expired! You were inactive for 10 minutes.")
                    return redirect('login_user')

            # Time update
            Profile.objects.filter(user=request.user).update(last_seen=now)

        return self.get_response(request)