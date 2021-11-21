import json
import report_status_tracking as rst
import requests
import os
import re
import boto3
import urllib
from generateToken.gitapp_generateToken_helpers import get_parameter

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
    
#Checks if user is authenticated, returns False if not, returns token if yes
def authenticate_user(code):
    print(code)
    
    client_id = get_parameter("gitapp_clientID").get("Parameter").get("Value")
    secret = get_parameter("gitapp_clientSecret").get("Parameter").get("Value")

    url = 'https://github.com/login/oauth/access_token?'
    #cert_str = get_parameter("gitapp_PKey").get("Parameter").get("Value")
    #app_id = get_parameter("gitapp_appID").get("Parameter").get("Value")
    payload = {'client_id': client_id, 'client_secret': secret, 'code' : code} 
    headers = {'Accept' : 'application/json'}

    encoded = urllib.parse.urlencode(payload) #Encoded and put it into url to be posted
    url = url + encoded

    r = requests.post(url, data=json.dumps(payload), headers=headers)
    json_res = json.loads(r.content)
    access_token = ""

    print(json_res)

    try:
        access_token = json_res['access_token']
        return access_token
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

#Checks whether the URL is valid or not
#False = not valid, A return = valid
def valid_url(url):
    try:
        url_re = re.findall("^([^\/]*\/[^\/]*)", url)
        url_re = url_re[0] #Has the owner/repo
        return url_re
    except:
        return False
        

def generate_return_header(status_code, message):
            
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin' : '*',
        'Access-Control-Allow-Headers' : '*',
    }
    
    return {
        'statusCode': status_code,
        'body' : message,
        'headers': headers
    }

#Convert database secrets to frontend readable format
def convert_db_secrets(secrets_list, repo_url):
    #secrets_list = [{'reportURL': 'report123', 'secret': 'password 1', 'secret_info': 'line 29', 'secret_status': 'allowlist', 'secretNum': '1'}, {'reportURL': 'report123', 'secret': 'password 2', 'secret_info': 'line 112', 'secret_status': 'security hub', 'secretNum': '2'}]

    temp_list = []

    if isinstance(secrets_list, list) and (secrets_list != []):
        
        for secret in secrets_list:
            temp_dict = {}
            temp_dict['secret'] = secret['secret']
            temp_dict['type'] = "Unknown Secret"
            temp_dict['location'] = repo_url
            temp_dict['code_location'] =  secret['secret_info']
            temp_dict['id'] = secret['secretNum']
            temp_list.append(temp_dict)
    
    print(temp_list)
    return temp_list

def lambda_handler(event, context):
    request = ""
    #request =event['requestContext']['http']['method']
    print(event)
    request = event["httpMethod"]
    
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
        response_code = 200

        request_dict = json.loads(event["body"])
        code = request_dict['code']

        #check if url is valid
        repo_url = request_dict['repo_url']
        if valid_url(repo_url) == False: #check if invalid
            response_code = 400
            body = "invalid url"
            return generate_return_header(response_code, body)

        #TODO: Get the keys from parameter store
        token = authenticate_user(code)
        if token == False and response_code != 400:
            print("not valid github user/bad code")  #TODO: for testing
            response_code = 401
            body = "not valid github user"
            return generate_return_header(response_code, body)
            
        user_info = get_user_id(token)
        print(user_info)
        if (user_info == "False" or user_info == False) and response_code != 400:
            print("wrong user id")  #TODO: for testing
            response_code = 401
            body = "wrong user id"
            return generate_return_header(response_code, body)

        user_id = str(user_info["id"])
        username = str(user_info["username"])
        token = str(token)
        print(token)
    
        #Access database
        
        dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')

        #Check if they are assigned to the report, if not 
        curr_reviewers = current_reviewers(repo_url,dynamodb)
        print(repo_url)
        print(curr_reviewers)

        if str(user_id) not in curr_reviewers and response_code != 400:
            print("not in curr reviewers") #TODO: for testing
            response_code = 403
            body = "not in curr reviewers"
            return generate_return_header(response_code, body)

        if response_code == 200 and response_code != 400:
            #If they pass all the checks retrieve data from the database 
            db_secrets = rst.read_secret(repo_url, dynamodb)
            print(db_secrets)
            secrets = convert_db_secrets(db_secrets, repo_url)
            print(secrets)
            
            body =  {}
            
            body['secrets'] = json.dumps(secrets)
            body['token'] = token
        

        headers = {
            'Content-Type': 'application/json',
            "Access-Control-Allow-Origin" : "*",
            'Access-Control-Allow-Headers' : '*'
        }
        return {
            'statusCode': response_code,
            'body': json.dumps(body),
            'token' : token,
            'headers': headers
        }
        
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