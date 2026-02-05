from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ROOT
    path("", views.home, name="home"),

    # CHAT
    path("chat/", include("chat.urls")),

    # AUTH
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
