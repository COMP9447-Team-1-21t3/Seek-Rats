import json
import boto3
import requests
import os
import re
import report_status_tracking as rst
import urllib
from helpers import *
from modifyTables import allowlist_modifyTables
from generateToken.gitapp_generateToken import get_ids
from sechub import *
    
#Attempts to send all secrets to the allow list. 
#If all sent to allow list-> ret True. If any not send e.g. to hub -> ret False
def send_to_allow_list(secrets_list ,dynamodb, repo_url):
    check = True

    if isinstance(secrets_list, list) and (secrets_list != []):
        allow_terms = []
        for secret in secrets_list:

            if secret['secret_status'] == "allow":
                allow_terms.append(secret['secret'])
            else:
                check = False
                
        
        owner = str((re.findall("(?:(?!\/).)*", repo_url))[0])
        repo = str((re.findall("\/(.*)", repo_url))[0])
        print(owner + " " + repo)
        try :
            ids = get_ids(owner, repo)
            owner_id = ids['org_id']
            repo_id = ids['repo_id']
            
            new_terms = allow_terms
            
            insert_new_terms(owner_id, repo_id, new_terms, dynamodb=dynamodb)
        except:
            pass

    return check
    
    
#Generates list of reviewers from dynamo db
def current_reviewers(url_re, dynamodb):
    database_list = rst.read_tracking_report(url_re, dynamodb)
    print(database_list)
    current_reviewers = []

    if isinstance(database_list, list):
        if (database_list != []): 
            for status in database_list:
                current_reviewers.append(status["reviewerID"])

    return current_reviewers
    
    
def lambda_handler(event, context):
    request = ""
    try:
        request = event["httpMethod"]
    except:
        pass
    
    if request == 'OPTIONS':
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Headers' : '*',
            'body' : request
        }
    
        return {
            'statusCode': 200,
            'headers': headers
        }
    
    if request == 'POST':
        form = json.loads(event["body"])
        body = form["body"]
        repo_url = str(form["repo_url"])
        token = form["token"]

        org_repo_url = valid_url(repo_url)

        if org_repo_url == False: #NOT VALID URL
            print("invalid url")
            return 400 #TODO: update this

        user_info = get_user_id(token) #check if they have correct id
        if user_info == False:
            print("wrong user id")  #TODO: for testing
            return 400
        
        print(user_info)

        user_id = str(user_info["id"])
        username = str(user_info["username"])

        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')

        print("nice")
        secrets = rst.read_secret(repo_url, dynamodb)
        print("=====BEFORE SECRETS=====")
        print(secrets)

        assigned_reviewers = current_reviewers(repo_url,dynamodb)
        if str(user_id) not in assigned_reviewers:
            print('not in assigned reviewers')
            return 400
            pass

        # #Temporary. Go through the form and update the secrets table. This is in lambda format
        # for list_item in report_list:
        
        status_secrets = get_secret_statuses(secrets)
        print(status_secrets)
        secrets_list = get_secrets_list(secrets)
        print(secrets_list)

        for list in body:
            key = list[0]
            val = list[1]
            if key.isnumeric():
                
                curr_val = "N/A"
                curr_val = status_secrets[str(key)]
                curr_secret = secrets_list[str(key)]
                print("curr val " + str(curr_val) + str(curr_secret))

                if val == "hub":
                    print("Sending secret {} to {}".format(key, val))

                    if curr_val == "hub":
                        third_party_report(username, repo_url, curr_secret)
                        pass #Do nothing since its already been sent to sechub
                    else: #New status is hub, send to security hub
                        rst.update_secret_status(repo_url, str(key), "hub", dynamodb)
                        third_party_report(username, repo_url, curr_secret)

                elif val == "allow":
                    print("Sending secret {} to {}".format(key, val))

                    if curr_val == "hub" or curr_val == "allow":
                        pass #Do nothing since its already been changed
                    else: #hasn't been touched, so just update the allow list in database
                        rst.update_secret_status(repo_url, str(key), "allow", dynamodb)


        #Update tracking for the user and check if all reviewers are done
        rst.update_tracking_status(repo_url, user_id , True, dynamodb) #updates tracking for the user
        status_table = rst.read_tracking_report(repo_url, dynamodb)
        print("---after status--")
        print(status_table)
        print("------ --")
        print(check_all_reviewers(status_table))
        
        secrets = rst.read_secret(repo_url, dynamodb)
        print("=====AFTER SECRETS=====")
        print(secrets)

        if check_all_reviewers(status_table): #Checks if all reviewers have reviewed the list. 
            #If all reviewers have finished their reviewer

            secrets = rst.read_secret(repo_url, dynamodb) #Get new secrets table with updated values
            all_allow = send_to_allow_list(secrets, dynamodb, org_repo_url)

            print(all_allow)

            # Try to update the status of the PR 
            try: #If not empty, SHA should be stored in all status table lists
                sha = status_table[0]["SHA"]
                print(sha)
                print(org_repo_url)
                if all_allow == True: # All true = success
                    update_status(sha, "success", org_repo_url, repo_url)
                    print("updated success")
                else: # One failed = error
                    update_status(sha, "failure",  org_repo_url, repo_url)
                    print("updated failure")
            except:
                pass

        headers = {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin" : "*",
            "Access-Control-Allow-Methods" :"*"
        }

        return {
            'statusCode': 200,
            'body': 'success',
            'headers': headers
        } 
    
    headers = {
        'Content-Type': 'text/plain',
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Headers' : '*',
    }

    return {
        'statusCode': 201,
        'body' : event,
        'headers': headers
    }