from django.contrib.auth.backends import ModelBackend
from .models import UserProfile  # Ensure it's using the correct custom User model
# from django.contrib.auth import get_user_model

# User = get_user_model()
#from accounts.models import User
class EmailAuthBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        print(f"Authenticating {email}...")  # Add debugging
        try:
            user = UserProfile.objects.get(email=email)
            print(f"Found user: {user}")  # Print user if found
        except UserProfile.DoesNotExist:
            print(f"User with email {email} does not exist.")
            return None
        print(f"Checking password for {password}...")
        if user.check_password(password):
            print("Password is correct.")
            return user
        else:
            print("Incorrect password.")
            return None

    def get_user(self, user_id):
        try:
            return UserProfile.objects.get(pk=user_id)
        except UserProfile.DoesNotExist:
            return None
