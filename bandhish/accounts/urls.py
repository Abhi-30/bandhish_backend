
from django.urls import path 

from .views import AdminAddClientAPI, ChangePassword, CreateHeyGenAvatarAPI, EditUserAPI, ForgetPassword, GoogleLoginView, HeyGenAvatarCallbackAPI, LoginAPI, LogoutView, ResetPassword,SimpleRegisterAPI,GetUserRoles, UploadVideoAPIToS3, UserDetailsAPI

urlpatterns = [
    #path('api/', include('accounts.urls')),
    path('login/',LoginAPI.as_view(), name='login'),
    path('register/',SimpleRegisterAPI.as_view(), name='register'),
    path('forget_password/',ForgetPassword.as_view(), name='forget_password'),
    path('reset_password/',ResetPassword.as_view(), name='reset_password'),
    path('show_user_roles/',GetUserRoles.as_view(), name='show_user_roles'),
    path('user_details/',UserDetailsAPI.as_view(), name='user_details'),
    path('user_edit/',EditUserAPI.as_view(), name='user_edit'),
    path('change_password/',ChangePassword.as_view(), name='change_password'),
    path('logout/',LogoutView.as_view(), name='logout'),
    path('google_login/',GoogleLoginView.as_view(), name='google_login'),
    path('admin/add_client/',AdminAddClientAPI.as_view(), name='admin_add_client'),
    
    path('upload_video_to_s3/',UploadVideoAPIToS3.as_view(), name='upload_video_to_s3'),
    path('HeyGenAvatarCallbackAPI/',HeyGenAvatarCallbackAPI.as_view(), name='HeyGenAvatarCallbackAPI'),
    path('heygen_avatar_create/',CreateHeyGenAvatarAPI.as_view(), name='avatar_create'),
]