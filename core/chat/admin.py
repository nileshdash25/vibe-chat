from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, ChatMessage
from django.db.models import Count
from django.utils.html import format_html
from .models import AdminInquiry
# --- 1. PROFILE ADMIN (Dashboard Analytics Setup) ---
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_avatar', 'user', 'badge', 'gender', 'age', 'is_guest', 'is_online_status', 'last_seen')   
    list_editable = ('badge', 'is_guest', 'gender')
    list_filter = ('is_guest', 'gender', 'last_seen')
    search_fields = ('user__username', 'user__email')

    # Avatar preview in list
    def user_avatar(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="width: 35px; height: 35px; border-radius: 50%;" />', obj.avatar.url)
        return "No Image"
    
    def is_online_status(self, obj):
        return obj.is_online()
    is_online_status.boolean = True
    is_online_status.short_description = "Online Now"

admin.site.register(Profile, ProfileAdmin)

# --- 2. CHAT MESSAGE ADMIN (Filter by Sender/Receiver) ---
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'short_message', 'is_read', 'has_file', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__username', 'receiver__username', 'message')

    def short_message(self, obj):
        return obj.message[:30] + "..." if obj.message else "No text"
    
    def has_file(self, obj):
        return bool(obj.file)
    has_file.boolean = True

admin.site.register(ChatMessage, ChatMessageAdmin)

# --- 3. CUSTOM USER ADMIN (Inline Profile) ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'is_active', 'last_login', 'date_joined')
    
    # Block/Unblock action
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = "✅ Activate selected users"

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = "🚫 Block selected users"

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.unregister(Group) 

# --- 4. ADMIN INQUIRY MODEL & ADMIN ---
class AdminInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'timestamp', 'is_resolved')
    list_filter = ('is_resolved', 'timestamp')
    search_fields = ('name', 'email', 'message')

admin.site.register(AdminInquiry, AdminInquiryAdmin)
