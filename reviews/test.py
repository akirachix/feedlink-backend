from django.test import TestCase
from .models import Review

class ReviewModelTest(TestCase):
    def test_create_review(self):
        review = Review.objects.create(ratings=5)
        self.assertEqual(review.ratings, 5)
        self.assertIsNotNone(review.review_id)
        self.assertEqual(str(review), f"Review {review.review_id} - {review.ratings} stars")

    def test_create_review_with_2_stars(self):
        review = Review.objects.create(ratings=2)
        self.assertEqual(review.ratings, 2)
        self.assertIsNotNone(review.review_id)
        self.assertEqual(str(review), f"Review {review.review_id} - {review.ratings} stars")

    def test_create_review_with_1_star(self):
        review = Review.objects.create(ratings=1)
        self.assertEqual(review.ratings, 1)
        self.assertIsNotNone(review.review_id)
        self.assertEqual(str(review), f"Review {review.review_id} - {review.ratings} stars")