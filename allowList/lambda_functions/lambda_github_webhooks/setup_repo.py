
import json
import boto3
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    org_id = event['org_id']
    repo_id = event['repo_id']

    try:
        if allowlist_modifyTables.setup_new_repo(org_id, repo_id, dynamodb=dynamodb):
            return {
                'statusCode': 200,
                'description': "OK"
            }
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }

    except Exception as e:
        if str(e)=="Repo with given ID already initialized":
            return {
                'statusCode': 401,
                'description': "Repo with given ID already initialized"
            }
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }