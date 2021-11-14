from flask import render_template, request
from app import app
import requests
import os
import json
import re
from report_status_tracking import *
import boto3

import urllib
#Database Test API

#Generates list of reviewers from dynamo db
def current_reviewers(url_re, dynamodb):
    database_list = read_tracking_report(url_re, dynamodb)
    print(database_list)
    current_reviewers = []

    if isinstance(database_list, list):
        if (database_list != []): 
            for status in database_list:
                current_reviewers.append(status["reviewerID"])

    return current_reviewers

#Checks if user is authenticated, returns False if not, returns token if yes
def authenticate_user(code):
    client_id = "bafc9bb95ef83e08ded6" #get from param store
    secret = ""

    url = 'https://github.com/login/oauth/access_token?'
    #cert_str = get_parameter("gitapp_PKey").get("Parameter").get("Value")
    #app_id = get_parameter("gitapp_appID").get("Parameter").get("Value")
    payload = {'client_id': client_id, 'client_secret': secret, 'code' : code} 
    headers = {'Accept' : 'application/json'}

    encoded = urllib.parse.urlencode(payload)
    url = url + encoded

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    json_res = json.loads(r.content)
    access_token = ""
    try:
        access_token = json_res['access_token']
        return access_token
    except:
        return False

def get_user_id(access_token):

    url = "https://api.github.com/user"
    token = 'token ' + str(access_token)
    headers = {'Authorization': token, 'Accept': 'application/vnd.github.v3+json'}
    r = requests.get(url, headers=headers)

    try:
        return json.loads(r.content)['id']
    except:
        return False


#Checks whether the URL is valid or not
#False = not valid, A return = valid
def valid_url(url):
    try:
        url_re = re.findall("^([^\/]*\/[^\/]*)", url)
        url_re = url_re[0] #Has the owner/repo
        return url_re
    except:
        return False



def convert_db_secrets(secrets_list):
    #secrets_list = [{'reportURL': 'report123', 'secret': 'password 1', 'secret_info': 'line 29', 'secret_status': 'allowlist', 'secretNum': '1'}, {'reportURL': 'report123', 'secret': 'password 2', 'secret_info': 'line 112', 'secret_status': 'security hub', 'secretNum': '2'}]

    temp_list = []

    if isinstance(secrets_list, list) and (secrets_list != []):
        
        for secret in secrets_list:
            temp_dict = {}
            temp_dict['secret'] = secret['secret']
            temp_dict['type'] = "Unknown Secret"
            temp_dict['location'] = secret['secret_info']
            temp_dict['code_location'] =  secret['secret']
            temp_dict['id'] = secret['secretNum']
            temp_list.append(temp_dict)
    print("asdsa")
    print(temp_list)
    return temp_list
    # secrets = [{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
    #         {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}]

@app.route('/report' ,  methods = ["GET","POST","OPTIONS"])
def auth_report_db():

    if request.method == "POST":
        print(request.data)
        request_dict =  json.loads(request.data)
        code = request_dict['code']
        repo_url = request_dict['repo_url']

        if valid_url(repo_url) == False: #check if invalid
            repo_url = "a" #TODO: for testing
        
        #TODO: Get the keys from parameter store
        token = authenticate_user(code)
        if token == False:
            print("not valid github user")  #TODO: for testing
            return 400
        
        user_id = str(get_user_id(token))
        if user_id == False:
            print("wrong user id")  #TODO: for testing
            return 400
        print('user id =' + str(user_id))

        #Access database
        url = "http://localhost:8000"
        dynamodb = boto3.resource('dynamodb', endpoint_url=url)

        #Check if they are assigned to the report, if not 
        curr_reviewers = current_reviewers(repo_url,dynamodb)
        print(repo_url)
        print(curr_reviewers)
        if str(user_id) not in curr_reviewers:
            print("not in curr reviewers") #TODO: for testing
            pass
            return 400

        print("nice")

        #If they pass all the checks retrieve data from the database 
        db_secrets = read_secret(repo_url, dynamodb)
        print(db_secrets)
        secrets = convert_db_secrets(db_secrets)
        print(secrets)
        headers = {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin" : "*"
        }

        return {
            'statusCode': 200,
            'body': json.dumps(secrets),
            'token' : token,
            'headers': headers
        }
    else:
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Headers' : '*'
        }
    
        return {
            'statusCode': 200,
            'headers': headers
        }

#Update the status of PR. Needs the HEAD_SHA, status and the repo_url ({owner/repo_name})
#Returns whether it succeeded or not
def update_status(sha, status, repo_url, return_url):

    url = 'https://api.github.com/repos/'+repo_url+'/statuses/'+sha
    token = 'token ' + str(os.environ['token']) #TODO : Get from parameter store
    target_url = str(os.environ['ngrok']) + "/?repo_url=" + str(return_url)
    payload = {'state': status , 'context':'Secrets Review Needed', 'target_url': target_url} 
    # The state of the status. Can be one of error, failure, pending, or success.

    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization': token}

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(url)
    print(r.content)
    if r.status_code == 202:
        return "Success"
    else:
        return "Fail"


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

# #Given a user_id and json_list, mark the user_id as done
# #Returns updated dict but does not send back to database.
# def mark_reviewer_done(user_id, json_list):

#     temp_dict = json_list

#     if isinstance(temp_dict, list) and (temp_dict != []):
#         for reviewer in temp_dict:
            
#             if reviewer['reviewerID'] == user_id:
#                 reviewer['tracking_status'] = True

#     return temp_dict

#Attempts to send all secrets to the allow list. 
#If all sent to allow list-> ret True. If any not send e.g. to hub -> ret False
def send_to_allow_list(secrets_list):
    check = True

    if isinstance(secrets_list, list) and (secrets_list != []):
        for secret in secrets_list:

            if secret['secret_status'] == "allow":
                #TODO: Send to the allow list
                pass
            else:
                check = False

    return check

#Send all secrets to the allow list 
def get_secret_statuses(secrets_list):

    temp_list = []

    if isinstance(secrets_list, list) and (secrets_list != []):
        
        for secret in secrets_list:
            temp_dict = {}
            temp_dict[secret['secretNum']] = secret['secret_status']
            temp_list.append(temp_dict)

    return temp_list

#Testing report
@app.route('/' ,  methods = ["GET","POST","OPTIONS"])
def report():
    if request.method == "POST":

        url = "http://localhost:8000" #remove after
        
        # form = event
        # # user_token = form["user"] #TODO: verify identity
        # report = form["body"]
        # report = str(report)
        # report_json = json.loads(report)
        
        # user_token = report_json["user"]
        # report_list = report_json["body"]
        # sha = report_json["commit_sha"]
        
        # repo_url = ""
 
        form = request.json
        body = form["body"]
        token = form["token"]
        repo_url = str(form["repo_url"])

        org_repo_url = valid_url(repo_url)

        if org_repo_url == False: #NOT VALID URL
            print("invalid url")
            return 400 #TODO: update this

        user_id = str(get_user_id(token)) #check if they have correct id
        if user_id == False:
            print("wrong user id")  #TODO: for testing
            return 400

        dynamodb = boto3.resource('dynamodb', endpoint_url=url)

        print("nice")
        secrets = read_secret(repo_url, dynamodb)
        print("=====BEFORE SECRETS=====")
        print(secrets)

        assigned_reviewers = current_reviewers(repo_url,dynamodb)
        if str(user_id) not in assigned_reviewers:
            print('not in assigned reviewers')
            return "400"
            pass

        # #Temporary. Go through the form and update the secrets table
        # for list_item in report_list:
        #     key = list_item[0]
        #     val = list_item[1]

            # if key.isnumeric():

            #     curr_val = "N/A"
            #     try:
            #         curr_val = secrets[str(key)]
            #         print("curr val " + str(curr_val))
            #     except:
            #         pass

            #     if val == "hub":
            #         print("Sending secret {} to {}".format(key, val))

            #         if curr_val != "hub":
            #             pass #Do nothing since its already been sent to sechub
            #         else: #New status is hub, send to security hub
            #             update_secret_status(repo_url, str(val), "hub", dynamodb)
            #             #TODO: Send to sec hub

            #     elif val == "allow":
            #         print("Sending secret {} to {}".format(key, val))

            #         if curr_val == "hub" or curr_val == "allow":
            #             pass #Do nothing since its already been changed
            #         else: #hasn't been touched, so just update the allow list 
            #             update_secret_status(repo_url, str(val), "hub", dynamodb)


        status_secrets = get_secret_statuses(secrets)

        for list in body:
            key = list[0]
            val = list[1]
            if key.isnumeric():
                
                curr_val = "N/A"
                try:
                    curr_val = status_secrets[str(key)]
                    print("curr val " + str(curr_val))
                except:
                    pass

                if val == "hub":
                    print("Sending secret {} to {}".format(key, val))

                    if curr_val == "hub":
                        pass #Do nothing since its already been sent to sechub
                    else: #New status is hub, send to security hub
                        update_secret_status(repo_url, str(key), "hub", dynamodb)
                        #TODO: Send to sec hub

                elif val == "allow":
                    print("Sending secret {} to {}".format(key, val))

                    if curr_val == "hub" or curr_val == "allow":
                        pass #Do nothing since its already been changed
                    else: #hasn't been touched, so just update the allow list 
                        update_secret_status(repo_url, str(key), "allow", dynamodb)


        #Update tracking for the user and check if all reviewers are done
        update_tracking_status(repo_url, user_id , True, dynamodb) #updates tracking for the user
        status_table = read_tracking_report(repo_url, dynamodb)
        print("---after status--")
        print(status_table)
        print("------ --")
        print(check_all_reviewers(status_table))
        
        secrets = read_secret(repo_url, dynamodb)
        print("=====AFTER SECRETS=====")
        print(secrets)

        if check_all_reviewers(status_table): #Checks if all reviewers have reviewed the list. 
            #If all reviewers have finished their reviewer

            secrets = read_secret(repo_url, dynamodb) #Get new secrets table with updated values
            all_allow = send_to_allow_list(secrets)

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
    else:
        headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Headers' : '*',
        }
    
        return {
            'statusCode': 200,
            'headers': headers
        }


#----------------------------------------------------------------------------------------

#Given the pull request body, return a list of assigned reviewers
def get_pr_reviewers(body):
    reviewer_list =  []

    if body['pull_request']['requested_reviewers']:
        for reviewer in body['pull_request']['requested_reviewers']:
            reviewer_list.append(str(reviewer['id']))
    
    return reviewer_list

#Use the API and get the diff for the current PR. Returns either N/A or the diff
def get_diff(body):

    url = body['pull_request']['url']
    token = 'token ' + str(os.environ['token']) #TODO : Get from parameter store
    headers = {'Accept': 'application/vnd.github.v3.diff', 'Authorization': token}
    r = requests.get(url,  headers=headers)
    

    if r.status_code == 200:
        return r.content
    else:
        return "N/A"

        
def scan_diff(diff_code):

    #TODO : Scan the code 
    pass

#Creates a database entry value to be stored in the database
def create_database_entry_value(reportURL, SHA, reviewers, dynamodb):
    #If empty, return empty list
    if reviewers != []: 
        for user in reviewers:
            insert_tracking(reportURL, str(user), SHA, status=False, dynamodb=dynamodb)
    
    return reviewers

@app.route('/github_update' ,  methods = ["GET","POST"])

def github_update():
    url = "http://localhost:8000"
    if request.method == 'POST':

        dynamodb = boto3.resource('dynamodb', endpoint_url=url)
        body = request.json
        action = body['action']

        #Check whether the webhook is a pull request update
        if body["pull_request"]:

            url = body['pull_request']['url']
            url_re = re.findall("(?<=github.com\/repos\/).*$", url)
            url_re = url_re[0] #Has the owner/repo + pull id inside

            diff_url = body['pull_request']['diff_url']
            head_sha = body["pull_request"]['head']['sha'] #Head_sha is the sha of the latest commit in the pull request. Needed to change status
            username = body['pull_request']['user']['login']
            uid = body['pull_request']['user']['id']           
            repo_url = body['repository']["full_name"]
            repo_id = body['repository']["id"]
            pull_id = body['number']

            is_org = False
            owner_id = body['repository']["owner"]["id"]

            try:
                if body["organization"]:
                    is_org = True
            except:
                pass

            print(action)
            print(head_sha)
            print("====BEFORE====")
            print(read_tracking_report(url_re, dynamodb))
            if action == "edited":
                # Remove all tables and recreate the tables and status by using similar process to create/reopened
                delete_tracking_record(url_re, dynamodb)
                pass
                
            if action == "created" or action == "reopened" or action == "opened" or action == "edited": 
                #TODO : Change pull request status to pending (DONE)
                #       Tracking table - create not completed status table first (DONE)
                #       Secrets table - send the diff to code scanner and return needed information, then create table (Not done)

                #Set up the report table. Report table key name will be the owner/repo + pull id OR repo id+ pull id.
                #For now, report table key name will be {owner name}/{repo name}
                #May be removed
                # report_table_key_name = url_re
                # report_table_dict = {}
                # report_table_dict['SHA'] = head_sha
                # report_table_dict['owner_id'] = owner_id
                # report_table_dict['repo_id'] = repo_id
                # report_table_dict['is_org'] = is_org

                #Gather reviewers from the PR request and store them in report table
                reviewers = get_pr_reviewers(body)

                if reviewers == []: #No reviewers, allow for it to be merged
                    #Set status of pull request to pending
                    update_status(head_sha, "success", repo_url,url_re )
                else:  #Deny auto pull request
                    #Set status of pull request to pending
                    update_status(head_sha, "pending", repo_url,url_re )
                    report_list = create_database_entry_value(url_re, head_sha, reviewers, dynamodb)
                
                #Set up the secrets table. Get the diff->scan it->cross reference results-> put into table
                #Get the diff of the commit
                diff_code = get_diff(body)
                results = scan_diff(diff_code)

                insert_secret(url_re, '1', 'secret 1', 'line 29', 'N/A', dynamodb)
                insert_secret(url_re, '2', 'secret 2', 'line 112', 'N/A', dynamodb)
                #TODO: Scan for secrets in the diff. Not yet implemented
                #TODO: Then cross reference with allow list
                #TODO : Process the results of scan_diff/cross reference and put into the database\

            elif action == "deleted" or action == "closed":
                delete_tracking_record(url_re, dynamodb)
                delete_secret_record(url_re, dynamodb)


            elif action == "assigned":
                pass

            elif action == "unassigned":
                pass

            elif action == "ready_for_review":
                pass

            elif action == "synchronize":
                #HEAD SHA is required to update the status
                #TODO: May do the same thing as action=="edited"

                update_SHA(url_re, headsha, dynamodb)

                pass

            elif action == "review_request_removed": #When someone removes a reviewer, remove them from reviewer table
                
                new_list = get_pr_reviewers(body)
                db_list = current_reviewers(url_re, dynamodb)

                new_set = set(db_list) - set(new_list)

                for val in new_set:
                    delete_tracking(url_re, str(val), dynamodb)


                if check_all_reviewers(read_tracking_report(url_re, dynamodb)):
                    update_status(head_sha, "success", repo_url, url_re)

            elif action == "review_requested": #When someone assigns a reviewer, add them to the reviewer table
                
                new_list = get_pr_reviewers(body)
                db_list = current_reviewers(url_re, dynamodb)

                new_set = set(new_list) - set(db_list)
                print(new_set)
                for val in new_set:
                    insert_tracking(url_re, str(val), head_sha, False, dynamodb)

                update_status(head_sha, "pending", repo_url, url_re)


        print("====AFTER====")
        print(read_tracking_report(url_re, dynamodb))
        secrets = read_secret(url_re, dynamodb)
        print(secrets)

    return render_template("login.html") 

