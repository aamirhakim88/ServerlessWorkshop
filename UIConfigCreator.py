import boto3, json

s3Client = boto3.client('s3', region_name='ap-south-1')
cloudformationClient = boto3.client('cloudformation', region_name='ap-south-1')
accountId = boto3.client('sts', region_name='ap-south-1').get_caller_identity().get('Account')
config = {
    'region': 'ap-south-1',
    'defaultContentType': 'application/json',
    'defaultAcceptType': 'application/json'
}

stackResponse = cloudformationClient.describe_stacks(
    StackName = "workshop-2018-deployment-" + accountId
)

for output in stackResponse['Stacks'][0]['Outputs']:
    if output["OutputKey"] == "APIEndpoint":
        config['invokeUrl'] = output["OutputValue"]
        break

s3Response = s3Client.put_object(
    Body=json.dumps(config),
    Bucket="chaostraderwebsitebucket"+accountId,
    Key="uiconfig.json",
    ACL='public-read'
)
