import json
import report_status_tracking as rst
from helpers import *
from differ import *
import requests
import os
import re
import boto3
import urllib
from generateToken.gitapp_generateToken import generate_token, generate_token_header


#Given the pull request body, return a list of assigned reviewers
def get_pr_reviewers(body):
    reviewer_list =  []

    if body['pull_request']['requested_reviewers']:
        for reviewer in body['pull_request']['requested_reviewers']:
            reviewer_list.append(str(reviewer['id']))
    
    return reviewer_list

#Update the status of PR. Needs the HEAD_SHA, status and the repo_url ({owner/repo_name})
#Returns whether it succeeded or not
def update_status(sha, status, repo_url, return_url):

    url = 'https://api.github.com/repos/'+repo_url+'/statuses/'+sha
    
    owner_str = str((re.findall("(?:(?!\/).)*", repo_url))[0])
    repo_str = str((re.findall("\/(.*)", repo_url))[0])
    
    print("gonna run generate token with {} {}".format(owner_str, repo_str))
    token_str = generate_token(owner_str, repo_str)
    headers = generate_token_header(token_str)
    
    
    f = open("config.txt", "r")
    target = f.read()

    target_url = str(target) + "?repo_url=" + str(return_url)
    payload = {'state': status , 'context':'Secrets Review Needed', 'target_url': target_url} 
    # The state of the status. Can be one of error, failure, pending, or success.

    #headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization': token}

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(r.content)
    if r.status_code == 202:
        return "Success"
    else:
        return "Fail"

#Use the API and get the diff for the current PR. Returns either N/A or the diff
def get_diff(body, repo_url):

    url = body['pull_request']['url']
    owner_str = str((re.findall("(?:(?!\/).)*", repo_url))[0])
    repo_str = str((re.findall("\/(.*)", repo_url))[0])
    token_str = generate_token(owner_str, repo_str)

    token = 'token ' + str(token_str) 
    headers = {'Accept': 'application/vnd.github.v3.diff', 'Authorization': token}
    r = requests.get(url,  headers=headers)
    print(r.content)

    if r.status_code == 200:
        return r.content
    else:
        return "N/A"

#Use Gitleaks to scan the diff and return list of secrets present in dict format
#Does this by creating a file and writing the diff to it. Then runs git leaks
#Returns [] if empty
def scan_diff(diff_code, allow_list_terms):

    #Create the file and write the diff to it
    f=open("/tmp/diff.txt", "w")
    diff_str  = str(diff_code)
    diff_str = diff_str.replace(r'\n', '\n')
    diff_str = diff_str.replace(r'\'', '\'')
    content=f.write(diff_str)
    f.close()
    
    secrets = gitleaks_scan_diff(allow_list_terms, "/tmp/diff.txt")

    if secrets == 0:
        return []
    else:
        return secrets
    pass


#Checks if all reviewers have completed the report.
#Return True for yes, False for no.
def check_all_reviewers(reviewer_list):
    check = True

    if isinstance(reviewer_list, list):
        if (reviewer_list == []):
            check = True
        else:    
            for status in reviewer_list:
                
                if status["tracking_status"] == False:
                    check = False
                    return check
    else:
        check = False
    return check
    
    