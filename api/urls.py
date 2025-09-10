
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (
    api_root,
    UserViewSet,
    UserSignupAPIView,
    UserLoginAPIView,
    ForgotPasswordView,
    VerifyCodeView,
    ResetPasswordView,
   
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verification/', VerifyCodeView.as_view(), name='verify-code'),
    path('reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('', include(router.urls)),
]