import hashlib

import boto3
import json

from insights.models import RedditDataCache, WebsiteAnalysisCache

lambda_client = boto3.client('lambda', region_name='us-east-1')


def dict_to_hash(d: dict) -> str:
    # Sort keys for consistent hash regardless of input order
    json_string = json.dumps(d, sort_keys=True)
    return hashlib.sha256(json_string.encode('utf-8')).hexdigest()


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
    try:
        cache_entry = WebsiteAnalysisCache.objects.get(url=url)
        if not cache_entry.is_expired():
            return cache_entry.result
    except WebsiteAnalysisCache.DoesNotExist:
        pass

    try:
        result = invoke_lambda("product-parser-lambda", {"url": url})
        WebsiteAnalysisCache.objects.update_or_create(
            url=url,
            defaults={"result": result}
        )
        return result
    except Exception as e:
        return {"error": f"Failed to invoke product-parser-lambda: {str(e)}"}


def fetch_reddit_data(query: dict) -> dict:
    query_hash = dict_to_hash(query)

    try:
        cache_entry = RedditDataCache.objects.get(query_hash=query_hash)
        if not cache_entry.is_expired():
            return cache_entry.result

    except RedditDataCache.DoesNotExist:
        pass

    try:
        reddit_output = invoke_lambda("subreddits-gather-lambda", query)

        RedditDataCache.objects.update_or_create(
            query=query,
            defaults={"result": reddit_output}
        )
        return reddit_output
    except Exception as e:
        return {"error": f"Failed to invoke Reddit lambdas: {str(e)}"}
