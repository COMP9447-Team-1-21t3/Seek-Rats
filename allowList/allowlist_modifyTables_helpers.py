import boto3

# List tables fetched from dynamo_db
def list_table_names(dynamodb=None):
	
	dynamodb = boto3.resource('dynamodb', endpoint_url="http://localhost:8000") if not dynamodb else dynamodb
	t_list = list(
		dynamodb.tables.filter(
    		ExclusiveStartTableName='organization_',
			Limit = 100
		)
	)
	return [x.name for x in t_list]

def validateID(function):
	def functionWrapper(org_id, *args, **kwargs):
		if not org_id :
			raise ValueError("org_id cannot be None")
		return function(org_id, *args, **kwargs)
	return functionWrapper

