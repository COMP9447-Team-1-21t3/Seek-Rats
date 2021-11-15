import os
import subprocess
import json

def get_all_secrets(report_obj):
    all_secrets = []
    for i in range(len(report_obj)):
        secret = report_obj[i]['offender']
        all_secrets.append(secret)
    return all_secrets

def get_repo_url(report_obj):
    url = report_obj[0]['repoURL']
    return url

def checker(new_secrets):
    if (len(new_secrets)!=0):
        print("Hardcoded secrets detected in your commit, use 'git commit --no-verify instead'")
        return 1
    elif (len(new_secrets)==0):
        print(" No secrets detected, Commit Successful'")
        return 0


def main():
    loc = os.getcwd()
    print('This is the current directory:',loc)

    process = subprocess.run(["gitleaks","-v", "--path="+ loc, "--unstaged"], capture_output= True , text= True)

    report_out = process.stdout
    report_err = process.stderr

    if("No leaks found" in report_err or "repository does not exist" in report_err):
        print("No secrets in commit, Commit Successful")
        return 0

    else:
        loc = []
        for i in range(len(report_out)):
            if(report_out[i]=="}"):
                loc+=[i]

        for i in loc:
            if i!=loc[-1]:
                report_out = report_out[:i+1]+','+report_out[i+1:]

        report_out = '[' + report_out + ']'
        report_obj = json.loads(report_out)

        url = get_repo_url(report_obj)
    
        detected_secrets = []
        detected_secrets = get_all_secrets(report_obj)
        # print(detected_secrets)

        api_return_val = ("string", ("term",("no_val", "no_val")))

        my_results = [(api_return_val[1][1])]
        print(my_results)
        new_secrets = []
        for i in detected_secrets:
            if i not in my_results:
                new_secrets.append(i)
        
        print(new_secrets)
        val = checker(new_secrets)
        return val

if __name__ == '__main__':
    raise SystemExit(main())