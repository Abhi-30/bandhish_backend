from django.db import models

from accounts.models import UserProfile
# Create your models here.


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, unique=True)
    price_inr = models.DecimalField(max_digits=10, decimal_places=2)
    credits = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_plans')
    updated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_plans') 
    is_monthly = models.BooleanField(default=True)  # True for monthly, False for yearly
    description = models.TextField(blank=True, null=True)
    templates_included = models.IntegerField(default=0)  # Number of templates included in the plan 
    voices_included = models.IntegerField(default=0)  # Number of voices included in the plan
        
    def __str__(self):
        return f"{self.name} ({self.credits} credits)"


class MasterFlow(models.Model):
    flow_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.CharField(max_length=2000, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_flows')
    updated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_flows')
    
    def __str__(self):
        return self.flow_name

class TemplateGroup(models.Model):
    flow = models.ForeignKey(
        MasterFlow,
        on_delete=models.CASCADE,
        related_name="template_groups"
    )
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    avatar_group_id = models.CharField(max_length=255, null=True, blank=True)
    is_trained = models.BooleanField(default=False)
    training_status = models.CharField(
        max_length=50,
        default="NOT_STARTED"
    )
    
    def __str__(self):
        return self.name
    

class TemplateVariant(models.Model):
    flow = models.ForeignKey(
        MasterFlow,
        on_delete=models.CASCADE,
        related_name="template_variants_flow"
    )
    template_group = models.ForeignKey(
        TemplateGroup,
        on_delete=models.CASCADE,
        related_name="template_variants"
    )
    name = models.CharField(max_length=255)
    # HeyGen identifiers
    image_key = models.CharField(max_length=255, null=True, blank=True)
    avatar_group_id = models.CharField(max_length=255, null=True, blank=True)

    is_trained = models.BooleanField(default=False)
    training_status = models.CharField(
        max_length=50,
        default="NOT_STARTED"
    )
    
    is_premium = models.BooleanField(default=False)
    preview_url = models.URLField(max_length=10000, null=True, blank=True)
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_variant = models.BooleanField(default=False)
    
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("training", "Training"),
            ("not_started", "Not Started"),
            ("in_progress", "In Progress")            
        ],
        default="pending"
    )
    
    motion_type = models.CharField(
        max_length=50,
        choices=[
            ("kling", "Kling"),
            ("veo2", "Veo2"),
            ("expressive", "Expressive"),
            ("none", "None")
        ],
        default="none"
    )
    
    def __str__(self):
        return self.name

# class TemplateVariant(models.Model):
#     template = models.ForeignKey(
#         Template,
#         on_delete=models.CASCADE,
#         related_name="variants"
#     )
#     heygen_avatar_id = models.CharField(max_length=255)
#     preview_url = models.URLField(max_length=1000, null=True, blank=True)

    
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(
#         UserProfile,
#         on_delete=models.CASCADE
#     )
#     is_active = models.BooleanField(default=True)
