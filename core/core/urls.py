from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static  # 🔥 YE IMPORT ZAROORI HAI

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chat.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
] 
# 🔥 YE LINE ADD KAR, TABHI PHOTO DIKHEGI 🔥
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)