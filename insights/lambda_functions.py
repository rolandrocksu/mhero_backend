import boto3
import json

lambda_client = boto3.client('lambda', region_name='us-east-1')


def invoke_lambda(function_name, input_dict):
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(input_dict).encode('utf-8')
    )
    response_payload = response['Payload'].read().decode('utf-8')
    output = json.loads(response_payload)
    return output


def analyze_website(url: str) -> dict:
    # Call "product-parser-lambda" with {"url": url}
    input_payload = {"url": url}
    lambda_output = invoke_lambda("product-parser-lambda", input_payload)

    return lambda_output


def fetch_reddit_data(query: dict) -> dict:
    reddit_lambda_output = invoke_lambda("subreddits-gather-lambda", query)
    return reddit_lambda_output
