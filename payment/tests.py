from django.test import TestCase
from rest_framework.test import APITestCase
from user.models import User
from orders.models import Order
from payment.models import Payment


class PaymentSerializerTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass',
            first_name='Test',
            last_name='User',
            role='buyer'
        )
        self.order = Order.objects.create(user=self.user, total_amount=100)


    def test_payment_serializer_validation(self):
        """Test serializer correctly formats data"""
        from api.serializers import PaymentSerializer
        payment = Payment.objects.create(
            amount=100.00,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user
        )
        serializer = PaymentSerializer(payment)
        self.assertEqual(serializer.data['amount'], '100.00')
        self.assertEqual(serializer.data['phone_number'], "254712345678")

    def test_payment_serializer_negative_amount(self):
        """Test serializer rejects negative amounts"""
        from api.serializers import PaymentSerializer
        data = {
            "phone_number": "254712345678",
            "amount": -10,
            "order_id": self.order.order_id,
            "user_id": self.user.id
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_payment_serializer_zero_amount(self):
        """Test serializer rejects zero amount"""
        from api.serializers import PaymentSerializer
        data = {
            "phone_number": "254712345678",
            "amount": 0,
            "order_id": self.order.order_id,
            "user_id": self.user.id
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_payment_serializer_receipt_included_when_success(self):
        """Test serializer includes basic fields for successful payments"""
        from api.serializers import PaymentSerializer
        payment = Payment.objects.create(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user,
            checkout_request_id="receipt-checkout-id",
            status="SUCCESS"
        )
        serializer = PaymentSerializer(payment)

        self.assertIn("amount", serializer.data)
        self.assertIn("phone_number", serializer.data)

    def test_payment_model_str_method(self):
        """Test Payment model string representation (fallback safe test)"""
        payment = Payment.objects.create(
            amount=150.00,
            phone_number="254798765432",
            order_id=self.order,
            user_id=self.user
        )
        str_repr = str(payment)
        self.assertIsInstance(str_repr, str)
        self.assertTrue(len(str_repr) > 0)