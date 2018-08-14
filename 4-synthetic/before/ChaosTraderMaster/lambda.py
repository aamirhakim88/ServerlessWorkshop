# Before Synthetic Events

import boto3, json
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all

patch_all()

lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    body = json.loads(event['body']) if event['body'] else {}
    symbols = body.get('symbols', []) if body else []

    worker_arn = get_worker_lambda_function()
    for symbol in symbols:
        lambda_client.invoke(FunctionName=worker_arn, InvocationType='Event', Payload=json.dumps({'symbol': symbol}))
    return {
        "isBase64Encoded": False,
        "statusCode": 202
    }

def get_worker_lambda_function():
    cloudFormationClient = boto3.client('cloudformation')
    stsClient = boto3.client('sts')

    stackResponse = cloudFormationClient.describe_stacks(
        StackName = "workshop-2018-deployment-" + stsClient.get_caller_identity()["Account"]
    )

    for output in stackResponse['Stacks'][0]['Outputs']:
        if output["OutputKey"] == "WorkerLambdaARN":
            return output["OutputValue"]
