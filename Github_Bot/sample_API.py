import requests
from requests_aws_sign import AWSV4Sign
from boto3 import session


def create_findings_API(auth, commiter, reporter, commit_id, repo_url, secrets):
    endpoint = "https://c1bryfiwv5.execute-api.ap-southeast-2.amazonaws.com/dev/create_scurity_hub_finding"
    headers = {"Content-Type": "application/json"}
    payload = {
        "commiter": commiter,
        "reporter": reporter,
        "commit_id": commit_id,
        "repo_url": repo_url,
        "secrets": secrets
    }
    response = requests.post(endpoint, auth=auth, headers=headers, json=payload)
    print(response.text)


# to get executeAPI permission, make sure to configure 'serviceUser' by aws configure --profile serviceUser
session = session.Session(profile_name='serviceUser')
credentials = session.get_credentials()
region = session.region_name or 'ap-southeast-2'
service = 'execute-api'
# Signing API request
auth = AWSV4Sign(credentials, region, service)

# sample data
commiter = "dev-A",
reporter = ["reviewman-1", "reviewman-3"],
commit_id = "b8a68fd01e7ee3870a5a76190cf3dd286ecb9d13",
repo_url = "/COMP9447-Team-1-21t3/Demo_Repo/commit/",
secrets = ["Line 10 app.py (Rapid API Key)", "Line 29 app.py (Password)"]

create_findings_API(auth, commiter, reporter, commit_id, repo_url, secrets)

