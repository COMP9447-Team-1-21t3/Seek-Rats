
import boto3
import json
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

# /allowlist/add_term/{org_id}/{repo_id}:
def add_term(event, context):
    # org_id, repo_id, new_terms
    # TODO
    org_id = event['pathParameters']['org_id']
    repo_id = event['pathParameters']['repo_id']
    query_params = event["queryStringParameters"]
    new_term = None

    try:
        new_term = query_params["term"]
    except KeyError:
        return {
            'statusCode': 409,
            'description': "Bad Key"
        }

    try:
        allowlist_modifyTables.insert_new_term(org_id, repo_id, new_term, dynamodb=dynamodb)
        return {
            'statusCode': 200,
            'description': "OK"
        }
    except Exception as e:
        if str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Cannot do operations on a non-existent table":
            return {
                'statusCode': 400,
                'description': "The organization id was not valid"
            }
        elif str(e)=="ValueError: Repo has not been initialized":
            return {
                'statusCode': 401,
                'description': "The repo id was not correct"
            }
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Requested resource not found":
            return {
                'statusCode': 410,
                'description': "An unknown error occurred on DynamoDB. Please try again later"
            }
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }
