import boto3


def list_table_names(dynamodb=None):
	"""List allowlist tables fetched from dynamo_db

	Args:
		dynamodb ([type], optional): [description]. Defaults to None.

	Returns:
		[type]: [description]
	"""
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	t_list = list(
		dynamodb.tables.filter(
    		ExclusiveStartTableName='allowList_repo_',
			Limit = 100
		)
	)
	return [x.name for x in t_list]

def validateID(function):
	"""[summary]

	Args:
		function ([type]): [description]
	"""

	def functionWrapper(repo_id, *args, **kwargs):
		if not repo_id :
			raise ValueError("repo_id cannot be None")
		tableName = f'allowList_repo_{repo_id}'
		if tableName not in list_table_names():
			raise ValueError(f"Repo with given ID does not exist")
		return function(str(repo_id), *args, **kwargs)

	return functionWrapper

