import os
import sys
import dj_database_url
from pathlib import Path

# 1. Base Directory Setup
# File location: django_chat/core/core/settings.py
# BASE_DIR pointing to: django_chat/
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# --- PATH FIX FOR NESTED APPS ---
# Isse Python ko 'core' folder ke andar wale apps (chat, etc.) mil jayenge
sys.path.append(os.path.join(BASE_DIR, 'core'))
sys.path.append(os.path.join(BASE_DIR, 'core', 'core'))

# 2. Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 3. Application Definition
INSTALLED_APPS = [
    'jazzmin',             # Admin Theme (Top pe hona chahiye)
    'daphne',              # ASGI Server
    'channels',            # WebSockets
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chat',                # Tera Main App
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files serve karne ke liye
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'chat.middleware.UpdateLastSeenMiddleware',
]

# --- URL & APPLICATION CONFIG ---
ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application'

# --- TEMPLATES CONFIGURATION (Ye missing tha, iske bina crash hoga) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 4. Database (PostgreSQL for Render)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# 5. Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# 6. Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 7. Static & Media Files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Whitenoise storage (Compression ke liye)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 8. Channel Layers (In-memory for development)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# 9. Email & Login Settings
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
LOGIN_URL = 'login_user'  
LOGIN_REDIRECT_URL = 'chat_room'

# 10. Jazzmin Admin Customization
JAZZMIN_SETTINGS = {
    "site_title": "Pro Chat Admin",
    "site_header": "Nilesh Dashboard",
    "site_brand": "⚡ PRO CHAT",
    "welcome_sign": "Welcome, Nilesh!",
    "copyright": "Nilesh Dash 2026",
    "user_avatar": "profile.avatar",
    "icons": {
        "auth.user": "fas fa-user",
        "chat.ChatMessage": "fas fa-comments",
        "chat.Profile": "fas fa-id-card",
    },
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index"},
        {"name": "Go to Chat", "url": "/chat/", "new_window": True},
    ],
    "show_ui_builder": False,
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}