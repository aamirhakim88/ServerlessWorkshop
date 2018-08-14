# Before Synthetic Events

import boto3, json
from multiprocessing.dummy import Pool as ThreadPool 

lambda_client = boto3.client('lambda')

def get_worker_lambda_function():
    cloudFormationClient = boto3.client('cloudformation')
    stsClient = boto3.client('sts')

    stackResponse = cloudFormationClient.describe_stacks(
        StackName = "workshop-2018-deployment-" + stsClient.get_caller_identity()["Account"]
    )

    for output in stackResponse['Stacks'][0]['Outputs']:
        if output["OutputKey"] == "WorkerLambdaARN":
            return output["OutputValue"]


worker_arn = get_worker_lambda_function()
def dummy_event(junk):
    lambda_client.invoke(FunctionName=worker_arn, InvocationType='Event', Payload=json.dumps({'symbol': 'warm'}))


def lambda_handler(event, context):
    pool = ThreadPool(2)
    pool.map(dummy_event, range(500))
    return {
        "isBase64Encoded": False,
        "statusCode": 202
    }
