from django.urls import path
from . import views

urlpatterns = [
    # --- CHAT ROOMS ---
    path('', views.chat_room, name='chat_room'),
    
    path('chat/<str:username>/', views.chat_room, name='private_chat'),
    
    # --- AUTH URLS ---
    path('get-name/', views.set_guest_name, name='set_guest_name'),
    path('register/', views.register_view, name='register_user'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_view, name='login_user'),
    path('logout/', views.logout_view, name='custom_logout'),
    path('profile/', views.profile_view, name='profile_view'),
    
    # --- PASSWORD RESET ---
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-verify-otp/', views.reset_verify_otp_view, name='reset_verify_otp'),
    path('new-password/', views.reset_new_password_view, name='reset_new_password'),

    # --- MESSAGE SENDING ---
    path('send_global/', views.send_message, name='send_global'),
    path('send_private/<str:username>/', views.send_message, name='send_private'),
    path('fix-db/', views.force_fix_db, name='fix_db'),

      #-- MESSAGE FETCHING ---  
    path('fetch/', views.fetch_messages, name='fetch_messages'),  # Yeh missing tha!
    path('fetch/<str:username>/', views.fetch_messages, name='fetch_messages_user'),

    path('update_typing/', views.update_typing_status, name='update_typing'),
    path('contact_admin/', views.contact_admin, name='contact_admin'),
    path('block_user/<str:username>/', views.block_user, name='block_user'),

    # --- ADMIN ANALYTICS DASHBOARD ---
    path('analytics/', views.analytics_view, name='analytics_dashboard'),
]