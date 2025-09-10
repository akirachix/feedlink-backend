from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from io import StringIO
from datetime import datetime, timezone
from .models import Listing

class ListingAPITestCase(TestCase):
   
    def setUp(self):
        self.client = APIClient()
        self.list_url = reverse('listings-list') 
        self.upload_csv_url = reverse('listing-csv-upload')

        
        self.valid_listing_data = {
            'product_type': 'edible',
            'category': 'Fruits',
            'description': 'Fresh apples',
            'quantity': 25.0,
            'original_price': 50.00,
            'discounted_price': 40.00,
            'expiry_date': '2025-12-31T18:00:00Z',
            'image_url': 'https://example.com/apples.jpg',
            'upload_method': 'manual',
            'pickup_window_duration': '2025-09-15T10:00:00Z',
        }

  

    def test_create_listing_manually(self):
      
        response = self.client.post(self.list_url, self.valid_listing_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Listing.objects.count(), 1)
        listing = Listing.objects.first()
        self.assertEqual(listing.product_type, 'edible')
        self.assertEqual(listing.status, 'available')  

    def test_list_listings(self):
        
        Listing.objects.create(
            product_type='edible',
            category='Vegetables',
            description='Carrots',
            quantity=10.0,
            original_price=20.00,
            discounted_price=15.00,
            expiry_date='2025-10-01T12:00:00Z',
            image_url='https://example.com/carrots.jpg',
            upload_method='manual',
            pickup_window_duration='2025-09-10T09:00:00Z',
            status='available'
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['category'], 'Vegetables')

    def test_retrieve_listing(self):
       
        listing = Listing.objects.create(
            product_type='inedible',
            category='Tools',
            description='Hammer',
            quantity=1.0,
            original_price=100.00,
            discounted_price=80.00,
            expiry_date='2025-11-01T10:00:00Z',
            image_url='https://example.com/hammer.jpg',
            upload_method='manual',
            pickup_window_duration='2025-09-12T14:00:00Z',
            status='available'
        )

        url = reverse('listings-detail', kwargs={'pk': listing.listing_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Hammer')

    def test_update_listing(self):
       
        listing = Listing.objects.create(
            product_type='edible',
            category='Dairy',
            description='Milk',
            quantity=5.0,
            original_price=10.00,
            discounted_price=8.00,
            expiry_date='2025-09-10T08:00:00Z',
            image_url='https://example.com/milk.jpg',
            upload_method='manual',
            pickup_window_duration='2025-09-09T18:00:00Z',
            status='available'
        )

        url = reverse('listings-detail', kwargs={'pk': listing.listing_id})
        updated_data = self.valid_listing_data.copy()
        updated_data['description'] = 'Organic Milk'
        updated_data['quantity'] = 10.0

        response = self.client.put(url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        listing.refresh_from_db()
        self.assertEqual(listing.description, 'Organic Milk')
        self.assertEqual(float(listing.quantity), 10.0)

    def test_delete_listing(self):
       
        listing = Listing.objects.create(
            product_type='edible',
            category='Bakery',
            description='Bread',
            quantity=3.0,
            original_price=5.00,
            discounted_price=4.00,
            expiry_date='2025-09-10T07:00:00Z',
            image_url='https://example.com/bread.jpg',
            upload_method='manual',
            pickup_window_duration='2025-09-09T17:00:00Z',
            status='available'
        )

        url = reverse('listings-detail', kwargs={'pk': listing.listing_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Listing.objects.count(), 0)


    def test_upload_valid_csv(self):
        
        csv_content = (
            "product_type,category,description,quantity,original_price,discounted_price,expiry_date,image_url,upload_method,pickup_window_duration\n"
            "edible,Vegetables,Tomatoes,10.5,50.00,40.00,2025-12-31T18:00:00Z,https://example.com/tomatoes.jpg,csv,2025-09-15T10:00:00Z\n"
            "inedible,Tools,Shovel,1.0,100.00,80.00,2025-10-01T12:00:00Z,https://example.com/shovel.jpg,csv,2025-09-15T14:30:00Z\n"
        )

        csv_file = StringIO(csv_content)
        csv_file.name = 'test.csv'

        response = self.client.post(self.upload_csv_url, {'csv_file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['listings']), 2)
        self.assertEqual(Listing.objects.count(), 2)

    def test_upload_csv_missing_file(self):
      
        response = self.client.post(self.upload_csv_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_upload_csv_invalid_row(self):
       
        csv_content = (
            "product_type,category,description,quantity,original_price,discounted_price,expiry_date,image_url,upload_method,pickup_window_duration\n"
            "edible,Vegetables,Tomatoes,10.5,50.00,40.00,2025-12-31T18:00:00Z,,csv,2025-09-15T10:00:00Z\n"
        )

        csv_file = StringIO(csv_content)
        csv_file.name = 'invalid.csv'

        response = self.client.post(self.upload_csv_url, {'csv_file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(Listing.objects.count(), 0)



    def test_create_listing_missing_required_field(self):
       
        invalid_data = self.valid_listing_data.copy()
        del invalid_data['image_url'] 

        response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_create_listing_invalid_datetime(self):
        
        invalid_data = self.valid_listing_data.copy()
        invalid_data['pickup_window_duration'] = '2:00:00' 

        response = self.client.post(self.list_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('pickup_window_duration', response.data)

    def test_upload_csv_empty(self):
       
        csv_content = "product_type,category,description,quantity,original_price,discounted_price,expiry_date,image_url,upload_method,pickup_window_duration\n"

        csv_file = StringIO(csv_content)
        csv_file.name = 'empty.csv'

        response = self.client.post(self.upload_csv_url, {'csv_file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['listings'], [])
        self.assertEqual(Listing.objects.count(), 0)