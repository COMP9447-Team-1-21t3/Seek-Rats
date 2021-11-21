import boto3
from moto import mock_dynamodb2
import report_status_tracking as rst


@mock_dynamodb2
def test_tracking_creation_and_insertion():
    expected_data = [{'reportURL': 'report123', 'reviewerID': 'reviewer1', 'SHA': '3ef81ac', 'tracking_status': False},
                     {'reportURL': 'report123', 'reviewerID': 'reviewer2', 'SHA': '3ef81ac', 'tracking_status': True}]

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    rst.create_tracking_table(dynamodb)
    rst.insert_tracking('report123', 'reviewer1', '3ef81ac', status=False, dynamodb=dynamodb)
    rst.insert_tracking('report123', 'reviewer2', '3ef81ac', status=True, dynamodb=dynamodb)
    actual_data = rst.read_tracking_report('report123', dynamodb)
    assert(actual_data == expected_data)


@mock_dynamodb2
def test_secret_creation_and_insertion():
    expected_data = [{'reportURL': 'report123', 'secretNum': '1', 'secret': 'password 1', 'secret_info': 'line 29', 'secret_status': 'allowlist'},
                     {'reportURL': 'report123', 'secretNum': '2', 'secret': 'password 2', 'secret_info': 'line 112', 'secret_status': 'security hub'}]

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    rst.create_secret_table(dynamodb)
    rst.insert_secret('report123', '1', 'password 1', 'line 29', 'allowlist', dynamodb=dynamodb)
    rst.insert_secret('report123', '2', 'password 2', 'line 112', 'security hub', dynamodb=dynamodb)
    actual_data = rst.read_secret('report123', dynamodb)
    assert (actual_data == expected_data)


@mock_dynamodb2
def test_tracking_update_status():
    expected_data = [{'reportURL': 'report123', 'reviewerID': 'reviewer1', 'SHA': '3ef81ac', 'tracking_status': True}]

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    rst.create_tracking_table(dynamodb)
    rst.insert_tracking('report123', 'reviewer1', '3ef81ac', status=False, dynamodb=dynamodb)
    rst.update_tracking_status('report123', 'reviewer1', True, dynamodb=dynamodb)
    actual_data = rst.read_tracking_report('report123', dynamodb)
    assert (actual_data == expected_data)


@mock_dynamodb2
def test_tracking_update_SHA():
    expected_data = [{'reportURL': 'report123', 'reviewerID': 'reviewer1', 'SHA': '3fa21be', 'tracking_status': False}]

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    rst.create_tracking_table(dynamodb)
    rst.insert_tracking('report123', 'reviewer1', '3ef81ac', status=False, dynamodb=dynamodb)
    rst.update_SHA('report123', '3fa21be', dynamodb)
    actual_data = rst.read_tracking_report('report123', dynamodb)
    assert (actual_data == expected_data)


@mock_dynamodb2
def test_secret_update_status():
    expected_data = [{'reportURL': 'report123', 'secretNum': '1', 'secret': 'password 1', 'secret_info': 'line 29', 'secret_status': 'security hub'}]

    dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
    rst.create_secret_table(dynamodb)
    rst.insert_secret('report123', '1', 'password 1', 'line 29', 'allowlist', dynamodb=dynamodb)
    rst.update_secret_status('report123', '1', 'security hub', dynamodb)
    actual_data = rst.read_secret('report123', dynamodb)
    assert (actual_data == expected_data)


test_tracking_creation_and_insertion()
test_secret_creation_and_insertion()
test_tracking_update_status()
test_tracking_update_SHA()
test_secret_update_status()
