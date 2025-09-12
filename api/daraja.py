import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
import base64
import datetime
        

class DarajaAPI:
    def __init__(self):
        self.consumer_key = settings.DARAJA_CONSUMER_KEY
        self.consumer_secret = settings.DARAJA_CONSUMER_SECRET
        self.base_url = settings.DARAJA_BASE_URL
        self.callback_url = settings.DARAJA_CALLBACK_URL
        self.passkey = settings.DARAJA_PASSKEY
        self.business_shortcode = settings.DARAJA_BUSINESS_SHORTCODE
        self.merchant_request_id = settings.DARAJA_MERCHANT_REQUEST_ID

    def get_access_token(self):
        url = f"{self.base_url}oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(
            url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        )
        response.raise_for_status()
        access_token = response.json().get("access_token")
        return access_token
    
    def ussd_push(self, amount, phone_number, account_reference, transaction_desc):
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        data_to_encode = (
            str(self.business_shortcode) + str(self.passkey) + str(timestamp)
        )
        password = base64.b64encode(data_to_encode.encode()).decode("utf-8")
        access_token = self.get_access_token()
        url = f"{self.base_url}mpesa/stkpush/v1/processrequest"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        data = {
            "BusinessShortCode": self.business_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": self.business_shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": self.callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"--- Daraja API Error Details ---")
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            try:
                print(f"Response JSON: {response.json()}")
            except requests.exceptions.JSONDecodeError:
                print("Response body is not valid JSON.")
        print(f"--- End of Error Details ---")
        response.raise_for_status()
        return response.json()