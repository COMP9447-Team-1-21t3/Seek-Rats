import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

global url
url = "http://localhost:8000"


# This function deletes a table specified by name
def delete_table(table_name, dynamodb=None):
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    try:
        table = dynamodb.Table(table_name)
        table.delete()
    except Exception as e:
        print(str(e))
        return False
    else:
        print(f'{table_name} table successfully deleted')
        return True


# This table creates the tracking table
def create_tracking_table(dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'reportURL',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'reviewerID',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'reportURL',
                    'AttributeType': 'S'  # string
                },
                {
                    'AttributeName': 'reviewerID',
                    'AttributeType': 'S'  # string
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except Exception as e:
        print(str(e))
        return False
    else:
        print("Tracking table successfully created")
        return True


# This function inserts a row into the tracking table
def insert_tracking(reportURL, reviewerID, SHA, status=False, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    item = {
        'reportURL': reportURL,
        'reviewerID': reviewerID,
        'SHA': SHA,
        'tracking_status': status
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
    except Exception as e:
        print(str(e))
        return False
    else:
        return True


# This function updates the tracking status of a single record associated with a given reportURL and a reviewerID
def update_tracking_status(reportURL, reviewerID, new_status, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)

    try:
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={
                'reportURL': reportURL,
                'reviewerID': reviewerID
            },
            UpdateExpression="set tracking_status=:s",
            ExpressionAttributeValues={
                ':s': new_status,
            },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print(str(e))
        return False
    else:
        print(f'successfully updated {response["Attributes"]}')
        return True


# This function updates all record's SHA value associated with a given reportURL
def update_SHA(reportURL, new_SHA, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)

    try:
        table = dynamodb.Table(table_name)
        # Query all records that has the given reportURL
        records = read_tracking_report(reportURL, dynamodb)
        # Update each record's SHA value
        for record in records:
            response = table.update_item(
                Key={
                    'reportURL': reportURL,
                    'reviewerID': record['reviewerID']
                },
                UpdateExpression="set SHA=:s",
                ExpressionAttributeValues={
                    ':s': new_SHA,
                },
                ReturnValues="UPDATED_NEW"
            )
            print(f'successfully updated {response["Attributes"]}')
    except Exception as e:
        print(str(e))
        return False
    else:
        return True


# This function deletes all records in the tracking table associated with a given reportURL
def delete_tracking_record(reportURL, dynamodb=None):
    deleted_items = 0
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    query_params = {
        'KeyConditionExpression': Key('reportURL').eq(reportURL),
        'ConsistentRead': True
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.query(**query_params)
        deleted_items += len(response['Items'])

        with table.batch_writer() as batch:
            for item in response['Items']:
                content = {
                    'reportURL': reportURL,
                    'reviewerID': item['reviewerID']
                }
                batch.delete_item(Key=content)

    except Exception as e:
        print(str(e))
        return False
    else:
        print(f'successfully deleted {deleted_items} records')
        return True


# This function deletes a tracking record associated with a given reportURL and a reviewerID
def delete_tracking(reportURL, reviewerID, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    key={
        'reportURL': reportURL,
        'reviewerID': reviewerID
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.delete_item(Key=key)
    except Exception as e:
        print(str(e))
        return False
    else:
        return True


# Get all existing tracking records with the same reportURL
def read_tracking_report(reportURL, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)

    to_return = []
    query_params = {
        'KeyConditionExpression': Key('reportURL').eq(reportURL),
        'ConsistentRead': True
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.query(**query_params)
        for item in response['Items']:
            to_return.append(item)

        # In case the tracking table has more than 100 records
        while response ['LastEvaluatedKey']:
            response = table.query(
                **query_params,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            # append any additional records 100 by 100
            for item in response['Items']:
                to_return.append(item['Items'])
    except KeyError:
        # response ['LastEvaluatedKey'] will not exist if there is no record leftover after the first run
        return to_return
    except Exception as e:
        print(str(e))
        return False
    else:
        return to_return


# This function fetches the status of tracking given a specific reportURL and a reviewerID
def read_tracking_reviewer_status(reportURL, reviewerID, dynamodb=None):
    table_name = "tracking"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    try:
        table = dynamodb.Table(table_name)
        key = {
            'reportURL': reportURL,
            'reviewerID': reviewerID
        }
        response = table.get_item(Key=key)
    except Exception as e:
        print(str(e))
        return False
    else:
        return response['Item']


# This function creates a secret table
def create_secret_table(dynamodb=None):
    table_name = "secret"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'reportURL',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'secretNum',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'reportURL',
                    'AttributeType': 'S'  # string
                },
                {
                    'AttributeName': 'secretNum',
                    'AttributeType': 'S'  # string
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
    except Exception as e:
        print(str(e))
        return False
    else:
        print("Secret table successfully created")
        return True


# This function inserts a record in the secret table
def insert_secret(reportURL, secretNum, secret, secret_info, status, dynamodb=None):
    table_name = "secret"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    item = {
        'reportURL': reportURL,
        'secretNum': secretNum,
        'secret': secret,
        'secret_info': secret_info,
        'secret_status': status
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.put_item(Item=item)
    except Exception as e:
        print(str(e))
        return False
    else:
        return True


# This function updates the secret status of a record associated with a given reportURL and a secretNum
def update_secret_status(reportURL, secretNum, new_status, dynamodb=None):
    table_name = "secret"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)

    try:
        table = dynamodb.Table(table_name)
        response = table.update_item(
            Key={
                'reportURL': reportURL,
                'secretNum': secretNum
            },
            UpdateExpression="set secret_status=:s",
            ExpressionAttributeValues={
                ':s': new_status,
            },
            ReturnValues="UPDATED_NEW"
        )
    except Exception as e:
        print(str(e))
        return False
    else:
        print(f'successfully updated {response["Attributes"]}')
        return True


# This function reads all secrets that are associated with a given reportURL
def read_secret(reportURL, dynamodb=None):
    table_name = "secret"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)

    to_return = []
    query_params = {
        'KeyConditionExpression': Key('reportURL').eq(reportURL),
        'ConsistentRead': True
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.query(**query_params)
        for item in response['Items']:
            to_return.append(item)

        # In case the tracking table has more than 100 records
        while response['LastEvaluatedKey']:
            response = table.query(
                **query_params,
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            # append any additional records 100 by 100
            for item in response['Items']:
                to_return.append(item['Items'])
    except KeyError:
        # response ['LastEvaluatedKey'] will not exist if there is no record leftover after the first run
        return to_return
    except Exception as e:
        print(str(e))
        return False
    else:
        return to_return


# This function deletes all records in the secret table associated with a given reportURL
def delete_secret_record(reportURL, dynamodb=None):
    deleted_items = 0
    table_name = "secret"
    if not dynamodb: dynamodb = boto3.resource('dynamodb', endpoint_url=url)
    query_params = {
        'KeyConditionExpression': Key('reportURL').eq(reportURL),
        'ConsistentRead': True
    }

    try:
        table = dynamodb.Table(table_name)
        response = table.query(**query_params)
        deleted_items += len(response['Items'])

        with table.batch_writer() as batch:
            for item in response['Items']:
                content = {
                    'reportURL': reportURL,
                    'secretNum': item['secretNum']
                }
                batch.delete_item(Key=content)
    except Exception as e:
        print(str(e))
        return False
    else:
        print(f'successfully deleted {deleted_items} records')
        return True