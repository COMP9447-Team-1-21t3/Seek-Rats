

# Seek-Rats

![This is an image](https://media.discordapp.net/attachments/894590864242905199/909389484888580146/tl.png)

A comprehensive secret detection and management solution that unites Security Operations with Developer Operations.

Our solution contains the follow components, and provides in-depth defence against hardcoded secrets while maintaining development speed:

- VSCode Extension, which highlights hardcoded secrets on the development console, and provides boiler templates for secure secret management. This also cross references and excludes secrets found on the allowlist.
- Pre-commit Hook, which prevents hardcoded secrets from being committed. This also cross references and excludes secrets found on the allowlist.
- Code Review , streamlined reporting of non-cross referenced secrets on a secure site when secrets are detected in a commit or pull request. The report can be used to either add to the universal allowlist or post an exposed secret finding to AWS’s Security Hub.

# Installation
## VS Code extension

To install extension locally, run 
```
cd VSCode_Extension/secretscanner/
npm install
```
#### How to use
Press F5 to enter debug mode

Create or open a file, press 
- Mac `CMD + Shift + P` 
- Windows `Ctrl-Shift-P`

and run the command 'Scan for Secrets' in the dropdown

## Pre-commit hook (Run locally)

This VS Code extension adds a command to your editor that when run will scan the current file for any hard coded secrets\

#### How to install

To try this extension out locally, in this directory, first run `npm install`\

## Allowlist and 



## VS Code extension (Run locally)

This VS Code extension adds a command to your editor that when run will scan the current file for any hard coded secrets\
Hard coded secrets that are found will be highlighted\
When you hover over a highlighted secret with your cursor, information about the secret will be displayed


=======
Seek-Rats contains the follow components and provides in-depth defence against hardcoded secrets while maintaining development speed:

- VSCode Extension, which highlights hardcoded secrets on the development console, and provides boiler templates for secure secret management. This also cross references and excludes secrets found on the allowlist.

- Pre-commit Hook, which prevents hardcoded secrets from being committed. This also cross references and excludes secrets found on the allowlist.

- Code Review , streamlined reporting of non-cross referenced secrets on a secure site when secrets are detected in a commit or pull request. The report can be used to either add to the universal allowlist or post an exposed secret finding to AWS’s Security Hub.

<!-- GETTING STARTED -->
## Getting Started

### Prerequisites


 - GitHub Repository

- [python 3.8](https://github.com/zricethezav/gitleaks) 

* [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)

* AWS Configured CLI
  ```sh
  sudo apt-get install awscli
  ```
* npm
  ```sh
  npm install npm@latest -g
  ```
* AWS CDK
  ```sh
  python -m pip install aws-cdk.aws-s3 aws-cdk.aws-lambda
  ```

  
## Installation and How to Use

Our Seek-Rats solution is a multi-layered solution where users either install all components for the whole system (works the best) or install individual pieces.

To install any/all components of Seek-Rats firstly clone the repo

Linux
  ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```

### **VSCode Extention Installation**
The VS Code extension adds a command to your editor that when run will scan the current file for any hard coded secrets. Hard coded secrets detected by the extension will be highlighted and when hovered over with your cursor displays any information about the secret if set.

1.  Firstly, navigate to the VSCode Extension Branch
  ```sh
   cd ./VSCode_Extension/secretscanner/
   ```
2. Install the extension through
  ```sh
   npm install
   ```

#### How to Use
Once installed in VSCode create or open a file, press 

Mac:
`cmd + Shift + p `

Windows:
`ctrl + Shift + p `

then run the command 'Scan for Secrets' in the dropdown

#### How to Configure
##### Syncing with the allowlist:
The 'allowlist_url' should contain your organisation's allowlist url to fetch the allowlist  
It can be extended to recognise more secret types.  

To sync for the current repository, update the allowlist_url with the allowlist endpoint + '/allowlist/get_list/' the repo name (Created when the secret review report is generated below) in `src/config.json` in the following format.

The allow list endpoint can be found once you generate the secret review report and running `terraform output`.
Image of the screenshot of the url output from secret review report.

![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911929609686237184/unknown.png)

screenshot of src/config.json
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911929245268340776/unknown.png)

With the allow list repo inside, this should pull from the allowlist
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911939075316006912/unknown.png)


##### Adding additional regex to be matched
In the `src/config.json` file, add more regex entries to the rules array.  
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911929245268340776/unknown.png)
'regex' is the regular expression to detect the secret type.  
'description' will be shown when the user is hovering over the secret.
<p align="right">(<a href="#top">back to top</a>)</p>

### **Pre-commit Hook**
The pre-commit hook runs everytime a commit is made and scans for any hardcoded secrets. 
The pre-commit hook is initially stored on our repository. However, it can be moved to your repository and installed to be used. 

To install on your personal repository
1.  Install [git-leaks](https://github.com/zricethezav/gitleaks) 
2.  Install [pre-commit](https://pre-commit.com/)
3.  Navigate to the root directory of the Seek-Rats repository
4. Move the pre-commit_config.yaml to the root of your desired repository
`mv pre-commit_config.yaml your_repo_root/`
5. Move the Pre-commit_Hook/gitleaks_checker.py/ to the root of your desired repository
`mv Pre-commit_Hook/gitleaks_checker.py your_repo_root/`
6. Rename the pre-commit_config.yaml file with a . at the front. This enables it to be read by the precommit hook
`mv pre-commit_config.yaml .pre-commit_config.yaml`
8. Run `pre-commit install` which sets up the pre commit in your repo
9. Run `pre commit run` to test the hook before execution

If there are no problems your hook has been set up using gitleaks everytime you run a commit.

**Identified errors:**
In the event like `no module named 'requests`',   try running the following line
 `pip install --target . requests`

**Syncing with the allowlist:**

Similar to the VSCode plugin, simply edit the url to be the same as  found in the `gitleaks_checker.py`which is originally found in `Pre-commit_Hook/gitleaks_checker.py`

The allow list endpoint can be found once you generate the secret review report and running `terraform output`.
Image of the screenshot of the url output from secret review report. (Image of the end point below)

![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911929609686237184/unknown.png)

![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911945500922617886/unknown.png)

<p align="right">(<a href="#top">back to top</a>)</p>

### **Secrets Code Review Report** 
The secrets code review report is hosted on AWS and interacts with GitHub Application. For these steps, please ensure you have AWS credentials set up as well as a GitHub account to create a GitHub Application.

Once the infrastructure is built, just add your GitHub application to any repository and (optional) enable checks and reviewers to be completed before a pull for best performance (This requires GitHub Teams/Pro).

As our secrets code review report backend is serverless, the following steps below outline how to install our infrastructure to your AWS services and GitHub Repository.

The following steps 
 1. Firstly, install [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) if you haven't already
2. Navigate to the terraform directory
  ```sh
   cd ./terraform/
   ```
3. Run the following commands and respond 'yes' when prompted
  ```sh
   terraform init
   terraform apply
   ```
Once created, you should be prompted with a list of endpoints. This is needed as  we will use this to store in our GitHub Application
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911907657114345502/unknown.png)
 
4. Open up [GitHub and navigate to create a new application.](https://docs.github.com/en/developers/apps/building-github-apps/creating-a-github-app)
 -  In your GitHub App, do the following steps:
     - For Homepage URL, you can do whatever you want as this will not be used.
	 - Put the `website_bucket_end` in the Callback URL. **After doing this place http:// at the start. This is crucial as the OAUTH redirect won't work if not done**
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911908415771660369/unknown.png)
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911908564916912128/unknown.png)
	 - Put the `gh_webhook_listener_endpoint` in the Webhook URL. **After doing this place / at the end. This is crucial as the webhook will not work if not done.**
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911909414431260703/unknown.png)
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911909719583637534/unknown.png)
	- After doing this, enable the following checks on your GitHub Application.
		- For Repository Permissions enable 
			- Contents - Read/Write
			- Issues - Read/Write
			- Metadata - Read Only
			- Pull Request - Read/Write
			- Webhooks - Read/Write
			- Commit Statuses - Read/Write
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911910393096593458/unknown.png)	
		- For Organisation Permissions enable 
			- Members - Read Only
			- Events - Read Only
			- Webhooks - Read/Write
		- User Permissions
			- None
		- Subscribe to Events
			- Pull Request
			- Pull Request Review Comment
			- Repository
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911911215117266964/unknown.png)

<p align="right">(<a href="#top">back to top</a>)</p>

5. Once you created your GitHub Application, we now have to store our GitHub secrets in Parameter Store so we can easily access them.
		 
	For the private key, generate the key with the 'Generate a private key' button and upload the whole private key including the headers to parameter store. The key should look like the image below.

  ```sh
aws ssm put-parameter --name "gitapp_PKey" --type "SecureString" --value "YOUR GITHUP APP PERSONAL KEY"
```   

![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911916776114237470/unknown.png)
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911917220312006657/unknown.png)
```sh
aws ssm put-parameter --name "gitapp_appID" --type "SecureString" --value "YOUR GITHUP APP ID"
```  
```sh
aws ssm put-parameter --name "gitapp_clientID" --type "SecureString" --value "YOUR GITHUP APP OAUTH CLIENT ID"
```   
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911915946585751582/unknown.png)

```sh
aws ssm put-parameter --name "gitapp_clientSecret" --type "SecureString" --value "YOUR GITHUP APP OAUTH CLIENT SECRET"
```   
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911915596269113354/unknown.png)

6. Navigate to the root directory of the seek rats repository and run the  create_client_id.py file

```sh
cd ../
python3 create_client_id.py
```  
7. Navigate to the Github_Bot/Webpage to build the s3 react site and sync it to the AWS S3 Bucket. 

	 seek-rats-site is the s3 bucket name in the 'website_bucket_end' variable. Screen shot of where you can find it is below.
```sh
cd ./Github_Bot/Webpage/reportfront
npm install
npm run build
aws s3 sync build s3://your-s3-bucket-name 
```  
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911922103891132466/unknown.png)

8. Navigate back to the terraform directory and run terraform apply one more time and reply yes
```sh
cd ../../../terraform/
terraform apply
```  

9. Now the secrets backend should be running. Install your application on any repository by going into GitHub Apps and choose a repository. 

 Seek Rats will now run on pull requests in that repository. (May take around 30-45 seconds to update)
![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911924390256574464/unknown.png)

11. (Optional) To enforce pull requests and checks, on a repository go to branches->branch protection rules and you may add a rule.

	If Seek-Rats has run atleast once your repository, you should be able to enable it in your checks (Named Secrets Review Needed)
	![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911924949634138174/unknown.png?width=1091&height=642)

	![enter image description here](https://media.discordapp.net/attachments/894590864242905199/911925078881632256/unknown.png?width=791&height=643)

<!-- USAGE EXAMPLES -->
## Usage


[How To Use Secrets Code Review DEMO](https://youtu.be/N2JpZoPHDUE)

[Pre Commit Hook DEMO](https://youtu.be/rH2Lej9xyKc)

[VSCODE Extension DEMO](https://youtu.be/XdT3u0a3ZKI)

