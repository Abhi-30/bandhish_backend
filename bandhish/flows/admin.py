from django.contrib import admin

# Register your models here.

from .models import SubscriptionPlan, TemplateGroup, MasterFlow, TemplateVariant

class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "price_inr", "credits","is_monthly","templates_included","voices_included","is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)
admin.site.register(SubscriptionPlan, SubscriptionPlanAdmin)
