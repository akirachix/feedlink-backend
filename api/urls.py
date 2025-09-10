from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, WasteClaimViewSet, OrderItemViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'item', OrderItemViewSet)
router.register(r'wasteclaims', WasteClaimViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
