
import boto3
import json
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')


# /allowlist/add_terms_with_info/{org_id}/{repo_id}:
def lambda_handler(event, context):
    # org_id, repo_id, new_terms
    # TODO
    org_id = event['org_id']
    repo_id = event['repo_id']
    new_terms = None

    try:
        new_terms = event["terms"]
    except KeyError:
        return {
            'statusCode': 409,
            'description': "Bad Key"
        }

    try:
        allowlist_modifyTables.insert_new_terms_with_info(org_id, repo_id, new_terms, dynamodb=dynamodb)
        return {
            'statusCode': 200,
            'description': "OK"
        }
    except Exception as e:
        if str(e)=="An error occurred (ValidationException) when calling the BatchWriteItem operation: Provided list of item keys contains duplicates":
            return {
                'statusCode': 403,
                'description': "Provided list of item keys contains duplicates"
            }
        elif str(e)=="ValueError: new_terms must be a list of dicts with the keys 'term' and 'info'":
            return {
                'statusCode': 403,
                'description': "Provided list must be a list of dicts with the keys 'term' and 'info'"
            }
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Cannot do operations on a non-existent table":
            return {
                'statusCode': 400,
                'description': "The organization id was not valid"
            }
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Requested resource not found":
            return {
                'statusCode': 410,
                'description': "An unknown error occurred on DynamoDB. Please try again later"
            }
        elif str(e)=="ValueError: Repo has not been initialized":
            return {
                'statusCode': 401,
                'description': "The repo id was not correct"
            }
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }
