from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, email):
        """Case-insensitive email lookup"""
        return self.get(email__iexact=email)
    

class UserRole(models.Model):
    role_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    Created_At=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    Created_By=models.CharField(max_length=100,null=True,blank=True)
    Updated_At=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    Updated_By=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.role_name
    
from django.core.validators import validate_email    
class UserProfile(AbstractUser):
    # Override username
    username = None  
    email = models.EmailField(unique=True, primary_key=True, validators=[validate_email])

    # Optional fields
    name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    mobile_no = models.CharField(unique=True, max_length=20, null=True, blank=True)
    profile_image = models.URLField(max_length=200, blank=True, null=True)
    company = models.ForeignKey("Company_Master", on_delete=models.SET_NULL, null=True, blank=True)
    # OTP related
    otp = models.CharField(max_length=400, null=True, blank=True)
    otp_created = models.DateTimeField(null=True, blank=True)

    # Custom fields
    role_name = models.ForeignKey(UserRole, on_delete=models.CASCADE,null=True, blank=True)
    admin_flag = models.BooleanField(default=False)
    #search_engine = models.CharField(max_length=800, null=True, blank=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    updated_by = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # Manager
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["mobile_no"]

    def __str__(self):
        return self.email

    def get_role_name(self):
        return self.role_name.role_name if self.role_name else None


class Company_Master(models.Model):
    company_name = models.CharField(max_length=200, unique=True)
    company_address = models.TextField(null=True, blank=True)
    company_contact = models.CharField(max_length=20, null=True, blank=True)
    company_email = models.EmailField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    created_by=models.CharField(max_length=100,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_by=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.company_name
    

class Customer_Master(models.Model):
    customer_name = models.CharField(max_length=200,null=True,blank=True)
    customer_address = models.TextField(null=True, blank=True)
    customer_contact = models.CharField(max_length=20, null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    designation = models.CharField(max_length=100,null=True,blank=True)
    department = models.CharField(max_length=100,null=True,blank=True)
    company = models.ForeignKey(Company_Master, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True,blank=True,null=True)
    created_by=models.CharField(max_length=100,null=True,blank=True)
    updated_at=models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_by=models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.customer_name


