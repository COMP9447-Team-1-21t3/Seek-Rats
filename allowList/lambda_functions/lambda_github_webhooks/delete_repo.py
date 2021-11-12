
import json
import boto3
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    org_id = event['org_id']
    repo_id = event['repo_id']
    try:
        allowlist_modifyTables.delete_repo(org_id, repo_id, dynamodb=dynamodb)
        return {
            'statusCode': 200,
            'description': "OK"
        }
    except Exception as e:
        if str(e) == "ValueError: Repo has not been initialized":
            return {
                'statusCode': 401,
                'description': "Given repo not initialized"
            }
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }
