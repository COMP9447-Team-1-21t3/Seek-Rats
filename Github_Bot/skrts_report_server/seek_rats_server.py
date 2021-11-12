import json

def lambda_handler(event, context):
    
    secrets = [{"secret":"test", "type":"Unknown Secret","location":"line 2 app.py", "code_location": "minecraft_seed = -test", "id":"1"}, 
  {"secret":"test", "type":"API Secret","location":"line 10 app.py", "code_location": "api_key= test", "id":"2"}]

    headers = {
      'Content-Type': 'application/json',
      "Access-Control-Allow-Origin" : "*"
      
    }

    return {
        'statusCode': 200,
        'body': json.dumps(secrets),
        'headers': headers
    }
