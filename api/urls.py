from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import USSDPUSHView, PaymentViewSet, mpesa_ussd_callback

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename='payments')

urlpatterns = [
    path("", include(router.urls)),
    path("ussdpush", USSDPUSHView.as_view(), name="ussdpush"),
    path("mpesa/callback", mpesa_ussd_callback, name="mpesa_callback"),
]
