import boto3
import string
import random

# List tables fetched from dynamo_db
def list_table_names(dynamodb):
	t_list = list(
		dynamodb.tables.filter(
    		ExclusiveStartTableName='organization_'
		)
	)
	return [x.name for x in t_list]

def gen_random_strings(n):
    toReturn = []
    for _ in range(n):
        toReturn.append(  ''.join(random.choice(string.ascii_letters) for i in range(15)) )
    return toReturn