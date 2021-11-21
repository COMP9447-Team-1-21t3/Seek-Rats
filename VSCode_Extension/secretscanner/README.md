# VS Code extension

This VS Code extension adds a command to your editor that when run will scan the current file for any hard coded secrets\
Hard coded secrets that are found will be highlighted\
When you hover over a highlighted secret with your cursor, information about the secret will be displayed



## How to run

To try this extension out locally, in this directory, first run `npm install`\
Then press F5 to enter debug mode\
Create or open a file, press `cmd + Shift + p` and run the command 'Scan for Secrets' in the dropdown

## How to configure
The 'allowlist_url' should contain your organisation's allowlist url to fetch the allowlist\
It can be extended to recognise more secret types.\
In the `src/config.json` file, add more entries to the rules array.\
'regex' is the regular expression to detect the secret type.\
'description' will be shown when the user is hovering over the secret.
