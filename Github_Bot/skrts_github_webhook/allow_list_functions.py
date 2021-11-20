
import json
import boto3
from modifyTables import allowlist_modifyTables

def delete_repo(org_id, repo_id, dynamodb):

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

def setup_repo(org_id, repo_id, dynamodb):

    #Tries to create org table if it doesn't exist
    try:
        allowlist_modifyTables.create_organization_table(org_id, dynamodb=dynamodb)
        tablename = f"allowlist_organization_{org_id}"
        table = dynamodb.Table(tablename)
        print("waiting for table {}".format(tablename))
        table.meta.client.get_waiter('table_exists').wait(TableName=tablename)
        print("finished ")
    except Exception as e:
        if "Table already exists" in str(e):
            pass
        else:
            raise(e)

    #Tries to create repo table
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

def delete_org(org_id, dynamodb):

        try:
            print("Attempting to delete {}".format(org_id))
            allowlist_modifyTables.delete_table(org_id, dynamodb=dynamodb)
            return {
                'statusCode': 200,
                'description': "OK"
            }
        except Exception as e:
            print(e)
            if str(e) == "ValueError: Org has not been initialized":
                return {
                    'statusCode': 401,
                    'description': "Given org not initialized"
                }
            else:
                return {
                    'statusCode': 404,
                    'description': "An unexpected error occurred"
            }

    