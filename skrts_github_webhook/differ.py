
import json
import urllib

import os
import subprocess
import json

#Returns a dict of the secret with secret info
def get_new_secrets_dict(report_obj, new_secrets_list):
    all_secrets = []
    for i in range(len(report_obj)):
        secret_dict = {}
        if report_obj[i]['offender'] in new_secrets_list:
            secret_dict["secret"] = report_obj[i]['offender']
            secret_dict["location"] = report_obj[i]['line']
            secret_dict["type"] = report_obj[i]['rule']
            all_secrets.append(secret_dict)
    return all_secrets


def get_all_secrets(report_obj):
    all_secrets = []
    for i in range(len(report_obj)):
        secret = report_obj[i]['offender']
        all_secrets.append(secret)
    return all_secrets

def checker(new_secrets):
    if (len(new_secrets)!=0):
        print("Hardcoded secrets detected in your commit, use 'git commit --no-verify instead'")
        return 1
    elif (len(new_secrets)==0):
        print(" No secrets detected, Commit Successful'")
        return 0


def gitleaks_scan_diff(allow_list_terms, file_name=""):
    loc = str(os.getcwd()).strip()
    print('This is the current directory:',loc)
    print(file_name)
    if file_name == "":
        process = subprocess.run(["./gitleaks","-v", "--path="+ loc, "--unstaged"], capture_output= True , text= True)
    else:
        loc = file_name
        
        process = subprocess.run(["./gitleaks","-v", "--path="+ loc, "--no-git",], capture_output= True , text= True)
        print(process)
	
    report_out = process.stdout
    report_err = process.stderr
    print(report_out)
    print(report_err)

    if("No leaks found" in report_err or "repository does not exist" in report_err):
        print(report_out)
        print(report_err)
        print("No secrets in commit, Commit Successful")
        return 0

    else:
        print(report_out)
        print(report_err)
        temp_dict = {} #temp dict to be removed

        loc = []
        for i in range(len(report_out)):
            if(report_out[i]=="}"):
                loc+=[i]
                
        for i in loc:
            if i!=loc[-1]:
                report_out = report_out[:i+1]+','+report_out[i+1:]
                
        report_out = '[' + report_out + ']'
        report_obj = json.loads(report_out)

        detected_secrets = []
        detected_secrets = get_all_secrets(report_obj)
        # print(detected_secrets)
        
        my_results = []
        
        whitelist  = allow_list_terms
        #may just be allow_list_terms
        
        for i in range(len(whitelist)):
            my_results += [whitelist[i][1].term]
        
        for i in detected_secrets:
            if i not in my_results:
                new_secrets.append(i)
        
        print(new_secrets)
        val = checker(new_secrets)

        if val == 1:
            return get_new_secrets_dict(report_obj, new_secrets)
        else:
            return 0
