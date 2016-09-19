import json
import hashlib
import datetime
import requests

"""
Usage:

client = IcepayClient(MERCHANT_ID, SECRET_CODE)

#create order
order_data = client.Checkout({
    "Amount": "1",
    "Country": "LT",
    "Currency": "EUR",
    "Description": "Test",
    "EndUserIP": "127.0.0.1",
    "PaymentMethod": "PAYPAL",
    "Issuer": "DEFAULT",
    "Language": "EN",
    "OrderID": "10000031",
    "URLCompleted": "https://mywebshop.com/Payment/Success",
    "URLError": "https://mywebshop.com/Payment/Failure"
})

payment_data = client.GetPayment(order_data['PaymentID'])

"""

class IcepayClient:

    BASE_API_URL = 'https://connect.icepay.com/webservice/api/v1/'

    def __init__(self, merchant_id, secret_code):
        self.merchant_id = merchant_id
        self.secret_code = secret_code


    def calc_checksum(self, url, method, body):
        assert isinstance(body, str), 'body must be a string'

        parts = [
            url,
            method,
            self.merchant_id,
            self.secret_code,
            body
        ]

        sig = ''.join([str(x) for x in parts])

        m = hashlib.sha256()
        m.update(sig.encode('utf8'))
        return m.hexdigest()

    def validate_postback(self, data):
        """
        data is QueryDict or dict, values received in POST.
        calcs and checks sha1 digest
        """
        parts = [
            self.secret_code,
            self.merchant_id,
            data.get('Status'),
            data.get('StatusCode'),
            data.get('OrderID'),
            data.get('PaymentID'),
            data.get('Reference'),
            data.get('TransactionID'),
            data.get('Amount'),
            data.get('Currency'),
            data.get('Duration'),
            data.get('ConsumerIPAddress')
        ]

        sig = '|'.join([str(x) for x in parts])

        m = hashlib.sha1()
        m.update(sig.encode('utf8'))
        digest = m.hexdigest()
        checksum = data.get('Checksum')
        assert digest == checksum, 'invalid postback checksum'

    def format_timestamp(self, time=None):
        #returns timestamp formatted as per icepay specs. must be utc.
        #returns now() if specific time not provided
        time = time or datetime.datetime.utcnow()
        return time.isoformat()[:19]

    def call_api(self, method, endpoint, data={}):
        assert method in ['POST', 'GET'], 'invalid method: %s, expected POST or GET' % method

        if 'Timestamp' not in data:
            data['Timestamp'] = self.format_timestamp()

        full_url = self.BASE_API_URL + endpoint

        data = json.dumps(data, separators=(',', ':'))

        headers = {
            'MerchantID': str(self.merchant_id),
            'Checksum': self.calc_checksum(full_url, method, data),
            'Content-Type': 'application/json'
        }

        if method == 'POST':
            r = requests.post(full_url, headers=headers, data=data)
        else:
            r = requests.get(full_url, headers=headers, data=data)

        if r.status_code == requests.codes.ok:
            checksum = self.calc_checksum(full_url, method, str(r.text))
            assert r.headers['Checksum'] == checksum, 'checksum verification failed'
            return r.json()
        else:
            r.raise_for_status()


    def GetMyPaymentMethods(self):
        return self.call_api('POST', 'payment/getmypaymentmethods')

    def Checkout(self, values):
        return self.call_api('POST', 'payment/checkout', values)

    def GetPayment(self, PaymentID):
        return self.call_api('POST', 'payment/getpayment', {"PaymentID": PaymentID})
