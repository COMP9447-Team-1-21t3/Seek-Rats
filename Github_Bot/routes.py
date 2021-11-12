
from flask import render_template, request
from app import app
import requests
import os
import json
import re


#Update the status of PR. Needs the HEAD_SHA, status and the repo_url ({owner/repo_name})
#Returns whether it succeeded or not
def update_status(sha, status, repo_url):

    url = 'https://api.github.com/repos/'+repo_url+'/statuses/'+sha
    token = 'token ' + str(os.environ['token']) #TODO : Get from parameter store
    payload = {'state': status , 'context':'Secrets Review Needed', 'target_url': str(os.environ['ngrok'])} 
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
    if False in reviewer_list.values():
        check = False
    return check

#Gets reviewer table in the database and marks the reviewer as done.
#Returns updated dict but does not send back to database.
def mark_reviewer_done(user_id, repo_url):

    temp_dict = {'93390642': True, '9999999': False}  #TODO: go to database and get this val
    temp_dict[user_id] = True
   
    return temp_dict

#Send all secrets to the allow list 
def send_to_allow_list(secrets_list):

    #TODO : go through the secrets database entry and send all to the allow list
    #send to allow list   /allowlist/add_terms/{org_id}/{repo_id}:
    pass
#Testing report
@app.route('/' ,  methods = ["GET","POST"])
def report():

    if request.method == "POST":
        print("hello")

        user_id = "9999999" #Placeholder for now, also need to verify identity

        form = request.form.to_dict()
        
        repo_url = ""

        #Temporary. Go through the form and update the secrets table
        for key,val in form.items():
            if key == "id":
                repo_url = val
            elif key.isnumeric():
                if val == "hub":
                    print("Sending secret {} to {}".format(key, val))
                    #update secrets table to make it send to sec hub
                    #send security report to security hub for that specific one if it hasn't been done before
                    pass
                elif val == "allow":
                    print("Sending secret {} to {}".format(key, val))
                    #update secrets table to make it allowlist for that secret
                    #if its already sechub do not change
                    pass

        reviewers_table = mark_reviewer_done(user_id, repo_url) 
        print(reviewers_table)
        print(check_all_reviewers(reviewers_table))
        if check_all_reviewers(reviewers_table): #Checks if all reviewers have reviewed the list. 
            #If all reviewers have finished their reviewer
            # TODO: Check if all secrets in the PR are allow list secrets 
            #       If any of them are sechub, deny the PR.

            # TODO: Delete all entries relating to the unique id as its completed 

            #Update the status of the PR if all are add to allow list
            update_status(form["sha"], "success", form["id"])

        else: #Not all reviewers have finished
            # TODO: Send the reviewers_table report to reviewer database
            pass
    
    secrets = [{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
                {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}]

    repo_url = "wontonz-1/draftstock"
    sha = "9cfefad4a796475ea3945f2918f65fbaa56aad75"
    date = "14/10/21"
    return render_template("temp2.html", secrets_list=secrets, commit_id=repo_url, date=date, sha=sha) 



#----------------------------------------------------------------------------------------

#Given the pull request body, return a list of assigned reviewers
def get_pr_reviewers(body):
    reviewer_list =  []

    if body['pull_request']['requested_reviewers']:
        for reviewer in body['pull_request']['requested_reviewers']:
            reviewer_list.append(reviewer['id'])
    
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

@app.route('/github_update' ,  methods = ["GET","POST"])

def github_update():

    if request.method == 'POST':

        body = request.json
        action = body['action']

        #Check whether the webhook is a pull request update
        if body["pull_request"]:

            url = body['pull_request']['url']
            
            url_re = re.findall("(?<=github.com\/repos\/).*$", url)
            url_re = url_re[0] #Has the owner/repo + pull id inside

            diff_url = body['pull_request']['diff_url']
            #Head_sha is the sha of the latest commit in the pull request.
            #This is whats given to update the status check however can change.
            head_sha = body["pull_request"]['head']['sha']
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

            if action == "created" or action == "reopened" or action == "opened": 
                #TODO : Change pull request status to pending (DONE)
                #       Report table - create not completed status table first (Need to Send to database)
                #       Reviewer table - Go through reviewer list if present and assign them (Need to Send to database)
                #       Secrets table - send the diff to code scanner and return needed information, then create table (Not done)
                #       After entries created, trigger serverless frontend ? prob dont need this (Not done)


                #Set status of pull request to pending
                update_status(head_sha, "pending", repo_url)


                #Set up the report table. Report table key name will be the owner/repo + pull id OR repo id+ pull id.
                #For now, report table key name will be {owner name}/{repo name}
                report_table_key_name = url_re
                report_table_dict = {}
                report_table_dict['SHA'] = head_sha
                report_table_dict['owner_id'] = owner_id
                report_table_dict['repo_id'] = repo_id
                report_table_dict['is_org'] = is_org
                # TODO: Send to report database



                #Set up the reviewer table in the database.
                reviewers = get_pr_reviewers(body)
                if reviewers != []: #Means at least 1 person assigned to review. 
                    #Create the table entry to be stored in the database
                    reviewer_table = {}

                    for user in reviewers:
                        reviewer_table[str(user)] = False
                    
                    print(reviewer_table) 
                # TODO: Send to reviewer database


                #Set up the secrets table. Get the diff->scan it->cross reference results-> put into table
                #Get the diff of the commit
                diff_code = get_diff(body)
                print(diff_code)

                #TODO: Scan for secrets in the diff. Not yet implemented
                results = scan_diff(diff_code)

                #TODO: Then cross reference with allow list
                #TODO : Process the results of scan_diff/cross reference and put into the database\

            elif action == "edited":
                #TODO : Remove all tables to the original merge
                #       Recreate the tables and status by using similar process to create/reopened
                pass

            elif action == "deleted":
                #TODO :  Remove all entries from the database
                pass

            elif action == "assigned":
                pass

            elif action == "unassigned":
                pass

            elif action == "ready_for_review":
                pass

            elif action == "synchronize":
                #TODO : The HEAD SHA will update, you will have to update the database
                #       HEAD SHA - Latest commit which links to the status
                #       May do the same thing as action=="edited"

                #TODO : Get the report table from the database with same url_re
                
                temp_data = {'SHA': '1231231231', 'owner_id': 231312312, 'repo_id': 231312312, 'is_org': True}

                temp_data['SHA'] = head_sha

                #TODO : Send updated data to report database

                pass

            elif action == "review_request_removed": #When someone removes a reviewer, remove them from reviewer table
                new_list = get_pr_reviewers(body)

                temp_dict = {'93390642': False, '9999999': False} #Use as place holder, actually get from database

                database_list = [*temp_dict]
                
                deleted_set = set(database_list) - set(new_list)
                    
                for val in deleted_set:
                    del temp_dict[val]
                    
                print(temp_dict) #this will replace the one in the database
                #TODO : Send updated data to report database

                # Assume 
                #TODO : Need to compare existing reviewers to new reviewers list
                #       remove the missing reviewers from the database.
                #       Either delete entry and replace it or update it
                pass
            elif action == "review_requested": #When someone assigns a reviewer, add them to the reviewer table
                
                new_list = get_pr_reviewers(body)


                temp_dict = {'93390642': False, '9999999': False} #Use as place holder, actually get from database

                if temp_dict == {}: #empty list or not exisitng 
                    #TODO: Create a new entry and set new_list as the 
                    pass

                update_status(head_sha, "success", repo_url)

                database_list = [*temp_dict]
                
                deleted_set = set(new_list) - set(temp_dict)
                    
                for val in deleted_set:
                    temp_dict[val] = False

                print(temp_dict) #this will replace the one in the database
                #TODO : Send updated data to report database

                #TODO : Need to compare existing reviewers to new reviewers list
                #       add the new reviewers to the database.
                pass

    return render_template("login.html") 

