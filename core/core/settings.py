import os
from pathlib import Path
import dj_database_url
import socket

# Force IPv4 to fix [Errno 101] Network is unreachable on Railway
#socket.getaddrinfo = lambda *args, **kwargs: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-change-this")
DEBUG = os.environ.get("DEBUG", "False") == "True"
ALLOWED_HOSTS = ['*']

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    "jazzmin",
    "daphne",
    "channels",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "chat",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",

    "chat.middleware.UpdateLastSeenMiddleware",

]

# --------------------------------------------------
# URL / ASGI / WSGI
# --------------------------------------------------
ASGI_APPLICATION = "core.asgi.application"
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"




# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# --------------------------------------------------
# DATABASE (Railway Safe)
# --------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }






# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA FILES
# --------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --------------------------------------------------
# DEFAULT PK
# --------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# CHANNELS (Redis optional)
# --------------------------------------------------
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": os.getenv(
            "CHANNEL_BACKEND",
            "channels.layers.InMemoryChannelLayer",
        )
    }
}

# --------------------------------------------------
# AUTH
# --------------------------------------------------
LOGIN_URL = "login_user"
LOGIN_REDIRECT_URL = "chat_room"

# Email Configuration
import os

# --- EMAIL CONFIGURATION (BREVO SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 2525
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_TIMEOUT = 60

# Auth Credentials (Railway Variables se aayenge)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Sender Email (Ye tera Gmail hona chahiye jo verified hai)
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'sipunashish11@gmail.com')

# --------------------------------------------------
# JAZZMIN
# --------------------------------------------------
JAZZMIN_SETTINGS = {
    "site_title": "Pro Chat Admin",
    "site_header": "Nilesh Dashboard",
    "site_brand": "PRO CHAT",
    "welcome_sign": "Welcome, Nilesh!",
    "copyright": "Nilesh Dash 2026",
    "icons": {
        "auth.user": "fas fa-user",
        "chat.ChatMessage": "fas fa-comments",
        "chat.Profile": "fas fa-id-card",
    },
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}
# CSRF Trust for Railway
CSRF_TRUSTED_ORIGINS = [
    "https://vibe-chat-production-54e5.up.railway.app",
]
# --- RAILWAY SECURITY FIX (ISKE BINA PHONE PE NAHI CHALEGA) ---
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True