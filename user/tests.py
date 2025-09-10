from django.test import TestCase
from user.models import User

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name='Semhal',
            last_name='Estifanos',
            email='semhal@gmail.com',
            password='testpass123',
            role='producer',
            till_number='1234'
        )

    def test_fields(self):
        user = self.user
        self.assertEqual(user.first_name, 'Semhal')
        self.assertEqual(user.last_name, 'Estifanos')
        self.assertEqual(user.email, 'semhal@gmail.com')
        self.assertEqual(user.role, 'producer')
        self.assertTrue(user.check_password('semu123'))
        self.assertEqual(user.till_number, '1234')

    def test_user(self):
        self.assertEqual(str(self.user), 'Semhal Estifanos')

    def test_non_producer(self):
        user = User.objects.create_user(
            first_name='Bruk',
            last_name='Estifanos',
            email='bruk@gmail.com',
            password='bruk123',
            role='buyer',
        )
        self.assertEqual(user.role, 'buyer')
        self.assertIsNone(user.till_number)
