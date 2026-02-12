from django.urls import path

from .views import CreateSubscriptionPlanAPIView, ToggleSubscriptionPlanStatusAPIView 
urlpatterns = [
    #path('api/', include('accounts.urls')),
    path('create_subscription_plan/', CreateSubscriptionPlanAPIView.as_view(), name='create_subscription_plan'),
    path('activate_deactivate_plan/', ToggleSubscriptionPlanStatusAPIView.as_view(), name='activate_deactivate_plan'),
]