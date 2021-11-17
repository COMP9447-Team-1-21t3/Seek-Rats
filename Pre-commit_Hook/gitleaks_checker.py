import os
import subprocess
import sys

def checker(report_err, report_out):
    if not report_err:
        return 0

    if report_err:
        print("Hardcoded secrets detected in your commit, use 'git commit --no-verify instead'")
        return 1

def main():
    loc = os.getcwd()
    print('This is the current directory:',loc)

    process = subprocess.run(["gitleaks","-v", "--path="+ loc, "--unstaged"], capture_output= True , text= True)

    process

    report_out = process.stdout
    report_err = process.stderr
    return_val = checker(report_err, report_out)

    return return_val

if __name__ == '__main__':
    raise SystemExit(main())