# Functions for the creation, deletion and modification of tables
import boto3
from datetime import datetime
from allowlist_modifyTables_helpers import validateID, list_table_names

def list_all_allowlist(dynamodb=None):
	list_table_names(dynamodb)

# should create a new table when a new repo is created with the name id.
def create_table(repo_id, dynamodb=None):
	"""[summary]

	Args:
		repo_id (int): [description]
		dynamodb ([type], optional): [description]. Defaults to None, which will uses the localhost:8000 instead of a given repo

	Raises:
		ValueError: if the repo_id is None, or a repo already exists for the given ID

	Returns:
		True: If a new table is successfully created the function will return true
	"""
	if not repo_id :
			raise ValueError("repo_id cannot be None")
	table_name = f'allowList_repo_{str(repo_id)}'
	if table_name in list_table_names():
		raise ValueError(f"Repo with given ID already has a table: 'allowList_repo_{repo_id}'")
	
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	
	dynamodb.create_table(
		TableName=table_name,
		KeySchema=[
			{
				'AttributeName': 'whitelist_term',
				'KeyType': 'HASH' # Partition key
			}, 
			{
				'AttributeName': 'time_added',
				'KeyType': 'RANGE'  # Sort key
			}
		],
		AttributeDefinitions=[
			{
				'AttributeName': 'whitelist_term',
				'AttributeType': 'S' # string
			},
			{
				'AttributeName': 'time_added',
				'AttributeType': 'S' #string [utc time]
			}
		],
		ProvisionedThroughput={
			'ReadCapacityUnits': 5,
			'WriteCapacityUnits': 5
		}
	)
	return True

@validateID
def insert_new_term(repo_id, new_term, dynamodb=None):

	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	table_name = f'allowList_repo_{str(repo_id)}'
	current_utc = str(datetime.datetime.utcnow())
	table = dynamodb.Table(table_name)
	response = table.put_item(
		Item = {
			'whitelist_term': new_term,
			'time_added': current_utc
		}
	)
	return response

# should delete an allowlist table when a repo gets deleted.
@validateID
def delete_table(repo_id, dynamodb=None):
	
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	
	pass
	# TODO aaaaaa

if __name__ == '__main__':
	create_table(123)