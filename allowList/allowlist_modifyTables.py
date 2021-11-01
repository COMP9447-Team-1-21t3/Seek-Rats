# Functions for the creation, deletion and modification of tables. Includes functions to get related table names and fetch data from tables.
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from datetime import datetime
from allowlist_modifyTables_helpers import validateID, list_table_names

@validateID
def create_organization_table(org_id, dynamodb=None):
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
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb

	table_name = f'organization_{org_id}'
	
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
def read_repo(org_id, repo_id, dynamodb=None):
	# TODO
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'
	repo_id = f'repo_{repo_id}'
	to_return = []
	query_params = {
		'KeyConditionExpression':  Key('repo_id').eq(repo_id), 
		'ProjectionExpression': "whitelist_term",
		'ConsistentRead': True
	}

	table = dynamodb.Table(table_name)
	response = table.query( **query_params)
	for item in response['Items']:
		to_return.append(item['whitelist_term'])

	try:
		while response['LastEvaluatedKey']:
			# When you run a query, the last evaluated key is saved. We use that to find the next item we need to start with for searching
			response = table.query(
				**query_params,
				ExclusiveStartKey = response['LastEvaluatedKey']
			)
			for item in response['Items']:
				to_return.append(item['whitelist_term'])
			
	except KeyError as e:
		# There is a possability the first pass won't leave any terms left - this is to catch that exclusive case
		pass

	return to_return


@validateID
def insert_new_term(org_id, repo_id, new_term, dynamodb=None):
	"""
	Inserts a new whitelist term into a given organization and repo

	Args:
		org_id (int/str): id of the organization to add term to
		repo_id (int/str): id of repo to add term to
		new_term (str): new term to add to the whitelist
		dynamodb (dynamodb service resource, optional): DynamoDB Connenction. Defaults to None, which will uses the localhost:8000 instead of a cloud server

	Returns:
		Response : Response from insert function
	"""
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'
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
def insert_new_terms(org_id, repo_id, new_terms, dynamodb=None):
	# TODO
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'
	repo_id = f'repo_{repo_id}'

	table = dynamodb.Table(table_name)

	with table.batch_writer() as batch:
		for term in new_terms:
			current_utc = str(datetime.utcnow())
			content = {
				'repo_id': repo_id,
				'whitelist_term': term,
				'time_added': current_utc
			}
			batch.put_item(Item = content)


@validateID
def delete_term(org_id, repo_id, term, dynamodb=None):
	# TODO
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'
	repo_id = f'repo_{repo_id}'

	try:
		table = dynamodb.Table(table_name)
		response = table.delete_item(
			Key = {
				'repo_id' : repo_id,
				'whitelist_term' : term
			}
		)
	except ClientError as e:
		# TODO
		raise ValueError("There was a bad paramater")
	else:
		return response

@validateID
def delete_repo(org_id, repo_id, dynamodb=None):
	# TODO
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'
	repo_id = f'repo_{repo_id}'
	deleted_items = 0
	query_params = {
		'KeyConditionExpression':  Key('repo_id').eq(repo_id), 
		'ProjectionExpression': "whitelist_term",
		'ConsistentRead': True
	}

	table = dynamodb.Table(table_name)
	response = table.query( **query_params)
	deleted_items += len(response['Items'])
	with table.batch_writer() as batch:
			for item in response['Items']:
				content = {
					'repo_id': repo_id,
					'whitelist_term': item['whitelist_term']
				}
				batch.delete_item(Key = content)
	
	try:
		while response['LastEvaluatedKey']:
			# When you run a query, the last evaluated key is saved. We use that to find the next item we need to start with for deleting
			response = table.query(
				**query_params,
				ExclusiveStartKey = response['LastEvaluatedKey']
			)
			deleted_items += len(response['Items'])
			with table.batch_writer() as batch:
				for item in response['Items']:
					content = {
						'repo_id': repo_id,
						'whitelist_term': item['whitelist_term']
					}
					batch.delete_item(Key = content)
	except KeyError as e:
		# There is a possability the first pass won't leave any terms left - this is to catch that exclusive case
		pass

	return deleted_items

@validateID
def delete_table(org_id, dynamodb=None):
	""" Deletes an organization table. 
		NOTE: THIS IS AN IRREVERSABLE PROCESS. DON'T DO THIS WITHOUT A GOOD PLAN

	Args:
		org_id ([type]): [description]
		dynamodb ([type], optional): [description]. Defaults to None.
	"""
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'organization_{org_id}'

	table = dynamodb.Table(table_name)
	table.delete

