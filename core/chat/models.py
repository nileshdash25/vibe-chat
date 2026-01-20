import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- CHAT MESSAGE MODEL ---
class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_messages')
    
    message = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # 🔥 For Blue Ticks
    is_read = models.BooleanField(default=False)

    def is_image(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return False

    def __str__(self):
        return f"{self.sender} -> {self.receiver}"

    class Meta:
        ordering = ['timestamp']

# --- PROFILE MODEL ---
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_seen = models.DateTimeField(default=timezone.now)
    is_typing = models.BooleanField(default=False)
    age = models.IntegerField(null=True, blank=True)
    is_guest = models.BooleanField(default=True) # Default True rakha hai naye users ke liye
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)
    
    gender = models.CharField(
        max_length=10, 
        choices=[('Male', 'Male'), ('Female', 'Female')], 
        blank=True, null=True
    )
    # Badge Choices
    BADGE_CHOICES = [
        ('Member', 'Member'),
        ('Admin', '👑 Admin'),
        ('VIP', '💎 VIP'),
        ('Verified', '✅ Verified'),
        ('Bot', '🤖 Bot'),
    ]
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default='Member')

    # 🔥 For Blocking Logic
    blocked_users = models.ManyToManyField('self', symmetrical=False, related_name='blocked_by', blank=True)

    def is_online(self):
        now = timezone.now()
        if self.last_seen:
            diff = now - self.last_seen
            if diff.total_seconds() < 120:
                return True
        return False

    def __str__(self):
        return f"{self.user.username} Profile"
    

# --- SIGNALS ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except:
        Profile.objects.create(user=instance)
# chat/models.py ke niche jodo

class AdminInquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False) # Nilesh ise check kar sakega

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"