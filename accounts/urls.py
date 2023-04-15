from django.urls import path, include
from accounts.views import *
from rest_framework import routers

router = routers.DefaultRouter()

router.register(r'request_donation', RequestDonationViewSet , basename='request-donation')



urlpatterns = [
    path('', include(router.urls)),
    path('register', RegistrationAPI.as_view()),
    path('login', UserLoginAPI.as_view()),
    path('password_reset', PasswordResetView.as_view()),
]