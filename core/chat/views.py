import random
from datetime import timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout, login 
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatMessage, Profile
from .forms import EmailRegistrationForm, ProfileUpdateForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import update_session_auth_hash
from .models import AdminInquiry
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .utils import sanitize_message
# --- 1. CHAT ROOM & AUTO CLEANUP ---

@login_required(login_url='login_user')
def chat_room(request, username=None):
    time_threshold = timezone.now() - timedelta(minutes=10)
    users = User.objects.filter(profile__last_seen__gte=time_threshold).exclude(id=request.user.id)
    total_online = users.count() + 1 

    chat_partner = None
    messages_list = []

    # Cleanup Global
    ChatMessage.objects.filter(receiver=None, timestamp__lt=timezone.now() - timedelta(hours=12)).delete()

    # Unread Counts
    unread_data = {}
    for u in User.objects.exclude(id=request.user.id):
        count = ChatMessage.objects.filter(sender=u, receiver=request.user, is_read=False).count()
        if count > 0:
            unread_data[u.username] = count

    if username:
        chat_partner = get_object_or_404(User, username=username)
        # Mark as Read
        ChatMessage.objects.filter(sender=chat_partner, receiver=request.user, is_read=False).update(is_read=True)
        unread_data.pop(chat_partner.username, None)

        messages_list = ChatMessage.objects.filter(
            Q(sender=request.user, receiver=chat_partner) |
            Q(sender=chat_partner, receiver=request.user)
        ).order_by('timestamp')
    else:
        messages_list = ChatMessage.objects.filter(receiver=None).order_by('timestamp')

    Profile.objects.update_or_create(user=request.user, defaults={'last_seen': timezone.now()})

    # Check if blocked (Initial Load)
    is_blocked_by_me = False
    if chat_partner and request.user.profile.blocked_users.filter(id=chat_partner.profile.id).exists():
        is_blocked_by_me = True

    return render(request, 'chat/room.html', {
        'users': users,
        'messages': messages_list,
        'chat_partner': chat_partner,
        'current_user': request.user,
        'total_online': total_online,
        'unread_db_counts': unread_data,
        'is_guest': request.user.profile.is_guest,
        'is_blocked_initial': is_blocked_by_me # Initial status for template
    })

# --- 2. SEND MESSAGE ---
@login_required
def send_message(request, username=None):
    if request.method == 'POST':
        msg = request.POST.get('message')
        file = request.FILES.get('file_upload')

        receiver = None
        if username:
            receiver = get_object_or_404(User, username=username)
            
            # 🔥 FIX: Agar Block hai (Dono taraf se), toh message mat bhejo
            # 1. Usne mujhe block kiya hai
            if receiver.profile.blocked_users.filter(id=request.user.profile.id).exists():
                messages.error(request, "🚫 Message failed! You are blocked.")
                return redirect('private_chat', username=username)
            
            # 2. Maine usse block kiya hai
            if request.user.profile.blocked_users.filter(id=receiver.profile.id).exists():
                messages.error(request, "🚫 Unblock user to send message.")
                return redirect('private_chat', username=username)

        if msg or file:
            clean_msg = sanitize_message(msg) if msg else ""

            ChatMessage.objects.create(
                sender=request.user,
                receiver=receiver,
                message=clean_msg,
                file=file
            )

    return redirect('private_chat', username=username) if username else redirect('chat_room')

# --- BLOCK USER ---

@login_required
def block_user(request, username):
    partner = get_object_or_404(User, username=username)
    profile = request.user.profile
    
    if profile.blocked_users.filter(id=partner.profile.id).exists():
        profile.blocked_users.remove(partner.profile)
        status = 'unblocked'
    else:
        profile.blocked_users.add(partner.profile)
        status = 'blocked'
        
    return JsonResponse({'status': status})

# --- 3. GUEST LOGIN (FIXED GENDER BUG) ---
def set_guest_name(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        gender_input = request.POST.get('gender')
        age_input = request.POST.get('age')
        
        if not nickname: 
            messages.error(request, "❌ Name cannot be empty.")
            return redirect('login_user')

        if not gender_input:
            messages.error(request, "❌ Please select a Gender.")
            return redirect('login_user')

        existing_user = User.objects.filter(username=nickname).first()
        if existing_user:
            if existing_user.email:
                messages.error(request, "❌ This name is reserved for a Member.")
                return redirect('login_user')
            
            time_threshold = timezone.now() - timedelta(minutes=10)
            try:
                if existing_user.profile.last_seen > time_threshold:
                    messages.error(request, f"❌ '{nickname}' is currently online!")
                    return redirect('login_user')
                else:
                    existing_user.delete()
            except:
                existing_user.delete()

        user = User.objects.create_user(username=nickname, email='', password=None)
        
        login(request, user)

        try:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.gender = gender_input
            profile.last_seen = timezone.now()
            profile.save()
        except Exception as e:
            print(f"❌ Profile Error: {e}")

        request.session['guest_name'] = nickname
        request.session['is_guest'] = True
        return redirect('chat_room')
        
    return redirect('login_user')

# --- 4. MEMBER LOGIN & CLEANUP ---
def login_view(request):
    try:
        now = timezone.now()
        guest_limit = now - timedelta(hours=24)
        User.objects.filter(email='', profile__last_seen__lt=guest_limit).delete()

        member_limit = now - timedelta(days=90)
        User.objects.exclude(is_superuser=True).filter(
            email__contains='@', 
            last_login__lt=member_limit
        ).delete()
    except Exception as e:
        print(f"⚠️ Cleanup Error: {e}")

    if request.user.is_authenticated:
        return redirect('chat_room')

    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')
        
        user = None
        if '@' in login_input:
            try:
                u = User.objects.get(email=login_input)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=login_input, password=password)

        if user is not None:
            login(request, user)
            Profile.objects.update_or_create(user=user, defaults={'last_seen': timezone.now()})
            request.session['is_guest'] = False
            return redirect('chat_room')
        else:
            return render(request, 'chat/get_name.html', {'error': 'Invalid Credentials'})
            
    return render(request, 'chat/get_name.html')

# --- 5. REGISTRATION & OTP ---
# Sabse upar imports mein ye line honi chahiye:
# from django.contrib.auth import logout as auth_logout

def register_view(request):
    # 🔥 FIX 2: Logout aur Reload 🔥
    # Agar koi user (Guest/Member) login hai, toh pehle logout karo
    if request.user.is_authenticated:
        logout(request)
        # Logout ke baad turant page reload karo taaki session clear ho jaye
        return redirect('register_user') 

    if request.method == 'POST':
        form = EmailRegistrationForm(request.POST)
        gender_input = request.POST.get('gender')

        if form.is_valid():
            user_data = form.cleaned_data
            email = user_data['email']
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "❌ Email already registered.")
                return render(request, 'chat/register.html', {'form': form})
            
            if not gender_input:
                messages.error(request, "❌ Please select a Gender.")
                return render(request, 'chat/register.html', {'form': form})

            request.session['reg_username'] = user_data['username']
            request.session['reg_email'] = email
            request.session['reg_password'] = user_data['password1']
            request.session['reg_gender'] = gender_input 
            
            otp = random.randint(1000, 9999)
            request.session['reg_otp'] = otp
            try: 
                send_mail('Verify OTP', f'OTP: {otp}', 'admin@chat.com', [email], fail_silently=False)
            except: 
                pass
            return redirect('verify_otp')
    else:
        form = EmailRegistrationForm()
    
    return render(request, 'chat/register.html', {'form': form})

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('reg_otp')
        
        # 1. OTP Check (int conversion safety ke saath)
        try:
            is_valid = generated_otp and int(entered_otp) == int(generated_otp)
        except:
            is_valid = False

        if is_valid:
            # 2. User Create karo
            user = User.objects.create_user(
                username=request.session['reg_username'],
                email=request.session['reg_email'],
                password=request.session['reg_password']
            )
            
            # 3. Login se pehle purana GUEST session saaf karo (Important!)
            # Isse redirect wala panga hamesha ke liye khatam ho jayega
            auth_login(request, user) 
            
            user_gender = request.session.get('reg_gender', 'Male')
            
            # 4. Profile Logic (get_or_create ki jagah update_or_create use karo)
            Profile.objects.update_or_create(
                user=user,
                defaults={
                    'gender': user_gender,
                    'is_guest': False, # Pakka member ban gaya
                    'last_seen': timezone.now()
                }
            )

            # 5. Session Safaya (Kachra saaf)
            keys_to_del = ['reg_otp', 'reg_username', 'reg_email', 'reg_password', 'reg_gender', 'is_guest']
            for key in keys_to_del:
                if key in request.session:
                    del request.session[key]
            
            messages.success(request, "✅ Account verified! Welcome to Pro Chat.")
            return redirect('chat_room')
        else:
            messages.error(request, "❌ Invalid OTP. Try again.")
            
    return render(request, 'chat/verify_otp.html')

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login_user')

# --- 6. PASSWORD RESET ---
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            otp = random.randint(1000, 9999)
            request.session['reset_email'] = email
            request.session['reset_otp'] = otp
            try: send_mail('Reset Password OTP', f'OTP: {otp}', 'admin@chat.com', [email], fail_silently=False)
            except: pass
            return redirect('reset_verify_otp')
        else:
            messages.error(request, "❌ No user found.")
    return render(request, 'chat/forgot_password.html')

def reset_verify_otp_view(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('reset_otp')
        if generated_otp and int(entered_otp) == generated_otp:
            request.session['otp_verified'] = True
            return redirect('reset_new_password')
        else:
            messages.error(request, "❌ Invalid OTP.")
    return render(request, 'chat/reset_verify_otp.html')

def reset_new_password_view(request):
    if not request.session.get('otp_verified'): return redirect('forgot_password')
    if request.method == 'POST':
        p1 = request.POST.get('pass1')
        p2 = request.POST.get('pass2')
        if p1 == p2:
            email = request.session.get('reset_email')
            user = User.objects.get(email=email)
            user.set_password(p1)
            user.save()
            del request.session['reset_email']
            del request.session['reset_otp']
            del request.session['otp_verified']
            messages.success(request, "✅ Password Reset Successful!")
            return redirect('login_user')
        else:
            messages.error(request, "❌ Passwords do not match.")
    return render(request, 'chat/reset_new_password.html')

# --- 7. PROFILE UPDATE ---
@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # 🔥 Check Database Value
    is_guest_mode = profile.is_guest 

    if request.method == 'POST':
        # 🛑 STOP: Agar Database mein 'Is Guest' Tick hai, toh yahi rok do
        if is_guest_mode:
            messages.error(request, "Guest users cannot edit profile!")
            return redirect('profile_view')

        # --- UPDATE LOGIC (Sirf Members ke liye) ---
        if request.FILES.get('avatar'):
            profile.avatar = request.FILES['avatar']
        
        gender = request.POST.get('gender')
        age = request.POST.get('age')
        
        if gender: profile.gender = gender
        if age: profile.age = age
        
        profile.save()

        # Password Update
        new_pass = request.POST.get('password')
        if new_pass:
            request.user.set_password(new_pass)
            request.user.save()
            update_session_auth_hash(request, request.user)

        messages.success(request, "Profile Updated Successfully!")
        return redirect('chat_room')

    # Template ko batao ki ye Guest hai ya nahi
    return render(request, 'chat/profile.html', {
        'profile': profile,
        'is_guest_mode': is_guest_mode 
    })

# --- 8. DB FIXER ---
def force_fix_db(request):
    from .models import Profile
    count = 0
    for u in User.objects.all():
        prof, created = Profile.objects.get_or_create(user=u)
        if 'simran' in u.username.lower():
            prof.gender = 'Female'
            count += 1
        elif not prof.gender or prof.gender == 'None':
            prof.gender = 'Male'
        prof.save()
    return HttpResponse(f"✅ Fixed {count} users.")

# --- 9. FETCH MESSAGES & TYPING STATUS ---
@login_required
def fetch_messages(request, username=None):
    partner = None
    raw_id = request.GET.get('last_id', '0')
    try: last_id = int(float(raw_id)) if raw_id not in ['undefined', 'null', ''] else 0
    except: last_id = 0
    
    msgs = []
    is_blocked_by_me = False
    is_blocked_by_them = False

    if username:
        partner = get_object_or_404(User, username=username)
        ChatMessage.objects.filter(sender=partner, receiver=request.user, is_read=False).update(is_read=True)
        
        msgs = ChatMessage.objects.filter(
            (Q(sender=request.user, receiver=partner) | Q(sender=partner, receiver=request.user)),
            id__gt=last_id
        ).order_by('timestamp')

        if request.user.profile.blocked_users.filter(id=partner.profile.id).exists():
            is_blocked_by_me = True
        
        if partner.profile.blocked_users.filter(id=request.user.profile.id).exists():
            is_blocked_by_them = True

    else:
        msgs = ChatMessage.objects.filter(receiver=None, id__gt=last_id).order_by('timestamp')

    data = []
    for m in msgs:
        file_url = m.file.url if m.file else None
        is_img = False
        is_audio = False # 🔥 Added for Voice Note
        
        if m.file:
            try:
                fname = m.file.name.lower()
                if fname.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    is_img = True
                elif fname.endswith(('.mp3', '.wav', '.ogg', '.webm')):
                    is_audio = True
            except: pass

        data.append({
            "id": m.id,
            "sender": m.sender.username,
            "message": m.message or "",
            "file_url": file_url,
            "is_image": is_img,
            "is_audio": is_audio,
            "time": m.timestamp.strftime("%H:%M"),
            "is_me": m.sender == request.user,
            "is_read": m.is_read,
            # 🔥 BADGE DATA ADDED HERE
            "badge": m.sender.profile.badge, 
            "badge_display": m.sender.profile.get_badge_display()
        })

    unread_counts = {}
    active_senders = ChatMessage.objects.filter(receiver=request.user, is_read=False).values_list('sender__username', flat=True).distinct()
    for sender in active_senders:
        unread_counts[sender] = ChatMessage.objects.filter(sender__username=sender, receiver=request.user, is_read=False).count()

    return JsonResponse({
        "messages": data,
        "notifications": unread_counts,
        "partner_typing": partner.profile.is_typing if partner else False,
        "is_blocked_by_me": is_blocked_by_me,   
        "is_blocked_by_them": is_blocked_by_them 
    })
@login_required
def update_typing_status(request):
    status = request.GET.get('status') == 'true'
    Profile.objects.filter(user=request.user).update(is_typing=status)
    return JsonResponse({'status': 'ok'})

# --- 10. CONTACT ADMIN ---

def contact_admin(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        msg = request.POST.get('message')
        
        if name and email and msg:
            AdminInquiry.objects.create(name=name, email=email, subject=subject, message=msg)
            messages.success(request, "✅ Your message has been sent to Admin!")
        else:
            messages.error(request, "❌ Please fill all fields.")
            
    return redirect('login_user')

# -- 11. ANALYTICS VIEW FOR ADMIN ---

@staff_member_required # Sirf Admin/Staff dekh payega
def analytics_view(request):
    # 1. Total Counts
    total_users = User.objects.count()
    total_messages = ChatMessage.objects.count()
    total_guests = Profile.objects.filter(is_guest=True).count()
    total_members = total_users - total_guests

    # 2. Activity Data (Last 5 active users)
    active_users = Profile.objects.order_by('-last_seen')[:5]

    context = {
        'total_users': total_users,
        'total_messages': total_messages,
        'total_guests': total_guests,
        'total_members': total_members,
        'active_users': active_users,
    }
    return render(request, 'chat/analytics.html', context)