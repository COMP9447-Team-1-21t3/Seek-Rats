# Seek-Rats
![This is an image]()


> A comprehensive secret detection and management solution that unites Security Operations with Developer Operations.

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

## Github Bot
The webhook uses DynamoDB tables to track the status of pull requst reviews.\
The python file in /lambda_layers/status_tracking_CRUD/report_status_tracking.py is a function that defines the CRUD operations\
of the DynamoDB tables related to status tracking. This python file is designed to be zipped as a lambda layer for usage convenience.
