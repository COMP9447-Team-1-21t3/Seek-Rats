# from _typeshed import NoneType
import os
import subprocess
import json
from requests import get
import urllib.request
from urllib.parse import quote

def get_values(repo_url):
    baseURL = "https://cl2tu6os57.execute-api.ap-southeast-2.amazonaws.com/beta"
    url = f"{baseURL}/allowlist/get_list/"
    data = {
        'repo_url': quote(repo_url)
    }
    response = get(url, params=data)

    if response.status_code != 200:
        print("Server Error")
    else:
        return response.json()
        

def get_all_secrets(report_obj):
    all_secrets = []
    for i in range(len(report_obj)):
        secret = report_obj[i]['offender']
        all_secrets.append(secret)
    return all_secrets

def get_repo_url(report_obj):
    url = report_obj[0]['repoURL']
    return url

def checker(new_secrets):
    if (len(new_secrets)!=0):
        print("Hardcoded secrets detected, consider fixing or  use 'git commit --no-verify instead'")
        return 1
    elif (len(new_secrets)==0):
        print(" No secrets detected, Commit Successful'")
        return 0


def main():
    loc = os.getcwd() 
    secret_config = "/secret_config.toml"
    process = subprocess.run(["gitleaks","-v", "--path="+ loc, "--unstaged", '--config-path=' +loc + secret_config], capture_output= True , text= True)

    report_out = process.stdout
    report_err = process.stderr
    
    new_secrets = []
    if("No leaks found" in report_err or "repository does not exist" in report_err):
        val = checker(new_secrets)

    else:
        loc = []
        for i in range(len(report_out)):
            if(report_out[i]=="}"):
                loc+=[i]

        for i in loc:
            if i!=loc[-1]:
                report_out = report_out[:i+1]+','+report_out[i+1:]

        report_out = '[' + report_out + ']'
        report_obj = json.loads(report_out)

        repo_url = get_repo_url(report_obj)
    
        detected_secrets = get_all_secrets(report_obj)

        api_return_val = get_values(repo_url)
        
        my_results = []

        if("whitelist" in api_return_val.keys()):

            whitelist = api_return_val.whitelist

            for i in range(len(whitelist)):
                my_results += [whitelist[i][1].term]

        
        for i in detected_secrets:
            if i not in my_results:
                new_secrets.append(i)
       
    val = checker(new_secrets)
    return val

if __name__ == '__main__':
    raise SystemExit(main())