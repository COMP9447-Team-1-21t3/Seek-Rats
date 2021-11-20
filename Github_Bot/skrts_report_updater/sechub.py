import json
import boto3
from datetime import datetime, timezone
import re


def lambda_handler(event, context):
    httpMethod = event["httpMethod"]
    commiter = ""
    reporter = ""
    commit_id = ""
    repo_url = ""
    secrets = ""
    if httpMethod == "GET":
        commiter = event["queryStringParameters"]["commiter"]
        reporter = event["queryStringParameters"]["reporter"]
        commit_id = event["queryStringParameters"]["commit_id"]
        repo_url = event["queryStringParameters"]["repo_url"]
        secrets = event["queryStringParameters"]["secrets"]
    elif httpMethod == "POST":
        body = json.loads(event["body"])
        commiter = body["commiter"]
        reporter = body["reporter"]
        commit_id = body["commit_id"]
        repo_url = body["repo_url"]
        secrets = body["secrets"]

    status = third_party_report(commiter, reporter, commit_id, repo_url, secrets)
    return {
        'statusCode': 200,
        # 'body':json.dumps(event)
        'body': json.dumps(status)
    }


# Function to report a finding to security hub given a title and description
def report_secrets_finding(title, description):
    client = boto3.client('securityhub')

    filters = {
        "ProductName": [
            {
                "Comparison": "EQUALS",
                "Value": "Default"
            }
        ]
    }

    # Access security hub and get the most recent finding Id
    ret_findings = str(client.get_findings(Filters=filters))
    reg = re.findall("Id[0-9]+", ret_findings)
    max_num = 0

    for ID in reg:
        curr = int(ID[2:])
        if curr > max_num:
            max_num = curr

    max_num += 1

    # Get current datetime for finding report
    uid_client = boto3.client("sts")
    uid = str(uid_client.get_caller_identity()["Account"])
    now = datetime.now(tz=timezone.utc)
    time = now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Get region
    region = str(client.meta.region_name)

    # Prefill the required finding report template
    secret_val = description
    product = "arn:aws:securityhub:" + region + ":" + uid + ":product/" + uid + "/seekrat"
    find_id = "Id" + str(max_num)

    findings = [{
        "AwsAccountId": uid,
        "CreatedAt": time,
        "Description": description,
        "FindingProviderFields": {
            "Severity": {
                "Label": "CRITICAL",
                "Original": "0"
            },
            "Types": [
                "Software and Configuration Checks/Vulnerabilities/ExposedSecret"
            ]
        },
        "Id": find_id,
        "GeneratorId": "TestGeneratorId",
        "ProductArn": "arn:aws:securityhub:ap-southeast-2:" + uid + ":product/" + uid + "/default",
        "Resources": [
            {
                "Id": "arn:aws:secretsmanager:ap-southeast-2:" + uid + ":secretsmanager",
                "Partition": "aws",
                "Region": "ap-southeast-2",
                "Type": "Secrets"
            }
        ],
        "SchemaVersion": "2018-10-08",
        "Title": title,
        "CreatedAt": time,
        "UpdatedAt": time
    }]

    # Push finding to secrets manager
    response = client.batch_import_findings(Findings=findings)

    if response["SuccessCount"] == 1:
        print("success!")
        return "Success"
    else:
        print(response)
        return "Error"


# Generate the third party secrets report and report to security hub
def third_party_report(reporter, repo_url, secret):
    title = "[{}] Code Review Secret Report".format(repo_url)

    desc = "Reported by {}, Repo = {}".format(reporter, repo_url)
    desc += " Secret Reported: "
    desc += " {},".format(secret)

    desc = desc[:-1]

    status = report_secrets_finding(title, desc)
    
    print(status)
    return status