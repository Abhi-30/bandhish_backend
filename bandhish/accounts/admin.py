from django.contrib import admin

# Register your models here.

from accounts.models import UserProfile,UserRole,Company_Master,Customer_Master
admin.site.register(UserRole)
admin.site.register(UserProfile)
admin.site.register(Company_Master)
admin.site.register(Customer_Master)

