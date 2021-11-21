import pytest
import os
from moto import mock_dynamodb2
import boto3

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"


@pytest.fixture
def db_resource(aws_credentials):
    with mock_dynamodb2():
        dynamodb = boto3.resource('dynamodb', region_name="ap-southeast-2")
        yield dynamodb
