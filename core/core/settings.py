import os
import sys
import dj_database_url
from pathlib import Path

# 1. Base Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Nested structure fix
# Purani line hata kar ye daal de
sys.path.append(os.path.join(BASE_DIR, 'core'))
sys.path.append(os.path.join(BASE_DIR, 'core', 'core'))

# 2. Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 3. Application Definition
INSTALLED_APPS = [
    'jazzmin',
    'daphne',      
    'channels',    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chat',        
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Static files ke liye zaroori
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'chat.middleware.UpdateLastSeenMiddleware',
]

ROOT_URLCONF = 'core.core.urls'

# 4. Database (PostgreSQL for Render)
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600
    )
}

# 5. Static Files (Production ready)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 6. Channel Layers (Production ke liye Redis chahiye hota hai par abhi InMemory rakhte hain)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# 7. Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# 8. Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 9. Static & Media Files (For Photo/Video Sharing)
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 10. Channel Layers (In-memory for development)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
# --- Email Settings ---
# Testing ke liye (OTP Terminal mein aayega):
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Jab Live karna ho (Gmail ke liye), upar wali line hata kar ye use karna:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password' # Google App Password
# Agar user bina login kiye chat page kholta hai, toh yahan bhejo
LOGIN_URL = 'login_user'  

# Login hone ke baad kahan jana hai
LOGIN_REDIRECT_URL = 'chat_room'

# --- Jazzmin Admin Customization ---
JAZZMIN_SETTINGS = {
    "site_title": "Pro Chat Admin",
    "site_header": "Nilesh Dashboard",
    "site_brand": "⚡ PRO CHAT",
    "welcome_sign": "Welcome, Nilesh!",
    "copyright": "Nilesh Dash 2026",
    "user_avatar": "profile.avatar", # User ka avatar sidebar mein dikhega

    # Sidebar Icons
    "icons": {
        "auth.user": "fas fa-user",
        "chat.ChatMessage": "fas fa-comments",
        "chat.Profile": "fas fa-id-card",
    },

    # Quick links top menu
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index"},
        {"name": "Go to Chat", "url": "/chat/", "new_window": True},
    ],
    
    "show_ui_builder": False, # Design final hone ke baad band kar sakte ho
}

JAZZMIN_UI_TWEAKS = {
    "theme": "darkly",   # 🔥 Dark Theme default rahega
    "dark_mode_theme": "darkly",
}
LOGIN_REDIRECT_URL = 'chat_room'