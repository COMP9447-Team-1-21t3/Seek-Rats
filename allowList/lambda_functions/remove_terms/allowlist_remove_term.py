
import boto3
import json
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

# /allowlist/remove_term/{org_id}/{repo_id}:
def lambda_handler(event, context):
    #TODO
    org_id = event['org_id']
    repo_id = event['repo_id']
    term = None

    try:
        term = event["term"]
    except KeyError:
        return {
            'statusCode': 409,
            'description': "Bad Key"
        }

    try:
        allowlist_modifyTables.delete_term(org_id, repo_id, term, dynamodb=dynamodb)
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
