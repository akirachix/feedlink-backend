
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from reviews.models import Review

class ReviewAPITestCase(APITestCase):
    def setUp(self):
        self.review = Review.objects.create(ratings=4)

    def test_list_reviews(self):
        url = reverse('review-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(r['review_id'] == self.review.review_id for r in response.data))

    def test_create_review_valid(self):
        url = reverse('review-list')
        data = {'ratings': 5}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['ratings'], 5)
        self.assertTrue('review_id' in response.data)

    def test_create_review_invalid_rating(self):
        url = reverse('review-list')
        data = {'ratings': 6} 
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ratings', response.data)
