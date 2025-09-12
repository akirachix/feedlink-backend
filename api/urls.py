

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet 
from .views import OrderViewSet, WasteClaimViewSet, OrderItemViewSet,ListingViewSet, ListingCSVUploadView


from .views import (
    UserViewSet,
    UserSignupAPIView,
    UserLoginAPIView,
    ForgotPasswordView,
    VerifyCodeView,
    ResetPasswordView,
   
)

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'orders', OrderViewSet)
router.register(r'item', OrderItemViewSet)
router.register(r'wasteclaims', WasteClaimViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'listings', ListingViewSet, basename='listings')


urlpatterns = [

    path('signup/', UserSignupAPIView.as_view(), name='user-signup'),
    path('login/', UserLoginAPIView.as_view(), name='user-login'),
    path('forgotpassword/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('verification/', VerifyCodeView.as_view(), name='verify-code'),
    path('reset/', ResetPasswordView.as_view(), name='reset-password'),
    path('listings/upload-csv/', ListingCSVUploadView.as_view(), name='listing-csv-upload'),
    path('', include(router.urls)),

]


