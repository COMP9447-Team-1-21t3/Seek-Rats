
from flask import render_template, request
from app import app
import requests
import os
import json
import re

#from sechub import report_secrets_finding, third_party_report

@app.route('/')

def home():
    # sec = request.args.get('secret')
    # report_finding(sec)
    return render_template("temp.html")

@app.route('/welcome')

def welcome():
    # sec = request.args.get('secret')
    # report_finding(sec)
    return render_template("login.html")




def mark_reviewer_done(user_id, repo_url):
    temp_dict = {93390642: 'False', 9999999: 'False'}  #go to database and get this val
    temp_dict[user_id] = 'True'
    print(temp_dict)

@app.route('/report' ,  methods = ["GET","POST"])

def report():

    if request.method == "POST":
        print("hello")

        user_id = "9999999" #Placeholder for now, also need to verify identity

        form = request.form.to_dict()
        
        repo_url = ""

        for key,val in form.items():
            if key == "id":
                repo_url = val
            elif key.isnumeric():
                if val == "hub":
                    print("Sending secret {} to {}".format(key, val))
                    #send to sec hub
                    pass
                elif val == "allow":
                    print("Sending secret {} to {}".format(key, val))
                    #send to allow list
                    pass

        mark_reviewer_done(user_id, repo_url) 

    
    secrets = [{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
                {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}]

    repo_url = "wontonz-1/draftstock"
    date = "14/10/21"
    return render_template("temp2.html", secrets_list=secrets, commit_id=repo_url, date=date) 



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

#Update the status of PR. Needs the HEAD_SHA, status and the repo_url ({owner/repo_name})
#Returns whether it succeeded or not
def update_status(sha, status, repo_url):

    url = 'https://api.github.com/repos/'+repo_url+'/statuses/'+sha
    token = 'token ' + str(os.environ['token']) #TODO : Get from parameter store
    payload = {'state': status , 'context':'Secrets Review Needed'} 
    # The state of the status. Can be one of error, failure, pending, or success.

    headers = {'Accept': 'application/vnd.github.v3+json', 'Authorization': token}

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    print(url)
    print(r.content)
    if r.status_code == 202:
        return "Success"
    else:
        return "Fail"

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
            print(url_re)
            print(url_re[0])

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
            org_id = ""

            if body["organization"]:
                is_org = True
                org_id = body["organization"]["id"]
                print("org id is " + str(org_id))

            print(action)
            print(head_sha)
            
            if action == "created" or action == "reopened" or action == "opened": 
                #TODO : Change pull request status to pending (DONE)
                #       Create the entries in the database
                #       Report table - create not completed status table first
                #       Reviewer table - Go through reviewer list if present and assign them (all in json)
                #       Secrets table - send the diff to code scanner and return needed information, then create table
                #       After entries created, trigger serverless frontend ? prob dont need this


                update_status(head_sha, "pending", repo_url) #Sets status of PR to pending

                reviewers = get_pr_reviewers(body)

                if reviewers != []: #Means at least 1 person assigned to review. 
                    #Create the table entry to be stored in the database
                    reviewer_table = {}

                    for user in reviewers:
                        reviewer_table[user] = 'False'
                    
                    print(reviewer_table) # TODO: Add to reviewer database

                #Get the diff of the commit
                diff_code = get_diff(body)
                print(diff_code)

                #Scan for secrets. Not yet implemented
                results = scan_diff(diff_code)

                #Then cross reference with allow list
                #TODO : Process the results of scan_diff/cross reference and put into the database


                #TODO : create dict

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
                pass

            elif action == "review_request_removed": #When someone removes a reviewer, remove them from reviewer table
                new_list = get_pr_reviewers(body)

                temp_dict = {93390642: 'False', 9999999: 'False'} #Use as place holder, actually get from database

                database_list = [*temp_dict]
                
                deleted_set = set(database_list) - set(new_list)
                    
                for val in deleted_set:
                    del temp_dict[val]
                    
                print(temp_dict) #this will replace the one in the database

                # Assume 
                #TODO : Need to compare existing reviewers to new reviewers list
                #       remove the missing reviewers from the database.
                #       Either delete entry and replace it or update it
                pass
            elif action == "review_requested": #When someone assigns a reviewer, add them to the reviewer table

                update_status(head_sha, "success", repo_url)

                new_list = get_pr_reviewers(body)

                temp_dict = {93390642: 'False', 9999999: 'False'} #Use as place holder, actually get from database

                database_list = [*temp_dict]
                
                deleted_set = set(new_list) - set(temp_dict)
                    
                for val in deleted_set:
                    temp_dict[val] = 'False'

                print(temp_dict) #this will replace the one in the database

                #TODO : Need to compare existing reviewers to new reviewers list
                #       add the new reviewers to the database.
                pass

    return render_template("login.html") 

