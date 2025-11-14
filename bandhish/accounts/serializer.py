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


class EditUserSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(required=False)
    company = serializers.CharField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "name",
            "mobile_no",
            "role_name",
            "company",
        ]

    def update(self, instance, validated_data):

        # Update role if provided
        role_name = validated_data.pop("role_name", None)
        if role_name:
            instance.role_name = UserRole.objects.get(role_name=role_name)

        # Update company if provided
        company = validated_data.pop("company", None)
        print(f"Updating company to: {company}")  # Debugging line
        if company:
            comp_ints = Company_Master.objects.get(company_name=company)
            instance.company = comp_ints
            
        # Update remaining fields dynamically
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

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


