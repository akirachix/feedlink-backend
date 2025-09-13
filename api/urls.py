

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, WasteClaimViewSet, OrderItemViewSet,ListingViewSet, ListingCSVUploadView, USSDPUSHView, PaymentViewSet, mpesa_ussd_callback
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .views import (
    UserViewSet,
    UserSignupAPIView,
    UserLoginAPIView,
    ForgotPasswordView,
    VerifyCodeView,
    ResetPasswordView,
   
)

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'item', OrderItemViewSet)
router.register(r'wasteclaims', WasteClaimViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'listings', ListingViewSet, basename='listings')
router.register(r"payments", PaymentViewSet, basename='payments')


urlpatterns = [

    path('signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verification/', VerifyCodeView.as_view(), name='verify-code'),
    path('reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('listings/upload-csv/', ListingCSVUploadView.as_view(), name='listing-csv-upload'),
    path("ussdpush", USSDPUSHView.as_view(), name="ussdpush"),
    path("mpesa/callback", mpesa_ussd_callback, name="mpesa_callback"),
    path('', include(router.urls)),

    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]


