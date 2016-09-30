import json
import hashlib
import datetime
import requests
import urllib

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
    BASIC_PAYMENT_URL = 'https://pay.icepay.eu/basic/'

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


    def getBasicPaymentURL(self, values):
        """
        url = client.getBasicPaymentURL({
            'IC_OrderID': 123,
            'IC_Amount': 100,
            'IC_Currency': 'EUR',
            'IC_Country': 'LT',
            'IC_URLCompleted': 'http://example.com/success',
            'IC_URLError': 'http://example.com/fail'
        })
        """

        ALL_FIELDS = ['IC_OrderID', 'IC_Amount', 'IC_Currency', 'IC_PaymentMethod', 'IC_Issuer', 'IC_Country',
                        'IC_Reference', 'IC_Description', 'IC_URLCompleted', 'IC_URLError', 'IC_PBMID']
        REQUIRED_FIELDS = ['IC_Amount', 'IC_Currency', 'IC_Country', 'IC_OrderID']

        CHECKSUM_FIELDS = ['IC_Amount', 'IC_OrderID', 'IC_Reference', 'IC_Currency', 'IC_Country',
                           'IC_URLCompleted', 'IC_URLError']


        #some validation
        assert isinstance(values, dict), 'values must be a dict'

        missing_fields = [field for field in REQUIRED_FIELDS if field not in values]
        assert len(missing_fields) == 0, 'Missing fields: %s' % ', '.join(missing_fields)

        unknown_fields = [key for key in values.keys() if key not in ALL_FIELDS]
        assert len(unknown_fields) == 0, 'Unknown fields: %s' % ', '.join(unknown_fields)

        assert isinstance(values['IC_Amount'], int), 'IC_Amount must be int, amount in cents.'

        values['IC_MerchantID'] = self.merchant_id
        values['IC_Version'] = 2

        #calc signature
        parts = [self.merchant_id, self.secret_code]  + [values.get(field, None) for field in CHECKSUM_FIELDS]
        sig = '|'.join([str(part if (part or part == 0) else '') for part in parts])
        m = hashlib.sha1()
        m.update(sig.encode('utf8'))

        values['chk'] = m.hexdigest()

        return self.BASIC_PAYMENT_URL + '?' + urllib.urlencode(values)
