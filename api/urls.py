from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewViewSet 
from .views import ListingViewSet, ListingCSVUploadView


router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'listings', ListingViewSet, basename='listings')


urlpatterns = [
    path('', include(router.urls)),
    path('api/listings/upload-csv/', ListingCSVUploadView.as_view(), name='listing-csv-upload'),

]



