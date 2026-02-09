from django.db import models

from accounts.models import UserProfile
# Create your models here.
class MasterFlow(models.Model):
    flow_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_flows')
    updated_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_flows')
    
    def __str__(self):
        return self.flow_name

class Template(models.Model):
    
    flow = models.ForeignKey(
        MasterFlow,
        on_delete=models.CASCADE,
        related_name="templates"
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    is_premium = models.BooleanField(default=False)
    template_data = models.JSONField()  # or TextField if needed
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="templates"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_templates"
    )

    def __str__(self):
        return f"{self.name} ({'Premium' if self.is_premium else 'Free'})"







class MasterApplication(models.Model):
    application_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    flow = models.ForeignKey(MasterFlow, on_delete=models.CASCADE, related_name='applications')
    
    def __str__(self):
        return self.application_name


class MasterTargetAudience(models.Model):
    target_audience_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    application = models.ForeignKey(MasterApplication, on_delete=models.CASCADE, related_name='target_audiences')
    
    def __str__(self):
        return self.target_audience_name
    

class MasterSector(models.Model):
    sector_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    #target_audience = models.ForeignKey(MasterTargetAudience, on_delete=models.CASCADE, related_name='sectors')
    flow = models.ForeignKey(MasterFlow, on_delete=models.CASCADE, related_name='sectors')
    
    def __str__(self):
        return self.sector_name


class script_flow_fields(models.Model):
    customer_name = models.CharField(max_length=200,null=True,blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_contact = models.CharField(max_length=20, null=True, blank=True)
    designation = models.CharField(max_length=100,null=True,blank=True)
    department = models.CharField(max_length=100,null=True,blank=True)
    company_name = models.CharField(max_length=200, null=True, blank=True)
    company_address = models.TextField(null=True, blank=True)
    company_contact = models.CharField(max_length=20, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    validity = models.CharField(max_length=100,null=True,blank=True)
    offers = models.TextField(null=True, blank=True)
    promo_code = models.CharField(max_length=100,null=True,blank=True)
    additional_info = models.TextField(null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    flow = models.ForeignKey(MasterFlow, on_delete=models.CASCADE, related_name='script_flow_fields', null=True, blank=True)
    image = models.URLField(null=True, blank=True)
    language = models.CharField(max_length=100,null=True,blank=True)
    tone = models.CharField(max_length=100,null=True,blank=True)
    rules = models.TextField(null=True, blank=True)
    script = models.TextField(null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    created_by=models.CharField(max_length=100,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_by=models.CharField(max_length=100,null=True,blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Script for {self.flow.flow_name if self.flow else 'No Flow'}" 
    
    