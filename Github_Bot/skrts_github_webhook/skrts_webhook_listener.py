import json
import report_status_tracking as rst
from helpers import *
from differ import *
from allow_list_functions import *
import requests
import os
import re
import boto3
import urllib
from modifyTables import allowlist_modifyTables

#Generates list of reviewers from dynamo db
def current_reviewers(url_with_pull_id, dynamodb):
    database_list = rst.read_tracking_report(url_with_pull_id, dynamodb)
    current_reviewers = []

    if isinstance(database_list, list):
        if (database_list != []): 
            for status in database_list:
                current_reviewers.append(status["reviewerID"])

    return current_reviewers
    
#Creates a database entry value to be stored in the database
def create_database_entry_value(reportURL, SHA, reviewers, dynamodb):
    #If empty, return empty list
    if reviewers != []: 
        for user in reviewers:
            rst.insert_tracking(reportURL, str(user), SHA, status=False, dynamodb=dynamodb)
            
def get_allow_list_terms(owner_id, repo_id, dynamodb):
    return allowlist_modifyTables.read_repo(owner_id, repo_id, dynamodb=dynamodb)
    
def lambda_handler(event, context):

    request =event['requestContext']['http']['method']

    if request == 'POST':
        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
        
        print(event)
        
        body = json.loads(event['body'])
        
        if "installation" in body.keys():
            
            if "account" in body["installation"]:
                action = body['action']
                owner_id = body["installation"]["account"]["id"]
            
                if action=="created":
                    for repo in body['repositories']:
                        repo_id = repo['id']
                        setup_repo(owner_id, repo_id, dynamodb = dynamodb)
                
                if action == "added" or action=="removed":
                    for repo in body['repositories_added']:
                        repo_id = repo['id']
                        setup_repo(owner_id, repo_id, dynamodb = dynamodb)
                        
                    for repo in body['repositories_removed']:
                        repo_id = repo['id']
                        delete_repo(owner_id, repo_id, dynamodb = dynamodb)
                        
                elif action == "deleted" and body["installation"]["repository_selection"] == "all":
                    delete_org(owner_id, dynamodb)
                    pass
                        
                return 200
            
        if not ("repository" in body.keys() or "pull_request" in body.keys()):
            print("Unhandled request")
            return 201 #Unhandled request
            
        repo_url = body['repository']["full_name"] # will be in the format "octocat/Hello-World"

        owner_str = str((re.findall("(?:(?!\/).)*", repo_url))[0])
        repo_str = str((re.findall("\/(.*)", repo_url))[0])
        
        owner = body['repository']["owner"]["id"]
        repo = body['repository']["id"]

        if "repository" in body.keys():
            action = body['action']

            if action == "created":
               setup_repo(owner, repo, dynamodb)
            elif action == "deleted":
                delete_repo(owner, repo, dynamodb)

        #Check whether the webhook is a pull request update
        if "pull_request" in body.keys():
            action = body['action']
            url = body['pull_request']['url']
            url_with_pull_id = re.findall("(?<=github.com\/repos\/).*$", url)
            url_with_pull_id = url_with_pull_id[0] #The repo name 
    
            diff_url = body['pull_request']['diff_url']
            head_sha = body["pull_request"]['head']['sha'] #Head_sha is the sha of the latest commit in the pull request. Needed to change status        
    
            if action == "edited":
                # Remove all tables and recreate the tables and status by using similar process to create/reopened
                rst.delete_tracking_record(url_with_pull_id, dynamodb)
                
            elif action == "synchronize":
                #HEAD SHA is updated so must synchronise the pull
                #TODO: May do the same thing as action=="edited"
                rst.update_SHA(url_with_pull_id, headsha, dynamodb)
      
            if action == "created" or action == "reopened" or action == "opened" or action == "edited": 
                #New pull request, create entries in dynamodb for tracking and secrets 
                reviewers = get_pr_reviewers(body)
    
                if reviewers == []: #No reviewers, allow for it to be merged
                    #Set status of pull request to success
                    print("Updating status to success")
                    update_status(head_sha, "success", repo_url,url_with_pull_id )
                else:  #Deny auto pull request
                    #Set status of pull request to pending
                    print("Updating status to pending")
                    update_status(head_sha, "pending", repo_url,url_with_pull_id )
                    report_list = create_database_entry_value(url_with_pull_id, head_sha, reviewers, dynamodb)
                
                print("updated status")
                
                # Set up the secrets table. Get the diff->scan it->cross reference results-> put into table
                # Get the diff of the commit
                diff_code = get_diff(body, repo_url)
                allow_list_terms = get_allow_list_terms(owner, repo, dynamodb=dynamodb)
                results = scan_diff(diff_code, allow_list_terms)

                #Insert the secrets in the database
                sec_counter = 0
                for secret in results:
                    rst.insert_secret(url_with_pull_id, str(sec_counter), secret['secret'], secret['location'], 'N/A', dynamodb)
                    sec_counter = sec_counter + 1
    
            elif action == "deleted" or action == "closed":
                #Delete all records related to the name if deleted or closed
                rst.delete_tracking_record(url_with_pull_id, dynamodb)
                rst.delete_secret_record(url_with_pull_id, dynamodb)
    
            elif action == "review_request_removed": #When someone removes a reviewer, remove them from reviewer table
                #Find the diff between the database list and local list
                new_list = get_pr_reviewers(body)
                db_list = current_reviewers(url_with_pull_id, dynamodb)
    
                new_set = set(db_list) - set(new_list)
    
                for val in new_set:
                    rst.delete_tracking(url_with_pull_id, str(val), dynamodb)
    
                if check_all_reviewers(rst.read_tracking_report(url_with_pull_id, dynamodb)):
                    update_status(head_sha, "success", repo_url, url_with_pull_id)
    
            elif action == "review_requested": #When someone assigns a reviewer, add them to the reviewer table
                #Find the diff between the database list and local list
                new_list = get_pr_reviewers(body)
                db_list = current_reviewers(url_with_pull_id, dynamodb)
    
                new_set = set(new_list) - set(db_list)
               
                for val in new_set:
                    rst.insert_tracking(url_with_pull_id, str(val), head_sha, False, dynamodb)
    
                update_status(head_sha, "pending", repo_url, url_with_pull_id)
    
            secrets = rst.read_secret(url_with_pull_id, dynamodb)
        
            headers = {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin' : '*',
                'Access-Control-Allow-Headers' : '*',
            }
        
            return {
                'statusCode': 200,
                'body' : json.dumps(secrets),
                'headers': headers
            }

    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Headers' : '*',
    }

    return {
        'statusCode': 200,
        'headers': headers
    }