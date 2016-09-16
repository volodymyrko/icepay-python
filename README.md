Icepay Python Client
=======================

Python client for Icepay REST API, https://icepay.com/docs/rest-api/

## Install

```
pip install icepay-python
```

## Usage

```python
from icepay import IcepayClient

#init client
client = IcepayClient(MERCHANT_ID, SECRET_CODE)


#get own payment methods
payment_methods = client.GetMyPaymentMethods()

#checkout
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

#get payment info by id
payment = client.GetPayment(1232)

```


## Advanced usage

```python

#calculate checksum for a request (eg, postback).
checksum = client.calc_checksum('https://www.mywebshop.com/postback', 'POST', request.raw_body)
assert checksum == requset.headers['Checksum']


#make an API call for an endpoint that doesnt have a helper in this lib
#note that timestamp is auto added if it's not present
values = {
    #request data
}
order = client.call_api('POST', 'payment/vaultcheckout', values)
```