# After Dependency Management

import json, requests, datetime, boto3, time
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

dynamo = boto3.client('dynamodb')

TICKER_URL = "http://ticker-api-322193039.ap-south-1.elb.amazonaws.com/ticker/{}"

def lambda_handler(event, context):
    symbol = event.get('symbol', None)
    if symbol == 'warm':
        time.sleep(10)
        return

    is_good_buy = get_buying_advice(symbol)
    store_symbol_details(symbol, is_good_buy)

def store_symbol_details(symbol, is_good_buy):
    dynamo.put_item(
        TableName='ChaosTrader',
        Item={
            'symbol': { 'S': symbol },
            'is_good_buy': { 'BOOL': is_good_buy}
            }
        )

def get_buying_advice(symbol):
    url = TICKER_URL.format(symbol)
    response = requests.get(url)
    body = response.json()
    _price_history = body.get('Item', {}).get('data', [])
    price_history = []
    good_purchase_counter = 0
    bad_purchase_counter = 0
    for price_data in _price_history:
        sdate, price = price_data
        date = datetime.datetime.strptime(sdate, '%Y-%m-%d')
        price_history.append({'date': date, 'price': price})
    for start_price_info in price_history:
        for end_price_info in price_history:
            if start_price_info['date'] > end_price_info['date']:
                price_delta = start_price_info['price'] - end_price_info['price']
                if price_delta > 0:
                    good_purchase_counter += 1
                else:
                    bad_purchase_counter += 1
    print("Good Buy Counter = {}, Bad Buy Counter = {}".format(good_purchase_counter, bad_purchase_counter))
    return True if good_purchase_counter > bad_purchase_counter else False