import urllib.request
import json
import hashlib
import datetime


class IcepayApiClient:
    CHECKOUT_URL = 'payment/checkout'
    REFUND_URL = 'refund/requestrefund'
    PAYMENT_REFUNDS_URL = 'refund/getpaymentrefunds'
    GET_MY_PAYMENT_METHODS_URL = 'payment/getmypaymentmethods'
    GET_PAYMENT_URL = 'payment/getpayment'

    # BASE_API_URL = 'https://connect.icepay.com/webservice/api/v1/'

    def __init__(self, merchant_id, secret_code, base_api_url):
        self.base_url = base_api_url
        self.secret_code = secret_code
        self.merchant_id = merchant_id

    def format_timestamp(self, now=None):
        now = now or datetime.datetime.utcnow()
        return now.isoformat()[:19]

    def calc_checksum(self, url, method, body):
        if not isinstance(body, str):
            raise Exception('body must be a string')

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

    def _prepare_http_headers(self, full_url, method, raw_data):
        return {
            'Content-Type': 'application/json',
            'Checksum': self.calc_checksum(full_url, method, raw_data),
            'Merchantid': self.merchant_id
        }

    def _make_api_call(self, method, endpoint, data=None):
        data = data or {}

        if 'Timestamp' not in data:
            data['Timestamp'] = self.format_timestamp()

        raw_data = json.dumps(data, separators=(',', ':'))
        full_url = self.base_url + endpoint
        headers = self._prepare_http_headers(full_url, method, raw_data)
        utf8_raw_data = raw_data.encode('utf-8')

        req = urllib.request.Request(
            full_url,
            utf8_raw_data,
            headers=headers
        )

        response = urllib.request.urlopen(req)
        content = response.read().decode('utf-8')

        return json.loads(content)

    def checkout(self, payment_uuid, amount, country, user_ip_address,
                 description, issuer, payment_method, currency='EUR',
                 language='EN', url_completed=None, url_error=None):
        data = {
            'Timestamp': self.format_timestamp(),
            'Amount': amount,
            'Country': country,
            'Currency': currency,
            'Description': description,
            'EndUserIP': user_ip_address,
            'PaymentMethod': payment_method,
            'Issuer': issuer,
            'Language': language,
            'OrderID': payment_uuid,
        }

        if url_completed:
            data['URLCompleted'] = url_completed

        if url_error:
            data['URLError'] = url_error

        response = self._make_api_call('POST', self.CHECKOUT_URL, data)

        return response

    def get_my_payment_methods(self):
        return self._make_api_call('POST', self.GET_MY_PAYMENT_METHODS_URL)

    def validate_postback(self, postback_data):
        """Calculate and check sha1 digest.

        postback_data is QueryDict or dict, values received in POST.
        """
        parts = [
            self.secret_code,
            self.merchant_id,
            postback_data['Status'],
            postback_data['StatusCode'],
            postback_data['OrderID'],
            postback_data['PaymentID'],
            postback_data['Reference'],
            postback_data['TransactionID'],
            postback_data['Amount'],
            postback_data['Currency'],
            postback_data['Duration'],
            postback_data['ConsumerIPAddress']
        ]

        digest = self.list_to_sha1(parts)
        checksum = postback_data.get('Checksum')

        return digest == checksum
        # assert digest == checksum, 'invalid postback checksum'

    def validate_web_redirect(self, get_params):
        """Calc and checks sha1 digest.

        get_params is all GET params that icepay adds to redirect url.
        """
        parts = [
            self.secret_code,
            self.merchant_id,
            get_params['Status'],
            get_params['StatusCode'],
            get_params['OrderID'],
            get_params['PaymentID'],
            get_params['Reference'],
            get_params['TransactionID'],
        ]

        digest = self.list_to_sha1(parts)
        checksum = get_params.get('Checksum')

        return digest == checksum

    @staticmethod
    def list_to_sha1(parts):
        """Convert input list to sha1."""
        sig = '|'.join(str(x) for x in parts if x is not None)

        m = hashlib.sha1()
        m.update(sig.encode('utf8'))
        return m.hexdigest()

    def get_payment(self, payment_id):
        data = {
            'PaymentID': payment_id
        }
        return self._make_api_call('POST', self.GET_PAYMENT_URL, data)

    def refund(self, payment_id, amount, currency='EUR'):
        data = {
            'PaymentID': payment_id,
            'RefundAmount': amount,
            'RefundCurrency': currency,
        }
        return self._make_api_call('POST', self.REFUND_URL, data)

    def get_payment_refunds(self, payment_id):
        data = {
            'PaymentID': payment_id,
        }
        return self._make_api_call('POST', self.PAYMENT_REFUNDS_URL, data)
