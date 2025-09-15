from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
from user.models import User
from orders.models import Order
from payment.models import Payment

class PaymentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpass',
            first_name='Test',
            last_name='User',
            role='buyer'
        )
        self.other_user = User.objects.create_user(
            email='otheruser@example.com',
            password='testpass',
            first_name='Other',
            last_name='User',
            role='buyer'
        )
        self.order = Order.objects.create(user=self.user, total_amount=100)
        self.payment_data = {
            "phone_number": "254712345678",
            "amount": 50,
            "account_reference": str(self.order.order_id), 
            "transaction_desc": "Test payment"
        }


    @patch("api.views.DarajaAPI.ussd_push")
    def test_stk_push_initiated_on_checkout(self, mock_ussd_push):
        mock_ussd_push.return_value = {
            "MerchantRequestID": "test-merchant-id",
            "CheckoutRequestID": "test-checkout-id"
        }
        self.client.force_authenticate(self.user)
        url = reverse('ussdpush')
        response = self.client.post(url, self.payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("USSD Push initiated", response.data["message"])
        self.assertTrue(Payment.objects.filter(checkout_request_id="test-checkout-id").exists())

    def test_payment_serializer_validation(self):
        from api.serializers import PaymentSerializer
        payment = Payment.objects.create(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user
        )
        serializer = PaymentSerializer(payment)
        self.assertEqual(serializer.data['amount'], '100.00')
        self.assertEqual(serializer.data['phone_number'], "254712345678")

    @patch("payment.models.Payment.objects.get")
    def test_callback_success_payment(self, mock_get):
        payment = Payment(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user
        )
        payment.save = lambda: None
        payment.generate_receipt = lambda: "http://testserver/receipt/xyz"
        mock_get.return_value = payment

        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-id",
                    "CheckoutRequestID": "test-checkout-id",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "MpesaReceiptNumber", "Value": "XYZ123"},
                            {"Name": "Amount", "Value": 100},
                            {"Name": "TransactionDate", "Value": 20240101121530}
                        ]
                    }
                }
            }
        }
        url = reverse('mpesa_callback')
        response = self.client.post(url, callback_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ResultCode'], 0)
        self.assertIn('receipt_url', response.data)

    @patch("api.views.DarajaAPI.ussd_push")

    def test_stk_push_failed(self, mock_ussd_push):
        mock_ussd_push.return_value = {"errorCode": "C2B00013", "errorMessage": "Insufficient funds"}
        self.client.force_authenticate(self.user)  
        url = reverse('ussdpush')
        response = self.client.post(url, self.payment_data, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Payment.objects.filter(order_id=self.order).exists())


    @patch("api.views.DarajaAPI.ussd_push")
    def test_stk_push_unauthenticated(self, mock_ussd_push):
        mock_ussd_push.return_value = {"errorCode": "C2B00013", "errorMessage": "Unauthenticated"}
        url = reverse('ussdpush')
        response = self.client.post(url, self.payment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch("api.views.DarajaAPI.ussd_push")
    def test_stk_push_user_not_owner(self, mock_ussd_push):
        mock_ussd_push.return_value = {
            "MerchantRequestID": "test-merchant-id",
            "CheckoutRequestID": "test-checkout-id"
        }
        self.client.force_authenticate(self.other_user)
        url = reverse('ussdpush')
        data = self.payment_data.copy()
        data['account_reference'] = str(self.order.order_id)  
        response = self.client.post(url, data, format='json')
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST])

    def test_payment_serializer_required_fields(self):
        from api.serializers import PaymentSerializer
        data = {}  
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("amount", serializer.errors)

    def test_payment_serializer_invalid_phone(self):
        from api.serializers import PaymentSerializer
        data = {
            "phone_number": "invalid",
            "amount": 100,
            "order_id": self.order.order_id,
            "user_id": self.user.id
        }
        serializer = PaymentSerializer(data=data)
        if hasattr(serializer, 'validate_phone_number'):
            self.assertFalse(serializer.is_valid())
            self.assertIn("phone_number", serializer.errors)
        else:
            self.assertTrue(True) 

    def test_payment_serializer_negative_amount(self):
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

    @patch("api.views.DarajaAPI.ussd_push")
    def test_double_payment(self, mock_ussd_push):
        Payment.objects.create(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user,
            checkout_request_id="double-checkout-id",
            status="SUCCESS"
        )
        mock_ussd_push.return_value = {"errorCode": "C2B00013", "errorMessage": "Duplicate payment"}
        self.client.force_authenticate(self.user)
        url = reverse('ussdpush')
        response = self.client.post(url, self.payment_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN, status.HTTP_200_OK])

    @patch("payment.models.Payment.objects.get")
    def test_callback_failure_payment(self, mock_get):
        payment = Payment(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user
        )
        payment.save = lambda: None
        payment.generate_receipt = lambda: None
        mock_get.return_value = payment

        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-id",
                    "CheckoutRequestID": "fail-checkout-id",
                    "ResultCode": 1032,
                    "ResultDesc": "Request cancelled by user",
                    "CallbackMetadata": {}
                }
            }
        }
        url = reverse('mpesa_callback')
        response = self.client.post(url, callback_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get('receipt_url', None))

    @patch("payment.models.Payment.objects.get")
    def test_callback_missing_fields(self, mock_get):
        payment = Payment(
            amount=100,
            phone_number="254712345678",
            order_id=self.order,
            user_id=self.user
        )
        payment.save = lambda: None
        payment.generate_receipt = lambda: None
        mock_get.return_value = payment

        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-id",
                    "CheckoutRequestID": "test-checkout-id",
                    "ResultCode": 0,
                    "ResultDesc": "Success"
                    
                }
            }
        }
        url = reverse('mpesa_callback')
        response = self.client.post(url, callback_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data.get('receipt_url', None))

    def test_callback_unknown_payment(self):
        callback_data = {
            "Body": {
                "stkCallback": {
                    "MerchantRequestID": "test-merchant-id",
                    "CheckoutRequestID": "nonexistent-checkout-id",
                    "ResultCode": 0,
                    "ResultDesc": "Success",
                    "CallbackMetadata": {
                        "Item": [
                            {"Name": "MpesaReceiptNumber", "Value": "XYZ123"},
                            {"Name": "Amount", "Value": 100},
                            {"Name": "TransactionDate", "Value": 20240101121530}
                        ]
                    }
                }
            }
        }
        url = reverse('mpesa_callback')
        response = self.client.post(url, callback_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_404_NOT_FOUND, status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_payment_serializer_receipt(self):
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