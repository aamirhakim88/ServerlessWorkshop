# After Synthetic Events

import boto3, json

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

def lambda_handler(event, context):
    symbol = event.get('queryStringParameters', {}).get('symbol', None)

    xray_recorder.begin_subsegment('dynamo-call')
    dynamo = boto3.client('dynamodb')
    _item = dynamo.get_item(TableName='ChaosTrader', Key={'symbol': {'S': symbol}})
    xray_recorder.end_subsegment()

    item = _item.get('Item')
    if item:
        is_good_buy = _item.get('Item', {}).get('is_good_buy', {}).get('BOOL', None)
        return {
            "isBase64Encoded": False,
            "statusCode": 200,
            "body": json.dumps({"is_good_buy": is_good_buy}),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
    else:
        return {
            "isBase64Encoded": False,
            "statusCode": 404,
            "body": json.dumps({}),
            "headers": {
                "Access-Control-Allow-Origin": "*"
            }
        }
