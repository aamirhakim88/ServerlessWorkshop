import boto3, json
from pprint import pprint

methodResponses = {
    "method.response.header.Access-Control-Allow-Origin": False,
    "method.response.header.Access-Control-Allow-Methods": False,
    "method.response.header.Access-Control-Allow-Headers": False,
}

cloudFormationClient = boto3.client('cloudformation', region_name='ap-south-1')
stsClient = boto3.client('sts', region_name='ap-south-1')
apigwClient = boto3.client('apigateway', region_name='ap-south-1')

stackResponse = cloudFormationClient.describe_stacks(
    StackName = "workshop-2018-deployment-" + stsClient.get_caller_identity()["Account"]
)

for output in stackResponse['Stacks'][0]['Outputs']:
    if output["OutputKey"] == "APIGWId":
        apigwId = output["OutputValue"]
        break

apigatewayResponse = apigwClient.get_resources(
    restApiId = apigwId
)

for item in apigatewayResponse['items']:
    if item['path'] == "/symbol":
        try:
            methodResponse = apigwClient.put_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = methodResponses
            )
        except apigwClient.exceptions.ConflictException as e:
            methodResponse = apigwClient.delete_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200'
            )
            methodResponse = apigwClient.put_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = methodResponses
            )
        except Exception as e:
            pprint(e.message)

        try:
            integrationResponse = apigwClient.put_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = {
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'GET,OPTIONS'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                }
            )
        except apigwClient.exceptions.ConflictException as e:
            integrationResponse = apigwClient.delete_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
            )
            integrationResponse = apigwClient.put_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = {
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'GET,OPTIONS'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                }
            )
        except Exception as e:
            pprint(e.message)

    if item['path'] == "/symbols":
        try:
            methodResponse = apigwClient.put_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = methodResponses
            )
        except apigwClient.exceptions.ConflictException as e:
            methodResponse = apigwClient.delete_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
            )
            methodResponse = apigwClient.put_method_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = methodResponses
            )
        except Exception as e:
            pprint(e.message)

        try:
            integrationResponse = apigwClient.put_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = {
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'POST,OPTIONS'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                }
            )
        except apigwClient.exceptions.ConflictException as e:
            integrationResponse = apigwClient.delete_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
            )
            integrationResponse = apigwClient.put_integration_response(
                restApiId = apigwId,
                resourceId = item['id'],
                httpMethod = "OPTIONS",
                statusCode = '200',
                responseParameters = {
                    "method.response.header.Access-Control-Allow-Origin": "'*'",
                    "method.response.header.Access-Control-Allow-Methods": "'POST,OPTIONS'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                }
            )
        except Exception as e:
            pprint(e.message)

try:
    deploymentResponse = apigwClient.create_deployment(
        restApiId = apigwId,
        stageName = "Prod"
    )
except Exception as e:
    pprint(e.message)
