import json
import boto3

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

    if isinstance(reviewer_list, list):

        if (reviewer_list != []) and (False in reviewer_list.values()):
            check = False
    
    else:
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
            'body' : request,
            'headers': headers
        }

    if request == 'POST':
        user_id = "9999999" #Placeholder for now, TODO: verify identity
        
        form = event
        # user_token = form["user"] #TODO: verify identity
        report = form["body"]
        report = str(report)
        report_json = json.loads(report)
        
        user_token = report_json["user"]
        report_list = report_json["body"]
        sha = report_json["commit_sha"]
        
        repo_url = ""

        #Temporary. Go through the form and update the secrets table
        for list_item in report_list:
            key = list_item[0]
            val = list_item[1]

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
            #update_status(form["sha"], "success", form["id"])

            pass

        else: #Not all reviewers have finished
            # TODO: Send the reviewers_table report to reviewer database
            pass

    
        headers = {
            'Content-Type': 'text/plain',
            'Access-Control-Allow-Origin' : '*',
            'Access-Control-Allow-Headers' : '*',
        }
    
        return {
            'statusCode': 200,
            'body' : event,
            'headers': headers
        }