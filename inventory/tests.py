from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from inventory.models import Listing
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

User = get_user_model()


class ListingModelTest(TestCase):

    def setUp(self):
        self.producer = User.objects.create_user(
            email='producer@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role='producer',
            latitude=Decimal('1.234567'),
            longitude=Decimal('2.345678')
        )

        self.buyer = User.objects.create_user(
            email='buyer@example.com',
            password='testpass123',
            first_name='Jane',
            last_name='Smith',
            role='buyer'
        )

        self.recycler = User.objects.create_user(
            email='recycler@example.com',
            password='testpass123',
            first_name='Bob',
            last_name='Green',
            role='recycler'
        )

        self.listing_data = {
            'producer': self.producer,
            'product_type': 'edible',
            'category': 'Fruits',
            'description': 'Fresh apples',
            'quantity': Decimal('10.50'),
            'original_price': Decimal('20.00'),
            'discounted_price': Decimal('15.00'),
            'expiry_date': timezone.now() + timedelta(days=7),
            'status': 'available',
            'upload_method': 'manual',
            'pickup_window_duration': timezone.now() + timedelta(hours=48),
            'unit': 'kg',
        }

    def test_create_listing_with_producer(self):
  
        listing = Listing.objects.create(**self.listing_data)
        self.assertEqual(listing.producer, self.producer)
        self.assertEqual(str(listing), "10.50 kg of edible")
        self.assertIsNotNone(listing.created_at)
        self.assertIsNotNone(listing.updated_at)

    def test_listing_requires_producer_role(self):
       
        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.buyer,  
                product_type='edible',
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='kg'
            )
            listing.full_clean() 

        listing = Listing(
            producer=self.producer,
            product_type='edible',
            quantity=Decimal('5.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='kg'
        )
        listing.full_clean()  

    def test_string_representation(self):
      
        listing = Listing.objects.create(**self.listing_data)
        expected_str = f"{listing.quantity} {listing.unit} of {listing.product_type}"
        self.assertEqual(str(listing), expected_str)

    def test_default_status(self):
    
        listing = Listing.objects.create(
            producer=self.producer,
            product_type='inedible',
            quantity=Decimal('3.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='unit'
        )
        self.assertEqual(listing.status, 'available')

    def test_expiry_date_can_be_null(self):

        listing = Listing.objects.create(
            producer=self.producer,
            product_type='inedible',
            quantity=Decimal('5.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='unit',
            expiry_date=None
        )
        self.assertIsNone(listing.expiry_date)

    def test_required_fields(self):
     
        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.producer,
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='kg'
            )
            listing.full_clean()

        with self.assertRaises(IntegrityError):
            listing = Listing(
                product_type='edible',
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='kg'
            )
            listing.save()

    def test_choices_validation(self):
      
        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.producer,
                product_type='invalid_type', 
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='kg'
            )
            listing.full_clean()

        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.producer,
                product_type='edible',
                quantity=Decimal('5.00'),
                upload_method='invalid_method', 
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='kg'
            )
            listing.full_clean()

        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.producer,
                product_type='edible',
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=timezone.now() + timedelta(hours=24),
                unit='invalid_unit'  
            )
            listing.full_clean()

    def test_auto_fields(self):

        listing = Listing.objects.create(**self.listing_data)
        self.assertIsNotNone(listing.created_at)
        self.assertIsNotNone(listing.updated_at)
        old_updated_at = listing.updated_at

        listing.quantity = Decimal('20.00')
        listing.save()

        listing.refresh_from_db()
        self.assertNotEqual(listing.updated_at, old_updated_at)
        self.assertGreater(listing.updated_at, listing.created_at)

    def test_image_and_image_url_optional(self):
   
        listing = Listing.objects.create(
            producer=self.producer,
            product_type='edible',
            quantity=Decimal('5.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='kg'
        )
        self.assertFalse(listing.image)  
        self.assertIsNone(listing.image_url)

    def test_original_and_discounted_price_optional(self):
      
        listing = Listing.objects.create(
            producer=self.producer,
            product_type='edible',
            quantity=Decimal('5.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='kg'
        )
        self.assertIsNone(listing.original_price)
        self.assertIsNone(listing.discounted_price)

    def test_category_and_description_optional(self):
       
        listing = Listing.objects.create(
            producer=self.producer,
            product_type='edible',
            quantity=Decimal('5.00'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='kg'
        )
        self.assertIsNone(listing.category)
        self.assertIsNone(listing.description)

    def test_listing_id_auto_increment(self):
    
        listing1 = Listing.objects.create(**self.listing_data)
        listing2 = Listing.objects.create(**self.listing_data)
        self.assertEqual(listing2.listing_id, listing1.listing_id + 1)

    def test_pickup_window_duration_required(self):
      
        with self.assertRaises(ValidationError):
            listing = Listing(
                producer=self.producer,
                product_type='edible',
                quantity=Decimal('5.00'),
                upload_method='manual',
                pickup_window_duration=None,  
                unit='kg'
            )
            listing.full_clean()

    def test_quantity_positive(self):

        listing = Listing.objects.create(
            producer=self.producer,
            product_type='edible',
            quantity=Decimal('0.01'),
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(hours=24),
            unit='kg'
        )
        self.assertEqual(listing.quantity, Decimal('0.01'))