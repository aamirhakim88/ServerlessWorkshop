import json, requests, datetime, boto3, time
from multiprocessing.dummy import Pool as ThreadPool 
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()


TICKER_URL = "http://ticker-api-322193039.ap-south-1.elb.amazonaws.com/ticker/{}"
dynamo = None
price_history = None

def lambda_handler(event, context):
    symbol = event.get('symbol', None)
    if symbol == 'warm':
        time.sleep(10)

    xray_recorder.begin_subsegment('compute-duration')
    is_good_buy = get_buying_advice(symbol)
    xray_recorder.end_subsegment()
    store_symbol_details(symbol, is_good_buy)

def store_symbol_details(symbol, is_good_buy):
    global dynamo
    xray_recorder.begin_subsegment('dynamo-call')
    if dynamo == None:
        dynamo = boto3.client('dynamodb')
    xray_recorder.end_subsegment()

    dynamo.put_item(
        TableName='ChaosTrader',
        Item={
            'symbol': { 'S': symbol },
            'is_good_buy': { 'BOOL': is_good_buy}
            }
        )
def calc_counters(start_price_info):
    good_purchase_counter = 0
    bad_purchase_counter = 0
    for end_price_info in price_history:
        if start_price_info['date'] > end_price_info['date']:
            price_delta = start_price_info['price'] - end_price_info['price']
            if price_delta > 0:
                good_purchase_counter += 1
            else:
                bad_purchase_counter += 1
    return good_purchase_counter-bad_purchase_counter
def listsum(numList):
    theSum = 0
    for i in numList:
        theSum = theSum + i
    return theSum
def get_buying_advice(symbol):
    global price_history
    pool = ThreadPool(2)
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
    goodList = pool.map(calc_counters, price_history)
    return True if listsum(goodList)>0 else False