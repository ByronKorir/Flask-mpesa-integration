from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/initiate-payment', methods=['POST'])
def initiate_payment():
    # Replace these values with your actual M-Pesa API credentials
    consumer_key = 'QbquxDyuI4sAyA0C2dAgcZUJr1yqFAuEAXsjmDG93iJQTGhK'
    consumer_secret = 'kH55gj4yfB4stEBBSWM0YtmpASChf5FyLaEE1zMsQ7ZGfeG7HjIyEKKJ6Hyf5bUM'
    shortcode = "174379"
    passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'

    access_token = get_access_token(consumer_key, consumer_secret)
    if not access_token:
        return jsonify({'error': 'Failed to obtain access token'}), 500

    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_token)
    }

    payload = {
        "BusinessShortCode": shortcode,
        "Password": generate_password(shortcode, passkey),
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": request.json['amount'],
        "PartyA": request.json['phone_number'],
        "PartyB": shortcode,
        "PhoneNumber": request.json['phone_number'],
        "CallBackURL": "https://3e83-196-216-90-74.ngrok-free.app/callback",
        "AccountReference": "Night house",
        "TransactionDesc": "Payment of Booking a house"
    }

    response = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', json=payload, headers=headers)

    if response.status_code == 200:
        # Parsing the response data and returning it as JSON
        response_data = response.json()
        return jsonify({
            'message': 'Payment initiated successfully',
            'mpesa_response': response_data
        }), 200
    else:
        return jsonify({'error': 'Failed to initiate payment'}), response.status_code


def get_access_token(consumer_key, consumer_secret):
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=(consumer_key, consumer_secret))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        return None

def generate_password(shortcode, passkey):
    import base64
    import hashlib
    import datetime

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data = shortcode + passkey + timestamp
    encoded_data = base64.b64encode(data.encode('utf-8'))

    return encoded_data.decode('utf-8')

def generate_timestamp():
    import datetime
    return datetime.datetime.now().strftime('%Y%m%d%H%M%S')

@app.route('/callback', methods=['POST'])
def payment_callback():
    data = request.get_json()
    print(data)

    return 'ok'



if __name__ == '__main__':
    app.run(debug=True)
