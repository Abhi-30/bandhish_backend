from rest_framework import serializers
from .models import Company_Master, UserProfile, UserRole

class SimpleRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ["email", "password"]

    def create(self, validated_data):
        print(f"Creating user with data: {validated_data}")  # Debugging line
        default_role = UserRole.objects.get(role_name="user")

        user = UserProfile.objects.create(
            email=validated_data["email"],
            role_name=default_role
        )
        user.set_password(validated_data["password"])
        user.save()

        return user


# class EditUserSerializer(serializers.ModelSerializer):
#     role_name = serializers.CharField(required=False)
#     company = serializers.CharField(required=False)

#     class Meta:
#         model = UserProfile
#         fields = [
#             "name",
#             "mobile_no",
#             "role_name",
#             "company",
#         ]

#     def update(self, instance, validated_data):

#         # Update role if provided
#         role_name = validated_data.pop("role_name", None)
#         if role_name:
#             instance.role_name = UserRole.objects.get(role_name=role_name)

#         # Update company if provided
#         company = validated_data.pop("company", None)
#         print(f"Updating company to: {company}")  # Debugging line
#         if company:
#             comp_ints = Company_Master.objects.get(company_name=company)
#             instance.company = comp_ints
            
#         # Update remaining fields dynamically
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)

#         instance.save()
#         return instance

from .utils import upload_profile_image_to_s3, generate_presigned_url
class EditUserSerializer(serializers.ModelSerializer):
    #role_name = serializers.CharField(required=False)
    company_name = serializers.CharField(required=False)
    company_address = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "name",
            "mobile_no",
            "company_name",
            "company_address",
            "profile_image",
        ]

    def update(self, instance, validated_data):
        # ---- Update role ----
        #role_name = validated_data.pop("role_name", None)
        #if role_name:
        #    instance.role_name = UserRole.objects.get(role_name=role_name)

        # ---- Update company details ----
        company_name = validated_data.pop("company_name", None)
        company_address = validated_data.pop("company_address", None)

        if company_name or company_address:
            if not instance.company:
                raise serializers.ValidationError(
                    {"company": "User is not associated with any company"}
                )

            company = instance.company

            if company_name:
                company.company_name = company_name

            if company_address:
                company.company_address = company_address

            company.save()

        # ---- Handle profile image upload ----
        profile_image = validated_data.pop("profile_image", None)
        if profile_image:
            s3_key = upload_profile_image_to_s3(
                file_obj=profile_image,
                user_id=instance.id
            )
            instance.profile_image = s3_key

        # ---- Update remaining user fields ----
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def get_profile_image_url(self, user):
        if not user.profile_image:
            return None
        return generate_presigned_url(user.profile_image)


from django.contrib.auth.hashers import check_password
class ChangePasswordSerializer(serializers.Serializer):
    model = UserProfile
    """
    Serializer for password change endpoint.
    """
    #old_password = serializers.CharField(required=True)
    oldpassword = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not check_password(value, user.password):
            raise serializers.ValidationError("Incorrect old password.")
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance

from rest_framework import serializers
from .models import CustomAvatarPreUploadVideo

class CustomAvatarVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAvatarPreUploadVideo
        fields = ["id", "avatar_name", "media_url","consent_url","created_at"]


class AdminAddClientSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(required=True)
    company_address = serializers.CharField(required=True)

    class Meta:
        model = UserProfile
        fields = ["email", "name", "mobile_no", "company_name", "company_address"]

    def validate_email(self, value):
        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value

    def create(self, validated_data):
        # Get or create 'User' role
        user_role, _ = UserRole.objects.get_or_create(role_name="User")
        admin_user = self.context.get("admin_user")  # 👈 access here
        #user = UserProfile.objects.get(email=admin_user.email)
        # Extract company data
        company_name = validated_data.pop("company_name")
        company_address = validated_data.pop("company_address")

        # Create or get company
        company_instance, created = Company_Master.objects.get_or_create(
            company_name=company_name,
            created_by=admin_user,
            defaults={"company_address": company_address}
        )

        # Optional: update address if company already exists but address is empty
        if not created and not company_instance.company_address:
            company_instance.company_address = company_address
            company_instance.save()

        # Create user
        user = UserProfile.objects.create(
            email=validated_data["email"],
            name=validated_data.get("name"),
            mobile_no=validated_data.get("mobile_no"),
            company=company_instance,
            role_name=user_role,
            is_active=True
        )

        return user

