from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, WasteClaimViewSet, OrderItemViewSet,ListingViewSet, ListingCSVUploadView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'item', OrderItemViewSet)
router.register(r'wasteclaims', WasteClaimViewSet)
router.register(r'listings', ListingViewSet, basename='listings')

urlpatterns = [

    path('api/listings/upload-csv/', ListingCSVUploadView.as_view(), name='listing-csv-upload'),
    path('api/', include(router.urls)),
]

