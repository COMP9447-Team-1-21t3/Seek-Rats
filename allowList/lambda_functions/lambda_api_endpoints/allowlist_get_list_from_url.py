
import boto3
import json
from urllib.parse import urlparse
from generateToken.gitapp_generateToken import get_ids
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    url = event['url']
    with_info = event['with_info']

    parsed_url = urlparse(url)
    path = parsed_url.path
    netloc = parsed_url.netloc

    split_path = path.split("/")
    if (len(split_path) != 3 and len(split_url) != 4) or "github" not in netloc:
        return {
            'statusCode': 402,
            'description': "Invalid URL"
        }
    
    org_name = split_path[1].strip()
    repo_name = split_path[2].strip()
    ids = None

    try:
        ids = get_ids(org_name, repo_name)
    except Exception as e:
        return {
            'statusCode': 402,
            'description': "Invalid URL"
        }

    org_id = ids['org_id']
    repo_id = ids['repo_id']
    
    # NGL, i think this is easier then invoking the other lambda function

    try: 
        list_of_terms = None
        if "with_info" in event.keys():
            if event["with_info"]:
                list_of_terms = allowlist_modifyTables.read_repo_with_info(org_id, repo_id, dynamodb=dynamodb)
        if list_of_terms == None:
            list_of_terms = allowlist_modifyTables.read_repo(org_id, repo_id, dynamodb=dynamodb)
        
        return {
            'statusCode': 200,
            'description': "OK",
            'body': json.dumps(list_of_terms)
        }
    except Exception as e:
        if str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Cannot do operations on a non-existent table":
            return {
                'statusCode': 400,
                'description': "The organization name was not valid"
            }
        elif str(e)=="ValueError: Repo has not been initialized":
            return {
                'statusCode': 401,
                'description': "The repo name was not correct"
            }
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Requested resource not found":
            return {
                'statusCode': 410,
                'description': "An unknown error occurred on DynamoDB. Please try again later"
            }
        else:
            return {
                'statusCode': 409,
                'description': "Bad Key"
            }
