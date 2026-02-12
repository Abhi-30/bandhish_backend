from django.shortcuts import render

# Create your views here.

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from .models import SubscriptionPlan
from accounts.models import UserProfile
# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import SubscriptionPlan, UserProfile
from .serializer import SubscriptionPlanCreateSerializer
from django.shortcuts import get_object_or_404

class CreateSubscriptionPlanAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_profile = UserProfile.objects.get(email=user.email)
        print("User Role:", user_profile.role_name)  # Debugging line
        
        # 🔐 Allow only Admin
        if not user_profile.role_name or user_profile.role_name.role_name != "Super Admin":
            return Response(
                {"message": "You do not have permission to create subscription plans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubscriptionPlanCreateSerializer(data=request.data)

        if serializer.is_valid():
            plan = serializer.save(
                created_by=user_profile,
                updated_by=user_profile
            )
            print("Created Subscription Plan:", plan)  # Debugging line
            return Response(
                {
                    "message": "Subscription plan created successfully.",
                    "data": SubscriptionPlanCreateSerializer(plan).data
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        plans = SubscriptionPlan.objects.all()
        serializer = SubscriptionPlanCreateSerializer(plans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        id = request.data.get("id")
        user_profile = UserProfile.objects.get(email=user.email)
        
        if not user_profile.role_name or user_profile.role_name.role_name != "Super Admin":
            return Response(
                {"message": "You do not have permission to update subscription plans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            plan = SubscriptionPlan.objects.get(id=id, is_active=True)
            print("Subscription Plan to Update:", plan)  # Debugging line
        except SubscriptionPlan.DoesNotExist:
            return Response({"message": "Subscription plan not found."}, status=status.HTTP_404_NOT_FOUND)

        if plan:
            #fetch the new values and update in database
            price = request.data.get("price_inr")
            credits = request.data.get("credits")
            templates_included = request.data.get("templates_included")
            voices_included = request.data.get("voices_included")
            description = request.data.get("description")
            is_monthly = request.data.get("is_monthly")
            
            if price is not None:
                plan.price_inr = price
            if credits is not None:
                plan.credits = credits
            if templates_included is not None:
                plan.templates_included = templates_included
            if voices_included is not None:
                plan.voices_included = voices_included
            if description is not None:
                plan.description = description 
            if is_monthly is not None: 
                plan.is_monthly = is_monthly 
            plan.updated_by = user_profile
            plan.save(update_fields=["price_inr", "credits", "templates_included", "voices_included", "description", "is_monthly", "updated_by", "updated_at"])
            return Response({"message": "Subscription plan updated successfully.", "data": SubscriptionPlanCreateSerializer(plan).data}, status=status.HTTP_200_OK)
        return Response({"message": "Subscription plan not found."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        
        #fetch the plan id from request data
        id = request.data.get("id")
        user = request.user
        user_profile = UserProfile.objects.get(email=user.email)
        if not user_profile.role_name or user_profile.role_name.role_name != "Super Admin":
            return Response(
                {"message": "You do not have permission to delete subscription plans."},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        try:
            plan = SubscriptionPlan.objects.get(id=id, is_active=True)
            print("Subscription Plan to Delete:", plan)  # Debugging line
        except SubscriptionPlan.DoesNotExist:
            return Response({"message": "Subscription plan not found."}, status=status.HTTP_404_NOT_FOUND)
        
        plan.is_active = False
        plan.updated_by = user_profile
        plan.save(update_fields=["is_active", "updated_by", "updated_at"])
        return Response({"message": "Subscription plan deleted successfully."}, status=status.HTTP_200_OK)

class ToggleSubscriptionPlanStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        plan_id = request.data.get("id")
        is_active = request.data.get("is_active")

        # Validate input
        if plan_id is None or is_active is None:
            return Response(
                {"error": "Both 'id' and 'is_active' fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
            
        if isinstance(is_active, str):
            if is_active.lower() == "true":
                is_active = True
            elif is_active.lower() == "false":
                is_active = False
            else:
                return Response(
                    {"error": "'is_active' must be true or false."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        # Get user profile
        try:
            user_profile = UserProfile.objects.get(email=request.user.email)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission check
        if not user_profile.role_name or user_profile.role_name.role_name != "Super Admin":
            return Response(
                {"error": "You do not have permission to modify subscription plans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get plan
        plan = get_object_or_404(SubscriptionPlan, id=plan_id)
        print("Toggling Subscription Plan Status:", plan)  # Debugging line
        # Update status
        plan.is_active = is_active
        plan.updated_by = user_profile
        plan.save(update_fields=["is_active", "updated_by", "updated_at"])

        action = "activated" if is_active else "deactivated"

        return Response(
            {
                "message": f"Subscription plan {action} successfully.",
                "data": SubscriptionPlanCreateSerializer(plan).data,
            },
            status=status.HTTP_200_OK,
        )