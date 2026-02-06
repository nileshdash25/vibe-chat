from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve
from django.shortcuts import redirect

urlpatterns = [
    # 1. Sabse Pehle MEDIA (Images) check karo - Taaki ye block na ho
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # 2. Admin URL
    path("admin/", admin.site.urls),

    # 3. Chat App (Prefix 'chat/' lagaya taaki frontend se match kare)
    path("chat/", include("chat.urls")),

    # 4. Auth (Login/Logout)
    path("accounts/", include("django.contrib.auth.urls")),

    # 5. Root Redirect (Agar koi seedha site khole toh chat pe bhejo)
    path("", lambda request: redirect('chat/', permanent=True)),
]