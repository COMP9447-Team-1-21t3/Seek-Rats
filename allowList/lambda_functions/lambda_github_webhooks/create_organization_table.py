
import json
import boto3
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    org_id = event['org_id']
    try:
        allowlist_modifyTables.create_organization_table(org_id, dynamodb=dynamodb)
        return {
            'statusCode': 200,
            'description': "OK"
        }
    except Exception as e:
        if "Table already exists" in str(e):
            return {
                'statusCode': 400,
                'description': "A table already exists for this organization"
            }
        else :
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }