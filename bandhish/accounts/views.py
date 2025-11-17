from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail

# Create your views here.

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .serializer import SimpleRegisterSerializer,EditUserSerializer,ChangePasswordSerializer
from rest_framework import status
from .models import UserProfile, UserRole
from random import randint

class LoginAPI(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        print(f"Authenticated user: {user}")  # Debugging line
        if user is None:
            return Response({"error": "Invalid email or password"}, status=400)
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "message": "Login successful",
            "user": {
                "email": user.email,
                "token": token.key,
                "name": user.name,
                "role": user.role_name.role_name if user.role_name else None,
                "company": user.company.company_name if user.company else None,
            }
        })


class SimpleRegisterAPI(APIView):
    def post(self, request):
        serializer = SimpleRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPassword(APIView):
    # def post(self, request):
    #     email = request.data.get('email')
    #     user = UserProfile.objects.filter(email=email).first()
    #     if user:
    #         #send otp to user email
    #         #create a otp and save it to user table
    #         otp = randint(1000, 9999)
    #         user.otp = otp
    #         user.otp_created = timezone.now()
    #         user.save(update_fields=['otp', 'otp_created'])
    #         #send otp to user email
    #         subject = 'Forgot Password OTP'
    #         message = f'Your OTP for resetting the password is: {otp}'
    #         email_from = settings.EMAIL_HOST_USER
    #         recipient_list = [email, ]
    #         send_mail(subject, message, email_from, recipient_list)
    #         return Response({'message':'Otp sent to your email'}, status=status.HTTP_200_OK)
    #     else:
    #         return Response({'error':'User not found'}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = UserProfile.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        # Generate and save OTP
        otp = randint(1000, 9999)
        user.otp = otp
        user.otp_created = timezone.now()
        user.save(update_fields=['otp', 'otp_created'])

        # Email details (Branding - Bandhish)
        subject = "Bandhish Studio - Password Reset OTP"

        html_message = f"""
        <html>
        <body>
            <h2 style="color:#2b2b2b;">Forgot Password Request</h2>
            <p>Dear {user.name or 'User'},</p>
            <p>Your OTP to reset your Bandhish Studio account password is:</p>
            <h1 style="color:#4A90E2; font-size: 32px;">{otp}</h1>
            <p>This OTP is valid for 10 minutes.</p>
            <p>If you did not request a password reset, please ignore this email.</p>
            <br>
            <p>Regards,<br><strong>Bandhish Studio Support Team</strong></p>
        </body>
        </html>
        """

        # From email (use Bandhish support email)
        email_from = settings.EMAIL_HOST_USER   # ← Your official email

        # Send email
        send_mail(
            subject,
            '',  # Plain text fallback (empty to use only HTML)
            email_from,
            [email],
            html_message=html_message
        )

        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)

class ResetPassword(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        user = UserProfile.objects.filter(email=email, otp=otp).first()
        if user:
            #check if otp is expired or not (5 minutes)
            time_diff = timezone.now() - user.otp_created
            if time_diff.total_seconds() > 300:
                return Response({'error':'OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            user.otp = None
            user.otp_created = None
            user.save(update_fields=['password', 'otp', 'otp_created'])
            return Response({'message':'Password reset successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'Invalid OTP or email'}, status=status.HTTP_400_BAD_REQUEST)

class GetUserRoles(APIView):
    
    def get(self, request):
        roles = UserRole.objects.filter(role_name__in=["user", "company_user"])
        data = [{"id": r.id, "role_name": r.role_name} for r in roles]
        return Response(data)

class UserDetailsAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user = UserProfile.objects.get(email=user.email)
        print(f"Fetched user details for: {user}")  # Debugging line
        return Response({
            "email": user.email,
            "name": user.name,
            "profile_image": user.profile_image,
            "phone": user.mobile_no,
            "is_active": user.is_active,
            "role": user.role_name.role_name if user.role_name else None,
            "company": user.company.company_name if user.company else None,
        })


class EditUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            user = UserProfile.objects.get(email=request.user.email)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EditUserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePassword(APIView):
    serializer_class = ChangePasswordSerializer
    model = UserProfile
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()

        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        print("request.data: ", request.data)

        if serializer.is_valid():
            print("serializer is valid")
            # Check old password
            if not self.object.check_password(serializer.data.get("oldpassword")):
                return Response({"error": "Current password is not correct"}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get

            self.object.set_password(serializer.data.get("password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }
            return Response(response)
        return Response({"error": serializer.errors},status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        request.user.auth_token.delete()
        return Response({"message": "Successfully logged out."},status=status.HTTP_200_OK)


import requests

class GoogleLoginView(APIView):
    def post(self, request):
        id_token_from_frontend = request.data.get("token")
        #print(f"Received ID token: {id_token_from_frontend}")  # Debugging line
        if not id_token_from_frontend:
            return Response({"error": "id_token is required"}, status=400)

        try:
            # Import Google libraries locally to avoid unresolved import at module load time
            import importlib
            id_token = importlib.import_module('google.oauth2.id_token')
            google_requests = importlib.import_module('google.auth.transport.requests')
        except Exception:
            return Response({"error": "Google auth libraries not installed. Install 'google-auth' and 'google-auth-oauthlib'."}, status=500)

        try:
            # Verify token with Google
            google_user = id_token.verify_oauth2_token(
                id_token_from_frontend,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID  # ← Replace with your actual Google Client ID
            )
            #print(f"Google user info: {google_user}")  # Debugging line
            email = google_user.get("email")
            #print(f"Email extracted: {email}")  # Debugging line
            name = google_user.get("name", "")
            #print(f"Name extracted: {name}")  # Debugging line
            picture = google_user.get("picture", "")
            #print(f"Picture URL extracted: {picture}")  # Debugging line

        except Exception as e:
            return Response({"error": "Invalid Google ID token"}, status=400)

        # Create or fetch user
        user, created = UserProfile.objects.get_or_create(
            email=email,
            defaults={
                "name": name if name else None,
                "profile_image": picture if picture else None,
                "mobile_no": None
            }
        )

        # Create token
        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "email": user.email,
            "token": token.key,
            "name": user.name,
            "profile_image": user.profile_image
        })