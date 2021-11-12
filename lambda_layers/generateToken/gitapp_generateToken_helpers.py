import boto3

ssm = boto3.client("ssm")

def get_parameter(param_name):
    return ssm.get_parameter(
        Name=param_name,
        WithDecryption=True
    )
