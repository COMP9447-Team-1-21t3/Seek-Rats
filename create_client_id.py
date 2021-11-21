import os
import subprocess
import json
import boto3


loc = os.getcwd() 

ssm = boto3.client("ssm")

client_id = ssm.get_parameter(Name='gitapp_clientID', WithDecryption=True)

temp_json = {}

temp_json['client'] = client_id["Parameter"]["Value"]

print(temp_json)
data = temp_json

with open(loc+"/Github_Bot/Webpage/reportfront/src/components/client_id.json", 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)