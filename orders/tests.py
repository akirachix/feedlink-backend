from django.test import TestCase
from django.contrib.auth import get_user_model
from inventory.models import Listing
from .models import Order, OrderItem, WasteClaim
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class OrderTestsMinimalSetup(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='pass',
            first_name='Test',
            last_name='User',
            role='buyer'
        )
        self.producer = User.objects.create_user(
            email='producer@example.com',
            password='pass',
            first_name='Producer',
            last_name='One',
            role='producer'
        )
        self.listing = Listing.objects.create(
            producer=self.producer,
            product_type='edible',
            category='Test Category',
            description='Test Description',
            quantity=10,
            original_price=100.0,
            expiry_date=timezone.now() + timedelta(days=10),
            discounted_price=80.0,
            status='available',
            upload_method='manual',
            pickup_window_duration=timezone.now() + timedelta(days=1),
        )

    def test_order_creation_and_pin(self):
        order = Order.objects.create(user=self.user, total_amount=0)
        self.assertIsNotNone(order.pin)
        self.assertEqual(len(order.pin), 4)

    def test_order_total_amount_updates(self):
        order = Order.objects.create(user=self.user, total_amount=0)
        OrderItem.objects.create(order=order, listing=self.listing, quantity=2, price=80)
        order.refresh_from_db()
        self.assertEqual(order.total_amount, 160)

    def test_waste_claim_creation_and_pin(self):
        self.listing.product_type = 'inedible'
        self.listing.save()
        claim = WasteClaim.objects.create(user=self.user, listing=self.listing)
        self.assertIsNotNone(claim.pin)
        self.assertEqual(len(claim.pin), 4)
