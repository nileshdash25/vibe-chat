import os
from pathlib import Path

# 1. Base Directory Setup
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Security Settings (Development Mode)
SECRET_KEY = 'django-insecure-your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = ['*']

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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'chat.middleware.UpdateLastSeenMiddleware',
    
]

ROOT_URLCONF = 'core.urls'

# 4. Template Configuration (Fixes admin.E403 error)
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

# 5. ASGI & WSGI Setup
WSGI_APPLICATION = 'core.wsgi.application'
ASGI_APPLICATION = 'core.asgi.application' # Daphne/Channels ke liye

# 6. Database (SQLite3)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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