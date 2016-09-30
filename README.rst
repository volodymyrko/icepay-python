Icepay Python Client
--------------------

Python client for Icepay REST API, https://icepay.com/docs/rest-api/

Install
-------

::

    pip install icepay-python

Usage
-----

.. code:: python

    from icepay import IcepayClient

    #init client
    client = IcepayClient(MERCHANT_ID, SECRET_CODE)


    #get own payment methods
    payment_methods = client.GetMyPaymentMethods()

    #checkout
    order_data = client.Checkout({
        "Amount": "1",
        "Country": "US",
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

    #get payment info by id
    payment = client.GetPayment(1232)

    #validate postback checksum
    # request.POST is dict or QueryDict with key:value map of post data
    # throws AssertionError on failure
    client.validate_postback(request.POST) 


    #generate URL for the BASIC payment mode
    url = client.getBasicPaymentURL({
        'IC_OrderID': 123,
        'IC_Amount': 100,
        'IC_Currency': 'EUR',
        'IC_Country': 'US',
        'IC_URLCompleted': 'https://mywebshop.com/Payment/Success',
        'IC_URLError': 'https://mywebshop.com/Payment/Failure'
    })

Advanced usage
--------------

.. code:: python


    #make an API call for an endpoint that doesnt have a helper in this lib
    #note that timestamp is auto added if it's not present
    values = {
        #request data
    }
    order = client.call_api('POST', 'payment/vaultcheckout', values)
