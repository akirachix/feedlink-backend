from django.test import TestCase

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from reviews.models import Review
from orders.models import Order, OrderItem
from inventory.models import Listing


# Create your tests here.
User = get_user_model()




class ReviewModelTest(TestCase):


   def setUp(self):
       self.buyer = User.objects.create_user(
           email='buyer@example.com',
           password='testpass123',
           first_name='Jane',
           last_name='Smith',
           role='buyer'
       )


       self.producer = User.objects.create_user(
           email='producer@example.com',
           password='testpass123',
           first_name='John',
           last_name='Doe',
           role='producer'
       )


       self.listing = Listing.objects.create(
           producer=self.producer,
           product_type='edible',
           quantity=Decimal('10.00'),
           upload_method='manual',
           pickup_window_duration=timezone.now() + timezone.timedelta(hours=48),
           discounted_price=Decimal('5.00')
       )


       self.order1 = Order.objects.create(
           user=self.buyer,
           total_amount=Decimal('10.00'),
           order_status='pending',
           payment_status='unpaid'
       )
       OrderItem.objects.create(
           order=self.order1,
           listing=self.listing,
           quantity=2,
           price=Decimal('5.00')
       )


       self.order2 = Order.objects.create(
           user=self.buyer,
           total_amount=Decimal('5.00'),
           order_status='pending',
           payment_status='unpaid'
       )
       OrderItem.objects.create(
           order=self.order2,
           listing=self.listing,
           quantity=1,
           price=Decimal('5.00')
       )


   def test_create_review_success(self):
       review = Review.objects.create(
           user=self.buyer,
           order=self.order1,
           ratings=5
       )
       self.assertEqual(review.user, self.buyer)
       self.assertEqual(review.order, self.order1)
       self.assertEqual(review.ratings, 5)
       self.assertIsNotNone(review.pk)


   def test_only_buyers_can_create_reviews(self):
       review = Review(
           user=self.producer,
           order=self.order1,
           ratings=4
       )
       with self.assertRaises(ValidationError):
           review.full_clean()


       review = Review(
           user=self.buyer,
           order=self.order1,
           ratings=4
       )
       review.full_clean()


   def test_cascade_delete_user_deletes_reviews(self):
       review = Review.objects.create(
           user=self.buyer,
           order=self.order1,
           ratings=5
       )
       review_id = review.pk


       self.buyer.delete()


       with self.assertRaises(Review.DoesNotExist):
           Review.objects.get(pk=review_id)


   def test_cascade_delete_order_deletes_reviews(self):
       review = Review.objects.create(
           user=self.buyer,
           order=self.order1,
           ratings=5
       )
       review_id = review.pk


       self.order1.delete()


       with self.assertRaises(Review.DoesNotExist):
           Review.objects.get(pk=review_id)


   def test_user_field_required(self):
       review = Review(
           user=None,
           order=self.order1,
           ratings=5
       )
       with self.assertRaises(ValidationError):
           review.full_clean()


   def test_order_field_required(self):
       review = Review(
           user=self.buyer,
           order=None,
           ratings=5
       )
       with self.assertRaises(ValidationError):
           review.full_clean()


   def test_ratings_field_required(self):
       review = Review(
           user=self.buyer,
           order=self.order1,
           ratings=None
       )
       with self.assertRaises(ValidationError):
           review.full_clean()


   def test_string_method_works(self):
       review = Review.objects.create(
           user=self.buyer,
           order=self.order1,
           ratings=5
       )
       expected = f"Review {review.pk} by {self.buyer} for Order {self.order1}"
       self.assertEqual(str(review), expected)


   def test_can_create_multiple_reviews_for_different_orders(self):
       review1 = Review.objects.create(
           user=self.buyer,
           order=self.order1,
           ratings=5
       )
       review2 = Review.objects.create(
           user=self.buyer,
           order=self.order2,
           ratings=4
       )
       self.assertIsNotNone(review1.pk)
       self.assertIsNotNone(review2.pk)
       self.assertEqual(Review.objects.filter(user=self.buyer).count(), 2)



