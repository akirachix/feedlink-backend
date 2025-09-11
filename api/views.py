
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from reviews.models import Review          
from .serializers import ReviewSerializer  


from rest_framework.views import APIView
from inventory.models import Listing
from .serializers import ListingSerializer
import csv
from io import TextIOWrapper

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
class ListingCSVUploadView(APIView):
    def post(self, request):
        file = request.FILES.get('csv_file')
        if not file:
            return Response({"error": "No CSV file uploaded."}, status=status.HTTP_400_BAD_REQUEST)
        reader = csv.DictReader(TextIOWrapper(file, encoding='utf-8'))
        listings_created = []
        errors = []
        for row in reader:
            serializer = ListingSerializer(data=row)
            if serializer.is_valid():
                instance = serializer.save(status='available', upload_method='csv')
                listings_created.append(serializer.data)
            else:
                errors.append({
                    "row": row,
                    "errors": serializer.errors
                })
        if errors:
            return Response({
                "created": listings_created,
                "errors": errors
            }, status=status.HTTP_207_MULTI_STATUS)
        else:
            return Response({
                "listings": listings_created
            }, status=status.HTTP_201_CREATED)