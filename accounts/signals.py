# accounts/signals.py

from datetime import datetime
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from Admin_app.models import UserDetails


def _save_google_user(sociallogin):
    if sociallogin.account.provider != 'google':
        return

    extra_data = sociallogin.account.extra_data
    full_name  = extra_data.get('name', '').strip()
    email      = extra_data.get('email', '').strip()

    print(f"🟢 Google user detected: {full_name} | {email}")  # ← debug

    if not email:
        print("❌ No email found in Google data")
        return

    existing = UserDetails.objects.filter(user_email=email).first()

    if existing:
        print(f"✅ Existing user found → updating name")
        existing.user_name = full_name or existing.user_name
        existing.save()
    else:
        print(f"✅ New user → creating UserDetails record")
        UserDetails.objects.create(
            user_name          = full_name,
            user_email         = email,
            user_phone         = None,
            user_city          = None,
            user_password      = '',
            user_register_date = datetime.today().date(),
            user_register_time = datetime.now().time(),
        )


@receiver(social_account_added)
def on_google_signup(sender, request, sociallogin, **kwargs):
    print("🔔 social_account_added signal fired")   # ← debug
    _save_google_user(sociallogin)
    request.session['show_complete_profile'] = True


@receiver(social_account_updated)
def on_google_return(sender, request, sociallogin, **kwargs):
    print("🔔 social_account_updated signal fired")  # ← debug
    _save_google_user(sociallogin)


@receiver(user_logged_in)
def set_custom_session(sender, request, user, **kwargs):
    print(f"🔔 user_logged_in signal fired for: {user.email}")  # ← debug
    try:
        user_details = UserDetails.objects.get(user_email=user.email)
        request.session['User_id']   = str(user_details.id)
        request.session['user_type'] = 'User'
        request.session.modified     = True
        print(f"✅ Session set → User_id: {user_details.id}")

        if not user_details.user_phone:
            request.session['show_complete_profile'] = True

    except UserDetails.DoesNotExist:
        print(f"❌ UserDetails not found for email: {user.email}")