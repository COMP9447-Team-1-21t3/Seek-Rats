# lambda function
import boto3

def fetch_tableContents(repo_id, fromTime = None, dynamodb = None):
	if not dynamodb:
		dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
	pass