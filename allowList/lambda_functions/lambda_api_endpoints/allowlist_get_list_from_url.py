
import json
import requests
# "www.github.com/{ORG}/{REPO}"

github_API_url = "www.api.github.com/repos"
OAUTH_TOKEN = "temps"

def lambda_handler(event, context):
    url = event['url']
    with_info = event['with_info']

    split_url = url.split("/")
    if len(split_url) != 3 or  "github.com" not in split_url[0]:
        return {
            'statusCode': 402,
            'description': "Invalid URL"
        }
    
    org_name = split_url[1].strip()
    repo_name = split_url[2].strip()
    
    request_url = f"{github_API_url}/{org_name}/{repo_name}"
    response = requests.get(request_url, headers={"Authorization": f"token {OAUTH_TOKEN}"})

    if response.status_code != 200:
        return {
            'statusCode': 402,
            'description': "Invalid URL"
        }

    res_dict = response.json()
    