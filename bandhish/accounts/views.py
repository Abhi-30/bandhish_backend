from django.utils import timezone
from django.conf import settings
from django.shortcuts import render
from django.core.mail import send_mail
import boto3

# Create your views here.

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate

from .serializer import SimpleRegisterSerializer,EditUserSerializer,ChangePasswordSerializer,AdminAddClientSerializer
from rest_framework import status
from .models import Company_Master, UserProfile, UserRole
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
        print(f"ResetPassword - user found: {user}")  # Debugging line
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

from .utils import generate_presigned_url

class UserDetailsAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = UserProfile.objects.get(email=request.user.email)
        print(f"Fetched user details for: {user.email}")

        profile_image_url = None
        if user.profile_image:
            profile_image_url = generate_presigned_url(user.profile_image)

        return Response({
            "email": user.email,
            "name": user.name,
            "mobile_no": user.mobile_no,
            "is_active": user.is_active,
            "role": user.role_name.role_name if user.role_name else None,
            "company": user.company.company_name if user.company else None,
            "company_address": user.company.company_address if user.company else None,
            "profile_image_url": profile_image_url
        }, status=status.HTTP_200_OK)
        
    # def get(self, request):
    #     user = request.user
    #     user = UserProfile.objects.get(email=user.email)
    #     print(f"Fetched user details for: {user}")  # Debugging line
    #     return Response({
    #         "email": user.email,
    #         "name": user.name,
    #         "profile_image": user.profile_image,
    #         "mobile_no": user.mobile_no,
    #         "is_active": user.is_active,
    #         "role": user.role_name.role_name if user.role_name else None,
    #         "company": user.company.company_name if user.company else None,
    #         "company_address": user.company.company_address if user.company else None,  
    #     })


class EditUserAPI(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            user = UserProfile.objects.get(email=request.user.email)
            print(f"User found for editing: {user}")  # Debugging line
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EditUserSerializer(
            user,
            data=request.data,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            user = serializer.save()

            return Response(
                {
                    "message": "User updated successfully",
                    "data": {
                        "name": user.name,
                        "mobile_no": user.mobile_no,
                        "role": user.role_name.role_name if user.role_name else None,
                        "company": user.company.company_name if user.company else None,
                        "profile_image_url": serializer.get_profile_image_url(user)
                    }
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # def put(self, request):
    #     try:
    #         user = UserProfile.objects.get(email=request.user.email)
    #     except UserProfile.DoesNotExist:
    #         return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    #     serializer = EditUserSerializer(user, data=request.data, partial=True)

    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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

from .models import CustomAvatarPreUploadVideo
from .serializer import CustomAvatarVideoSerializer 
from uuid import uuid4


from botocore.client import Config

class UploadVideoAPIToS3(APIView):
    
    # def post(self, request):
    #     avatar_name = request.data.get("avatar_name")
    #     media_file = request.FILES.get("media_file")
    #     print(f"Received avatar_name: {avatar_name}")  # Debugging line
    #     print(f"Received media_file: {media_file}")  # Debugging line
    #     if not avatar_name:
    #         return Response({"error": "avatar_name is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     if not media_file:
    #         return Response({"error": "media_file is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     # Clean and uniquely name file
    #     filename = media_file.name.replace(" ", "_")
    #     print(f"Original filename: {filename}")  # Debugging line
    #     unique_name = f"{uuid4().hex}_{filename}"
    #     print(f"Unique filename generated: {unique_name}")  # Debugging line
        
    #     s3_key = f"Users/Videos/{unique_name}"

    #     s3 = boto3.client(
    #         "s3",
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME
    #     )

    #     # Upload to S3 with proper error handling
    #     try:
    #         s3.upload_fileobj(
    #             media_file,
    #             settings.AWS_STORAGE_BUCKET_NAME,
    #             s3_key,
    #         )
    #     except Exception as e:
    #         return Response({"error": f"S3 upload failed: {str(e)}"}, status=500)

    #     media_url = (
    #         f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
    #         f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
    #     )
    #     print(f"Media uploaded to S3. URL: {media_url}")  # Debugging line
    #     # Save avatar (without user — as your model shows)
    #     avatar = CustomAvatarPreUploadVideo.objects.create(
    #         avatar_name=avatar_name,
    #         media_url=media_url
    #     )

    #     serializer = CustomAvatarVideoSerializer(avatar)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    #new with training and consent file upload
    # def post(self, request):
    #     avatar_name = request.data.get("avatar_name")
    #     training_video = request.FILES.get("media_file")
    #     consent_video = request.FILES.get("consent_file")

    #     # Debugging logs
    #     print("avatar_name:", avatar_name)
    #     print("training_video:", training_video)
    #     print("consent_video:", consent_video)

    #     # Validations
    #     if not avatar_name:
    #         return Response({"error": "avatar_name is required"}, status=400)

    #     if not training_video:
    #         return Response({"error": "training_video is required"}, status=400)

    #     if not consent_video:
    #         return Response({"error": "consent_video is required"}, status=400)

    #     # Initialize S3 client
    #     s3 = boto3.client(
    #         "s3",
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME
    #     )

    #     def upload_to_s3(file_obj, folder="Users/AvatarVideos/"):
    #         """Reusable upload helper."""
    #         filename = file_obj.name.replace(" ", "_")
    #         unique = f"{uuid4().hex}_{filename}"
    #         s3_key = f"{folder}{unique}"

    #         try:
    #             s3.upload_fileobj(
    #                 file_obj,
    #                 settings.AWS_STORAGE_BUCKET_NAME,
    #                 s3_key
    #             )
    #         except Exception as e:
    #             raise Exception(f"S3 upload failed: {str(e)}")

    #         return (
    #             f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
    #             f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
    #         )

    #     # Upload both files
    #     try:
    #         training_video_url = upload_to_s3(training_video)
    #         consent_video_url = upload_to_s3(consent_video)
    #     except Exception as upload_err:
    #         return Response({"error": str(upload_err)}, status=500)

    #     print("Training Video URL:", training_video_url)
    #     print("Consent Video URL:", consent_video_url)

    #     # Save avatar record
    #     avatar = CustomAvatarPreUploadVideo.objects.create(
    #         avatar_name=avatar_name,
    #         media_url=training_video_url,
    #         consent_url=consent_video_url,
    #         unique_id=str(uuid4())
    #     )

    #     serializer = CustomAvatarVideoSerializer(avatar)
    #     return Response(serializer.data, status=201)
    
    
    def post(self, request):
        avatar_name = request.data.get("avatar_name")
        training_video = request.FILES.get("media_file")
        consent_video = request.FILES.get("consent_file")

        print("avatar_name:", avatar_name)
        print("training_video:", training_video)
        print("consent_video:", consent_video)

        # Validations
        if not avatar_name:
            return Response({"error": "avatar_name is required"}, status=400)

        # if not training_video:
        #     return Response({"error": "training_video is required"}, status=400)

        if not consent_video:
            return Response({"error": "consent_video is required"}, status=400)

        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )

        def upload_training_video(file_obj, folder="Users/AvatarVideos/"):
            """Upload training video without modifying Content-Type"""
            filename = file_obj.name.replace(" ", "_")
            unique = f"{uuid4().hex}_{filename}"
            s3_key = f"{folder}{unique}"

            try:
                s3.upload_fileobj(
                    file_obj,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    s3_key
                )
            except Exception as e:
                raise Exception(f"S3 upload failed: {str(e)}")

            return (
                f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
                f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            )

        # def upload_consent_video(file_obj, folder="Users/AvatarVideos/"):
        #     """Upload consent video WITH correct Content-Type to fix D-ID error"""
        #     filename = file_obj.name.replace(" ", "_")
        #     unique = f"{uuid4().hex}_{filename}"
        #     s3_key = f"{folder}{unique}"

        #     try:
        #         s3.upload_fileobj(
        #             file_obj,
        #             settings.AWS_STORAGE_BUCKET_NAME,
        #             s3_key,
        #             ExtraArgs={
        #                 "ContentType": "video/mp4"   # IMPORTANT FIX
        #             }
        #         )
        #     except Exception as e:
        #         raise Exception(f"Consent S3 upload failed: {str(e)}")

        #     return (
        #         f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
        #         f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
        #     )

        # def upload_consent_video(file_obj, avatar_name, folder="Users/AvatarVideos/"):
        #     """Upload consent video with correct Content-Type AND matching filename to speaker name."""
            
        #     # Force the filename to match avatar_name
        #     ext = file_obj.name.split(".")[-1]  # Keep original extension
        #     new_filename = f"{avatar_name.strip().replace(' ', '_')}_consent.{ext}"
        #     s3_key = f"{folder}{uuid4().hex}_{new_filename}"  # Add UUID for uniqueness

        #     try:
        #         s3.upload_fileobj(
        #             file_obj,
        #             settings.AWS_STORAGE_BUCKET_NAME,
        #             s3_key,
        #             ExtraArgs={
        #                 "ContentType": "video/mp4"
        #             }
        #         )
        #     except Exception as e:
        #         raise Exception(f"Consent S3 upload failed: {str(e)}")

        #     return (
        #         f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
        #         f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
        #     )
        
        
        def upload_consent_video(file_obj, avatar_name, folder="Users/AvatarVideos/"):
            ext = file_obj.name.split(".")[-1]
            new_filename = f"{avatar_name.strip().replace(' ', '_')}_consent.{ext}"
            print("New consent filename:", new_filename)  # Debugging line
            s3_key = f"{folder}{uuid4().hex}_{new_filename}"
            print("S3 Key for consent video:", s3_key)  # Debugging line
            try:
                s3.upload_fileobj(
                    file_obj,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    s3_key,
                    ExtraArgs={
                        "ContentType": "video/mp4",
                        "ACL": "public-read"
                    }
                )
            except Exception as e:
                raise Exception(f"Consent S3 upload failed: {str(e)}")

            return (
                f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
                f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
            )
        
        # Upload videos
        try:
            #training_video_url = upload_training_video(training_video)
            ##consent_video_url = upload_consent_video(consent_video)
            consent_video_url = upload_consent_video(consent_video, avatar_name)
        except Exception as upload_err:
            return Response({"error": str(upload_err)}, status=500)

        #print("Training Video URL:", training_video_url)
        print("Consent Video URL:", consent_video_url)

        # Save avatar record
        avatar = CustomAvatarPreUploadVideo.objects.create(
            avatar_name=avatar_name,
            #media_url=training_video_url,
            consent_url=consent_video_url,
            unique_id=str(uuid4())
        )

        serializer = CustomAvatarVideoSerializer(avatar)
        return Response(serializer.data, status=201)
    
    # def post(self, request):
    #     media_file = request.FILES.get("media_file")
    #     consent_file = request.FILES.get("consent_file")

    #     if not media_file:
    #         return Response({"error": "media_file is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     if not consent_file:
    #         return Response({"error": "consent_file is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     s3_client = boto3.client(
    #         "s3",
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME
    #     )

    #     # ----- UPLOAD TRAINING MEDIA FILE -----
    #     media_filename = media_file.name.replace(" ", "_")
    #     media_unique = f"{uuid4().hex}_{media_filename}"
    #     media_key = f"Users/AvatarMedia/{media_unique}"

    #     print("Uploading media_file to S3...")

    #     try:
    #         s3_client.upload_fileobj(media_file, settings.AWS_STORAGE_BUCKET_NAME, media_key)
    #     except Exception as e:
    #         return Response({"error": f"Media file upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     media_presigned_url = s3_client.generate_presigned_url(
    #         "get_object",
    #         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": media_key},
    #         ExpiresIn=36000  # 10 hours
    #     )
    #     print("Media file uploaded successfully.")
        
    #     # ----- UPLOAD CONSENT FILE -----
    #     consent_filename = consent_file.name.replace(" ", "_")
    #     consent_unique = f"{uuid4().hex}_{consent_filename}"
    #     consent_key = f"Users/AvatarConsent/{consent_unique}"

    #     print("Uploading consent_file to S3...")

    #     try:
    #         s3_client.upload_fileobj(consent_file, settings.AWS_STORAGE_BUCKET_NAME, consent_key)
    #     except Exception as e:
    #         return Response({"error": f"Consent file upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    #     consent_presigned_url = s3_client.generate_presigned_url(
    #         "get_object",
    #         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": consent_key},
    #         ExpiresIn=36000  # 10 hours
    #     )

    #     print("Both files uploaded successfully!")
        
    #     # Save record in database
    #     avatar_record = CustomAvatarPreUploadVideo.objects.create(
    #         avatar_name=request.data.get("avatar_name", "Unnamed Avatar"),
    #         unique_id=str(uuid4()),
    #         media_url=media_presigned_url,
    #         consent_url=consent_presigned_url,
    #     )
    #     print(f"Avatar record created with ID: {avatar_record.id}")  # Debugging line
        
    #     # Return everything needed for HeyGen
    #     return Response({
    #         "media": {
    #             "s3_key": media_key,
    #             "presigned_url": media_presigned_url
    #         },
    #         "consent": {
    #             "s3_key": consent_key,
    #             "presigned_url": consent_presigned_url
    #         }
    #     }, status=status.HTTP_201_CREATED)

    # def post(self, request):
    #     media_file = request.FILES.get("media_file")
    #     consent_file = request.FILES.get("consent_file")

    #     if not media_file:
    #         return Response({"error": "media_file is required"}, status=400)

    #     if not consent_file:
    #         return Response({"error": "consent_file is required"}, status=400)

    #     # FIX: Force S3 to use region endpoint (ap-south-1)
    #     s3_client = boto3.client(
    #         "s3",
    #         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    #         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    #         region_name=settings.AWS_S3_REGION_NAME,
    #         config=Config(
    #             signature_version="s3v4",
    #             s3={"addressing_style": "virtual"}  # IMPORTANT
    #         )
    #     )

    #     # -------- Upload media file ----------
    #     media_filename = media_file.name.replace(" ", "_")
    #     media_key = f"Users/AvatarMedia/{uuid4().hex}_{media_filename}"

    #     s3_client.upload_fileobj(media_file, settings.AWS_STORAGE_BUCKET_NAME, media_key)

    #     media_presigned_url = s3_client.generate_presigned_url(
    #         "get_object",
    #         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": media_key},
    #         ExpiresIn=36000
    #     )
    #     print("Media file uploaded successfully.")
    #     print("Generating presigned URL for media file...", media_presigned_url)  # Debugging line
    #     # -------- Upload consent file ----------
    #     consent_filename = consent_file.name.replace(" ", "_")
    #     consent_key = f"Users/AvatarConsent/{uuid4().hex}_{consent_filename}"

    #     s3_client.upload_fileobj(consent_file, settings.AWS_STORAGE_BUCKET_NAME, consent_key)

    #     consent_presigned_url = s3_client.generate_presigned_url(
    #         "get_object",
    #         Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": consent_key},
    #         ExpiresIn=36000
    #     )
    #     print("Consent file uploaded successfully.")
    #     print("Generating presigned URL for consent file...", consent_presigned_url)  # Debugging line

    #     # SAVE record
    #     avatar_record = CustomAvatarPreUploadVideo.objects.create(
    #         avatar_name=request.data.get("avatar_name", "Unnamed Avatar"),
    #         unique_id=str(uuid4()),
    #         media_url=media_presigned_url,
    #         consent_url=consent_presigned_url,
    #     )
    #     print(f"Avatar record created with ID: {avatar_record.id}")  # Debugging line
        
    #     # 🔍 DEBUG PRINTS
    #     print("MEDIA URL:", media_presigned_url)
    #     print("CONSENT URL:", consent_presigned_url)

    #     return Response({
    #         "media": {
    #             "s3_key": media_key,
    #             "presigned_url": media_presigned_url
    #         },
    #         "consent": {
    #             "s3_key": consent_key,
    #             "presigned_url": consent_presigned_url
    #         }
    #     }, status=201)


class HeyGenAvatarCallbackAPI(APIView):
    
    def get(self, request):
        return Response({"message": "HeyGen Avatar Callback API is running."}, status=status.HTTP_200_OK)
    
    def post(self, request):
        callback_id = request.data.get("callback_id")
        print(f"Received callback_id: {callback_id}")  # Debugging line
        event_type = request.data.get("event_type")
        print(f"Received event_type: {event_type}")  # Debugging line
        avatar_id = request.data.get("avatar_id")
        print(f"Received avatar_id: {avatar_id}")  # Debugging line
        status_value = request.data.get("status")
        print(f"Received status: {status_value}")  # Debugging line

        print(f"Received callback from HeyGen: {request.data}")

        if not callback_id:
            return Response({"error": "callback_id missing"}, status=status.HTTP_400_BAD_REQUEST)

        # Find the avatar record using callback_id
        try:
            avatar = CustomAvatarPreUploadVideo.objects.get(callback_id=callback_id)
            print(f"Found avatar record: {avatar}")  # Debugging line
        except CustomAvatarPreUploadVideo.DoesNotExist:
            return Response({"error": "Callback ID not found"}, status=status.HTTP_404_NOT_FOUND)

        # Update fields
        avatar.heygen_status = status_value
        if avatar_id:
            avatar.avatar_id = avatar_id
        avatar.save()

        return Response({"message": "Callback processed"}, status=status.HTTP_200_OK)



# class AdminAddClientAPI(APIView):
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def post(self, request):
#         # Check if user is admin
#         user = request.user
#         print(f"Authenticated user: {user.email}, admin_flag: {user.admin_flag}")  # Debugging line
#         user_profile = UserProfile.objects.get(email=user.email, is_active=True)    
#         if not user_profile.admin_flag:
#             return Response(
#                 {"error": "Only admins can add clients"},
#                 status=status.HTTP_403_FORBIDDEN
#             )
        
#         serializer = AdminAddClientSerializer(data=request.data)
#         if serializer.is_valid():
#             # Generate random password
#             import string
#             import random
#             password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            
#             # Create user
#             user_profile = serializer.save()
#             user_profile.set_password(password)
#             user_profile.created_by = request.user.email
#             user_profile.save()
            
#             # Send email with credentials
#             subject = "Bandhish Studio - Account Created"
#             html_message = f"""
#             <html>
#             <body>
#                 <h2 style="color:#2b2b2b;">Welcome to Bandhish Studio</h2>
#                 <p>Dear {user.name or 'User'},</p>
#                 <p>Your account has been created by the administrator.</p>
#                 <p><strong>Login Credentials:</strong></p>
#                 <ul>
#                     <li><strong>Email:</strong> {user.email}</li>
#                     <li><strong>Password:</strong> {password}</li>
#                     <li><strong>Role:</strong> User</li>
#                 </ul>
#                 <p>Please log in and change your password after your first login.</p>
#                 <p>Login URL: <a href="http://localhost:5173/login">Click here to login</a></p>
#                 <br>
#                 <p>Regards,<br><strong>Bandhish Studio Support Team</strong></p>
#             </body>
#             </html>
#             """
            
#             email_from = settings.EMAIL_HOST_USER
            
#             try:
#                 send_mail(
#                     subject,
#                     '',
#                     email_from,
#                     [user.email],
#                     html_message=html_message
#                 )
                
#                 return Response(
#                     {
#                         "message": "Client added successfully and email sent",
#                         "user": {
#                             "email": user.email,
#                             "name": user.name,
#                             "mobile_no": user.mobile_no,
#                             "company": user.company.company_name if user.company else None,
#                             "role": user.role_name.role_name
#                         }
#                     },
#                     status=status.HTTP_201_CREATED
#                 )
#             except Exception as e:
#                 # User created but email failed
#                 return Response(
#                     {
#                         "message": "Client added but email sending failed",
#                         "error": str(e),
#                         "user": {
#                             "email": user.email,
#                             "name": user.name,
#                             "role": user.role_name.role_name
#                         },
#                         "temp_password": password
#                     },
#                     status=status.HTTP_201_CREATED
#                 )
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CompanyUserPagination(PageNumberPagination):
    page_size = 5                # default items per page
    page_size_query_param = "page_size"  # ?page_size=10
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })

class AdminAddClientAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        admin_user = request.user
        print(f"Authenticated user: {admin_user.email}, admin_flag: {admin_user.admin_flag}")  # Debugging line 
        if not admin_user.admin_flag:
            return Response(
                {"error": "Only admins can add clients"},
                status=status.HTTP_403_FORBIDDEN
            )

        #serializer = AdminAddClientSerializer(data=request.data)
        
        serializer = AdminAddClientSerializer(
            data=request.data,
            context={"admin_user": admin_user}   # 👈 pass here
        )

        if serializer.is_valid():
            import string, random
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            # Create client user
            client_user = serializer.save()
            client_user.set_password(password)
            client_user.created_by = admin_user.email
            client_user.save()

            subject = "Bandhish Studio - Account Created"
            html_message = f"""
            <html>
            <body>
                <h2>Welcome to Bandhish Studio</h2>
                <p>Dear {client_user.name or 'User'},</p>
                <p>Your account has been created.</p>
                <ul>
                    <li><strong>Email:</strong> {client_user.email}</li>
                    <li><strong>Password:</strong> {password}</li>
                    <li><strong>Company:</strong> {client_user.company.company_name}</li>
                    <li><strong>Role:</strong> {client_user.role_name.role_name}</li>
                </ul>
                <p>Please change your password after first login.</p>
                <p>
                  Login URL:
                  <a href="http://localhost:5173/login">Click here</a>
                </p>
                <br>
                <p>Regards,<br><strong>Bandhish Studio Team</strong></p>
            </body>
            </html>
            """

            try:
                send_mail(
                    subject,
                    '',
                    settings.EMAIL_HOST_USER,
                    [client_user.email],
                    html_message=html_message
                )

                return Response(
                    {
                        "message": "Client and company created successfully",
                        "user": {
                            "email": client_user.email,
                            "name": client_user.name,
                            "company": client_user.company.company_name,
                            "role": client_user.role_name.role_name
                        }
                    },
                    status=status.HTTP_201_CREATED
                )

            except Exception as e:
                return Response(
                    {
                        "message": "Client created, email failed",
                        "temp_password": password,
                        "error": str(e)
                    },
                    status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        admin_user = request.user
        print(
            f"Authenticated user: {admin_user.email}, admin_flag: {admin_user.admin_flag}"
        )

        if not admin_user.admin_flag:
            return Response(
                {"error": "Only admins can view clients"},
                status=status.HTTP_403_FORBIDDEN
            )

        companies_qs = Company_Master.objects.filter(
            created_by=admin_user.email
        ).prefetch_related("userprofile_set")

        paginator = CompanyUserPagination()
        paginated_companies = paginator.paginate_queryset(companies_qs, request)

        data = []
        for company in paginated_companies:
            users = company.userprofile_set.all()
            user_data = []

            for user in users:
                user_data.append({
                    "email": user.email,
                    "name": user.name,
                    "mobile_no": user.mobile_no,
                    "profile_image": user.profile_image,
                    "admin_flag": user.admin_flag,
                    "created_by": user.created_by,
                    "created_at": user.created_at,
                    "role": user.role_name.role_name if user.role_name else None
                })

            data.append({
                "company_id": company.id,
                "company_name": company.company_name,
                "company_address": company.company_address,
                "users": user_data
            })

        return paginator.get_paginated_response(data)
    
class CreateHeyGenAvatarAPI(APIView):
    def post(self, request):
        avatar_name = request.data.get("avatar_name")
        training_url = request.data.get("training_footage_url")
        print(f"Received training_url: {training_url}")  # Debugging line
        consent_url = request.data.get("video_consent_url")
        print(f"Received consent_url: {consent_url}")  # Debugging line
        callback_id = request.data.get("callback_id")
        print(f"Received callback_id: {callback_id}")  # Debugging line
        callback_url = request.data.get("callback_url")
        print(f"Received callback_url: {callback_url}")  # Debugging line
        
        # ----------- VALIDATIONS -----------
        if not avatar_name:
            return Response({"error": "avatar_name is required"}, status=400)

        if not training_url:
            return Response({"error": "training_footage_url is required"}, status=400)

        if not consent_url:
            return Response({"error": "video_consent_url is required"}, status=400)

        if not callback_id:
            callback_id = uuid4().hex  # auto-generate if not provided

        # ----------- SAVE RECORD IN DB -----------
        # avatar_record, created = CustomAvatarPreUploadVideo.objects.update_or_create(
        #     unique_id=callback_id,
        #     defaults={
        #         "avatar_name": avatar_name,
        #         "media_url": training_url,
        #         "consent_url": consent_url,
        #         "heygen_status": "processing"
        #     }
        # )

        #print(f"Avatar record created with ID: {avatar_record.id}")  # Debugging line
        # ----------- PREPARE REQUEST PAYLOAD -----------
        payload = {
            "avatar_name": avatar_name,
            "training_footage_url": training_url,
            "video_consent_url": consent_url,
            "callback_id": callback_id,
            "callback_url": callback_url,  # store in settings
        }
        print(f"Payload for HeyGen API: {payload}")  # Debugging line
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Api-Key": settings.HEYGEN_API_KEY
        }
        print(f"Headers for HeyGen API: {headers}")  # Debugging line
        # ----------- CALL HEYGEN API -----------
        heygen_response = requests.post(
            "https://api.heygen.com/v2/video_avatar",
            json=payload,
            headers=headers
        )

        print("HeyGen Response:", heygen_response.status_code, heygen_response.text)

        # ----------- HANDLE HEYGEN RESPONSE -----------
        if heygen_response.status_code != 200:
            #avatar_record.heygen_status = "failed"
            #avatar_record.save()
            print("HeyGen API call failed.")  # Debugging line
            return Response({
                "error": "HeyGen API failed",
                "details": heygen_response.text
            }, status=500)

        data = heygen_response.json()
        print(f"HeyGen API response data: {data}")  # Debugging line
        
        # Save HeyGen avatar ID if available
        avatar_id = data.get("data", {}).get("avatar_id")
        print(f"Extracted avatar_id: {avatar_id}")  # Debugging line
        # if avatar_id:
        #     avatar_record.avatar_id = avatar_id
        #     avatar_record.save()

        return Response({
            "message": "HeyGen avatar creation request submitted",
            "callback_id": callback_id,
            #"avatar_record_id": avatar_record.id,
            "heygen_response": data
        }, status=200)