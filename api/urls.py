from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, ListingCSVUploadView

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listings')

urlpatterns = [

    path('api/listings/upload-csv/', ListingCSVUploadView.as_view(), name='listing-csv-upload'),
    path('api/', include(router.urls)),
]