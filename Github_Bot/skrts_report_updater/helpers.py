import re
import requests
import json
from generateToken.gitapp_generateToken import generate_token, generate_token_header


#Checks whether the URL is valid or not
#False = not valid, A return = valid
def valid_url(url):
    try:
        url_re = re.findall("^([^\/]*\/[^\/]*)", url)
        url_re = url_re[0] #Has the owner/repo
        return url_re
    except:
        return False
        
        
def get_user_id(access_token):
    print(access_token)
    url = "https://api.github.com/user"
    token = 'token ' + str(access_token)
    headers = {'Authorization': token, 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)

    
    try:
        user_dict = {}
        user_dict['id'] = json.loads(r.content)['id']
        user_dict['username'] = json.loads(r.content)['login']
        return user_dict
    except:
        return False
        
#Put all secrets statuses in a list with their index as their secret number
def get_secret_statuses(secrets_list):

    temp_dict = {}

    if isinstance(secrets_list, list) and (secrets_list != []):
        
        for secret in secrets_list:
            temp_dict[secret['secretNum']] = secret['secret_status']

    return temp_dict
    
#Put all secrets in a list with their index as their secret number
def get_secrets_list(secrets_list):

    temp_dict = {}

    if isinstance(secrets_list, list) and (secrets_list != []):
        
        for secret in secrets_list:
            temp_dict[secret['secretNum']] = secret['secret_info']

    return temp_dict
    
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