# serializers.py

from rest_framework import serializers
from .models import SubscriptionPlan

class SubscriptionPlanCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "price_inr",
            "credits",
            "templates_included",
            "voices_included",
            "description",
            "is_monthly",
            "is_active" 
        ]

    def validate_name(self, value):
        if SubscriptionPlan.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Plan with this name already exists.")
        return value
