from django.contrib import admin

# Register your models here.

from accounts.models import UserProfile,UserRole,Company_Master,AdminWallet,AdminWalletTransaction,Customer_Master,CustomAvatarPreUploadVideo


class companyAdminWallet(admin.ModelAdmin):
    list_display = ('admin_user','total_credits','credits_used','credits_remaining','updated_at','updated_by')
    list_display_links = ('admin_user','total_credits','credits_used','credits_remaining','updated_at','updated_by') 
    search_fields = ('admin_user__email',) 
    list_filter = ('admin_user__email',)
admin.site.register(AdminWallet, companyAdminWallet)

class AdminWalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'credits','created_at','created_by')
    list_display_links = ('wallet', 'transaction_type', 'amount', 'credits','created_at','created_by')
    search_fields = ('wallet__admin_user__email', 'transaction_type') 
    list_filter = ('transaction_type', 'created_at') 
admin.site.register(AdminWalletTransaction, AdminWalletTransactionAdmin)

class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('role_name', 'is_active')
    search_fields = ('role_name',)
    list_filter = ('is_active',)
admin.site.register(UserRole, UserRoleAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'mobile_no', 'role_name', 'company', 'is_active', 'created_at', 'created_by', 'updated_at', 'updated_by')
    list_display_links = ('email','name','mobile_no','role_name','company','is_active')
    search_fields = ('email', 'name', 'mobile_no')
    list_filter = ('is_active', 'role_name')
admin.site.register(UserProfile, UserProfileAdmin)

class CompanyMasterAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'is_active', 'created_at', 'created_by', 'updated_at', 'updated_by')
    list_display_links = ('company_name','is_active','created_at','created_by','updated_at','updated_by')
    search_fields = ('company_name',)
    list_filter = ('is_active',)
admin.site.register(Company_Master, CompanyMasterAdmin)

# class CustomAvatarPreUploadVideoAdmin(admin.ModelAdmin):
#     list_display = ('id','avatar_name', 'media_url', 'created_at')
#     search_fields = ('avatar_name',)
#     list_filter = ('created_at',)
# admin.site.register(CustomAvatarPreUploadVideo, CustomAvatarPreUploadVideoAdmin)

# admin.site.register(Customer_Master)

