
import boto3
import json
import os
from modifyTables import allowlist_modifyTables

dynamodb = boto3.resource('dynamodb')

# /allowlist/get_list/{org_id}/{repo_id}:
def get_list(event, context):
    org_id = event['pathParameters']['org_id']
    repo_id = event['pathParameters']['repo_id']
    query_params = event["queryStringParameters"]

    try: 
        list_of_terms = None
        if "with_info" in query_params.keys():
            if query_params["with_info"]:
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
                'description': "The organization id was not found"
            }
        elif str(e)=="ValueError: Repo has not been initialized":
            return {
                'statusCode': 401,
                'description': "The repo id was not correct"
            }
        else:
            return {
                'statusCode': 409,
                'description': "Bad Key"
            }


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
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }


# /allowlist/add_terms/{org_id}/{repo_id}:
def add_terms(event, context):
    # org_id, repo_id, new_terms
    org_id = event['pathParameters']['org_id']
    repo_id = event['pathParameters']['repo_id']
    query_params = event["queryStringParameters"]

    try:
        new_terms = query_params["terms"]
    except KeyError:
        return {
            'statusCode': 409,
            'description': "Bad Key"
        }

    try:
        allowlist_modifyTables.insert_new_terms(org_id, repo_id, new_terms, dynamodb=dynamodb)
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
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Cannot do operations on a non-existent table":
            return {
                'statusCode': 400,
                'description': "The organization id was not valid"
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


# /allowlist/add_terms_with_info/{org_id}/{repo_id}:
def add_terms_with_info(event, context):
    # org_id, repo_id, new_terms
    # TODO
    org_id = event['pathParameters']['org_id']
    repo_id = event['pathParameters']['repo_id']
    query_params = event["queryStringParameters"]

    try:
        new_terms = query_params["terms"]
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
        elif str(e)=="An error occurred (ResourceNotFoundException) when calling the Query operation: Cannot do operations on a non-existent table":
            return {
                'statusCode': 400,
                'description': "The organization id was not valid"
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


# /allowlist/remove_term/{org_id}/{repo_id}:
def remove_term(event, context):
    #TODO
    org_id = event['pathParameters']['org_id']
    repo_id = event['pathParameters']['repo_id']
    query_params = event["queryStringParameters"]

    try:
        term = query_params["terms"]
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
        else:
            return {
                'statusCode': 404,
                'description': "An unexpected error occurred"
            }
