from django.shortcuts import render
from .serializers import USSDPUSHSerializer, PaymentSerializer
from rest_framework import status, viewsets
from .daraja import DarajaAPI
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from payment.models import Payment
import datetime


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class USSDPUSHView(APIView):
    def post(self, request):
        serializer = USSDPUSHSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            daraja = DarajaAPI()
            ussd_response = daraja.ussd_push(
                phone_number=data["phone_number"],
                amount=float(data["amount"]),
                account_reference=data["account_reference"],
                transaction_desc=data["transaction_desc"],
            )
            merchant_request_id = ussd_response.get("MerchantRequestID")
            checkout_request_id = ussd_response.get("CheckoutRequestID")
            print("Saved checkout requestID:", checkout_request_id)
            Payment.objects.create(
                amount=float(data["amount"]),
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id,
                status="PENDING"
            )
            return Response(
                {
                    "message": "USSD Push initiated, check your phone to complete the payment.",
                    "response": ussd_response,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["POST"])
def mpesa_ussd_callback(request):
    print("Daraja Callback Data:", request.data)
    body = request.data.get("Body", {})
    stk_callback = body.get("stkCallback", {})
    merchant_request_id = stk_callback.get("MerchantRequestID")
    checkout_request_id = stk_callback.get("CheckoutRequestID")
    result_code = int(stk_callback.get("ResultCode", 1))
    result_desc = stk_callback.get("ResultDesc")
    try:
        payment = Payment.objects.get(checkout_request_id=checkout_request_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)
    payment.merchant_request_id = merchant_request_id
    payment.result_code = result_code
    payment.result_desc = result_desc
    receipt_url = None
    if result_code == 0:
        metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
        parsed_metadata = {item["Name"]: item.get("Value") for item in metadata}
        payment.mpesa_receipt_number = parsed_metadata.get("MpesaReceiptNumber")
        payment.amount = parsed_metadata.get("Amount", payment.amount)
        txn_date = parsed_metadata.get("TransactionDate")
        if txn_date:
            txn_date_str = str(txn_date)
            payment.payment_date = datetime.strptime(txn_date_str, "%Y%m%d%H%M%S")
        payment.status = "SUCCESS"
        receipt_url = payment.generate_receipt()
    else:
        payment.status = "FAILED"
    payment.save()
    return Response({
        "ResultCode": 0,
        "ResultDesc": "Callback processed successfully",
        "receipt_url": receipt_url,
    })