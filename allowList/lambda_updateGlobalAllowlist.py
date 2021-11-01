# lambda function
# recieves thing from bot/website, update table
import boto3

def update_table(repo_id, new_terms, dynamodb=None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
	pass