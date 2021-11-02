import boto3
import base64
from botocore.exceptions import ClientError
import json
import os
import sys

# definition of global variables
region_name = "ap-southeast-2"
current = "AWSCURRENT"
pending = "AWSPENDING"
path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')

# setting up logger
scriptname = os.path.splitext(os.path.basename(__file__))[0]
from logger import clsLogging
loginstance = clsLogging(path, scriptname)
logger = loginstance.setup()


# This function gets a particular secret(in key-value format) by its ARN
def get_secret(client, secret_arn, stage, token=None):
    try:
        # Only do VersionId validation against the stage if a token is passed in
        if token:
            get_secret_value_response = client.get_secret_value(SecretId=secret_arn, VersionId=token, VersionStage=stage)
        else:
            get_secret_value_response = client.get_secret_value(SecretId=secret_arn, VersionStage=stage)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            raise e
    else:
        # find secret string in the response json object.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret_json = get_secret_value_response['SecretString']
            secret = json.loads(secret_json)
            return secret
        else:
            decoded_binary_secret_json = base64.b64decode(get_secret_value_response['SecretBinary'])
            decoded_binary_secret = json.loads(decoded_binary_secret_json)
            return decoded_binary_secret


# This function gets a particular secret's raw response by its ARN
# there's no versionID in raw get_secret() response, use describe_secret()
def get_secret_raw(client, secret_arn, stage, token=None):
    try:
        # Only do VersionId validation against the stage if a token is passed in
        if token:
            get_secret_value_response = client.get_secret_value(SecretId=secret_arn, VersionId=token,
                                                                VersionStage=stage)
        else:
            get_secret_value_response = client.get_secret_value(SecretId=secret_arn, VersionStage=stage)
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
    else:
        return True


# This function lists metadata of all existing secrets
def list_secret(client):
    try:
        response = client.list_secrets(
            MaxResults=100,
            SortOrder='asc'
        )
    except ClientError as e:
        raise e
    else:
        if 'SecretList' in response:
            secrets = response['SecretList']
        else:
            logger.error('list_secret: "SecretList" field not exist in client.list_secrets() response.', exc_info=True)
            sys.exit()

        # list of all secrets (in raw format) in secret manager
        secret_list = list()
        for secret in secrets:
            secret_list.append(secret)
        return secret_list


# This function picks secrets (in key-value format) and ARN out from raw response of client.get_secret_value()
def list_secret_values(client, secret_list):
    # list of all secrets (in key-value format) in secret manager
    secret_value_list = list()
    for secret in secret_list:
        secret_arn = secret['ARN']
        secret_value = get_secret(client, secret_arn, current)
        secret_value['ARN'] = secret_arn
        secret_value_list.append(secret_value)
    return secret_value_list


# This function retrieves the ClientRequestToken(i.e. versionID) of a pending secret
def retrieve_pending_versionID(secret_arn):
    metadata = client.describe_secret(SecretId=secret_arn)
    for version in metadata["VersionIdsToStages"]:
        if pending in metadata["VersionIdsToStages"][version]:
            return version

    # if function hasn't return yet, it means no "AWSPENDING" found in "VersionIdsToStages"
    logger.error(f'retrieve_pending_versionID: no pending version found in secret {secret_arn}', exc_info=True)
    sys.exit()


# creates a secret of "other" type (i.e. non database type). This type of secret cannot be tested in the target system.
# todo this function assumes that the secret has a specific format
# This function rotates the secret in AWS secret manager and returns the value of new secret
def rotate_other_secret(client, secret_arn, new_version_id=None):
    exclude_characters = '`/@"\'\\'

    # make sure the secret exists
    try:
        secret = get_secret(client, secret_arn, current)
    except client.exceptions.ResourceNotFoundException:
        logger.error(f'rotate_other_secret: secret {secret_arn} not exist in AWS secret manager, exiting.\n', exc_info=True)
        # todo implement cross referencing and use it here
        sys.exit()
    else:
        logger.info(f'rotate_other_secret: Successfully retrieved secret for {secret_arn}, target secret exists.')

        # rotation logic
        # if pending version already exists, simply finish rotating secret
        pending_exists = get_secret_raw(client, secret_arn, pending)
        if pending_exists:
            logger.info(f'rotate_other_secret: pending version of secret {secret_arn} already exists. Rotating secret now.')

            if new_version_id:
                finish_secret(client, secret_arn, new_version_id)
            else:
                pending_version = retrieve_pending_versionID(secret_arn)
                # finish secret rotation
                finish_secret(client, secret_arn, pending_version)
        else:
            logger.info(f'rotate_other_secret: pending version of secret {secret_arn} already exists. Finishing secret now.')
            for key in secret.keys():
                passwd = client.get_random_password(ExcludeCharacters=exclude_characters)
                secret[key] = passwd['RandomPassword']

            # Using custom version id if it's passed in
            if new_version_id:
                client.put_secret_value(SecretId=secret_arn,
                                        ClientRequestToken=new_version_id,
                                        SecretString=json.dumps(secret),
                                        VersionStages=['AWSPENDING'])
                logger.info(f'rotate_other_secret: Successfully put secret for ARN {secret_arn} and custom version {new_version_id}.')
                finish_secret(client, secret_arn, new_version_id)
            # use AWS SDK automatic version id if no custom version id passed in
            else:
                client.put_secret_value(SecretId=secret_arn,
                                        SecretString=json.dumps(secret),
                                        VersionStages=['AWSPENDING'])
                logger.info(f'rotate_other_secret: Successfully put secret for ARN {secret_arn} with automatically generated version id.')
                pending_version = retrieve_pending_versionID(secret_arn)
                finish_secret(client, secret_arn, pending_version)


# This function finishes a pending rotation
def finish_secret(client, secret_arn, pending_version):
    # First describe the secret to get the current version
    metadata = client.describe_secret(SecretId=secret_arn)
    current_version = None
    for version in metadata["VersionIdsToStages"]:
        if current in metadata["VersionIdsToStages"][version]:
            # check if pending_version is a target secret's current version
            if version == pending_version:
                # pending_version is already marked as current, return
                logger.info(f'finish_secret: Version {pending_version} already marked as AWSCURRENT for secret {secret_arn}')
                return
            # remember the current version, which is the version to be replaced by pending_version
            current_version = version
            break

    client.update_secret_version_stage(SecretId=secret_arn,
                                       VersionStage=current,
                                       MoveToVersionId=pending_version,
                                       RemoveFromVersionId=current_version)
    client.update_secret_version_stage(SecretId=secret_arn,
                                       VersionStage=pending,
                                       RemoveFromVersionId=pending_version)
    logger.info(f'finish_secret: Successfully set AWSCURRENT stage to version {pending_version} for secret {secret_arn}')


# todo pre receive hook cannot have an IAM role that has access to all secrets in AWS secret manager
# do a rotate and see if it's successful, if successful, cancel_rotation????
def cross_ref(password_string):
    """
    :param password_string: the output from pre-commit hook which contains potential passwords
    :param region_name:
    :return:
    """

    pass


# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

secret_list = list_secret(client)
secret_value_list = list_secret_values(client, secret_list)

# print(secret_value_list[1])
# todo test rotate_other_secret(client, secret_value_list[0]['ARN'])
rotate_other_secret(client, secret_value_list[2]['ARN'])
# print(secret_list)

# todo need to think how to enforce "other" password format
# create_other_secret(client, secret_value_list[0]['ARN'], 'random')

# todo how to distinguish DB secret and "other" secret based on metadata? maybe tags?
# client.describe_secret() has the same output as client.list_secrets()
# for secret in secret_list:
#     secret_arn = secret['ARN']
#     metadata = client.describe_secret(SecretId=secret_arn)
#     print(metadata)
#
# print(retrieve_pending_versionID(secret_value_list[1]['ARN']))
# print(get_secret_raw(client, secret_value_list[1]['ARN'], pending))
