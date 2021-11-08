"""
# Recieve event from github
# Do something based on the event

## On repo create: create new hash
## On repo delete: delete hashes
## On repo rename: do nothing
## On branch: do nothing
"""

import boto3
import json
import os

dynamodb = boto3.resource('dynamodb', region="ap-southeast-2")

# main function
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }