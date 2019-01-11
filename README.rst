Icepay Python Client
--------------------

Python client for Icepay REST API, https://icepay.com/docs/rest-api/


Usage
-----

.. code:: python

    from icepay import IcepayClient

    BASE_API_URL = 'https://connect.icepay.com/webservice/api/v1/'
    MERCHANT_ID = 'xxx'
    SECRET_CODE = 'yyy'

    # init client
    client = IcepayClient(MERCHANT_ID, SECRET_CODE, BASE_API_URL)


    # get own payment methods
    payment_methods = client.get_my_payment_methods()

    # start checkout
    icepay_response = client.checkout(
        payment_uuid='abc123',  # local payment id
        amount='10000',  # amount in cents (100 here)
        country='NL',  # country code
        user_ip_address='1.2.3.4',
        description='payment for something',
        issuer='VISA',  # 'VISA'/'ING'/'DEFAULT' ...
        payment_method='CREDITCARD',  # 'CREDITCARD'/'IDEAL'/'PAYPAL' ...
        currency='EUR',
        language='EN',
        url_completed='https://site.com/success_url',
        url_error='https://site.com/error_url',
    )

    # icepay_response['PaymentScreenURL'] - url where user should be redirected to complete payment

    # get payment info by id
    payment = client.get_payment('1232')

    # validate postback checksum
    # request.POST is dict or QueryDict with key:value map of post data
    # returns True/False
    client.validate_postback(request.POST) 

    # validate web redirect from icepay
    # get_params is dict with GET params got from icepay in a redirect url
    payment = client.validate_web_redirect(get_params)

    # make refund
    client.refund(payment_id, amount, currency='EUR')

    # get all refunds related to some payment
    client.get_payment_refunds(payment_id):


Used with python 3.5.x
-----
