# Functions for the creation, deletion and modification of tables. Includes functions to get related table names and fetch data from tables.
import boto3
from datetime import datetime
from allowlist_modifyTables_helpers import validateID

def create_table(org_id, dynamodb=None):
	"""
	#	Will create an allowlist table on the given dynamodb connection, 'allowList_organization'. It has 2 primary attributes,
	#	'repo_id' (string, hash key) and 'whitelist term' (string, sort key)

	Args:
		org_id (int/str): the name of the org the table is for
		dynamodb (dynamodb service resource, optional): DynamoDB connection. Defaults to None, which will uses the localhost:8000 instead of a given region

	Raises:
		ValueError: if the repo_id is None, or a repo already exists for the given ID

	Returns:
		True: If a new table is successfully created the function will return true
	"""
	if not org_id :
			raise ValueError("org_id cannot be None")
	table_name = f'organization_{org_id}'
	
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	
	dynamodb.create_table(
		TableName=table_name,
		KeySchema=[
			{
				'AttributeName': 'repo_id',
				'KeyType': 'HASH' # Partition key
			}, 
			{
				'AttributeName': 'whitelist_term',
				'KeyType': 'RANGE'  # Sort key
			}
		],
		LocalSecondaryIndexes=[
			{
				'IndexName':"LatestAdditions",
				'KeySchema':[
					{
						'AttributeName': 'repo_id',
						'KeyType': 'HASH' # Partition key
					}, 
					{
						'AttributeName': 'time_added',
						'KeyType': 'RANGE'  # Sort key
					}
				],
				'Projection':{
					'ProjectionType':'ALL'
				}
			}
		],
		AttributeDefinitions=[
			{
				'AttributeName': 'repo_id',
				'AttributeType': 'S' # string
			}, 
			{
				'AttributeName': 'whitelist_term',
				'AttributeType': 'S' # string
			},
			{
				'AttributeName': 'time_added',
				'AttributeType': 'S' # string [UTC]
			}

		],
		ProvisionedThroughput={
			'ReadCapacityUnits': 5,
			'WriteCapacityUnits': 5
		}
	)
	return True

@validateID
def insert_new_term(org_id, repo_id, new_term, dynamodb=None):
	"""Inserts a new whitelist term into a given organization and repo

	Args:
		org_id (int/str): id of the organization to add term to
		repo_id (int/str): id of repo to add term to
		new_term (str): new term to add to the whitelist
		dynamodb (dynamodb service resource, optional): DynamoDB Connenction. Defaults to None, which will uses the localhost:8000 instead of a cloud server

	Returns:
		Response : Response from insert function
	"""
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{str(org_id)}'
	repo_id = f'repo_{repo_id}'
	current_utc = str(datetime.utcnow())
	table = dynamodb.Table(table_name)
	response = table.put_item(
		Item = {
			'repo_id' : repo_id,
			'whitelist_term': new_term,
			'time_added': current_utc
		}
	)
	return response

@validateID
def delete_table(repo_id, dynamodb=None):
	
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	
	pass
	# TODO aaaaaa

