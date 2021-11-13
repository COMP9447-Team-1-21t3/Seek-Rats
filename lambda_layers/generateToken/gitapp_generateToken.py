import jwt
import requests
import time
try:
	from gitapp_generateToken_helpers import get_parameter
except ImportError:
	from generateToken.gitapp_generateToken_helpers import get_parameter

cert_str = get_parameter("gitapp_PKey").get("Parameter").get("Value")
app_id = get_parameter("gitapp_appID").get("Parameter").get("Value")

def generate_jwt_headers():
	"""
		Summary: Generates the headers for a JWT token that will expire in 3 mins
	"""
	seconds= int(time.time())
	cert_bytes= cert_str.encode()

	payload = {
		# issued at time, 60 seconds in the past to allow for clock drift
		'iat': seconds - 60,
		# JWT expiration time (3 minute maximum)
		'exp': seconds + (3 * 60),
		# GitHub App's identifier
		'iss': app_id
	}

	a_jwt = jwt.encode(payload, cert_bytes, algorithm='RS256')

	headers = {
		"Authorization": f"Bearer {a_jwt}", 
		"Accept": "application/vnd.github.machine-man-preview+json"
	}
	return headers

def generate_token_header(token):
	headers = {
		"Authorization": f"token {token}",
        "Accept": "application/vnd.github.machine-man-preview+json"
	}
	return headers

def generate_token(owner, repo):
	"""
	"""
	headers=generate_jwt_headers()
	response = requests.get(
		f'https://api.github.com/repos/{owner}/{repo}/installation',
		headers=headers
	)
	acc_tok_url = response.json()['access_tokens_url']
	response = requests.post(acc_tok_url, headers=headers)
	token = response.json()['token']
	return token

def get_ids(owner, repo):
	token = generate_token(owner, repo)
	response = requests.get(
        "https://api.github.com/installation/repositories",
        headers=generate_token_header(token)
    )
	if int(response.status_code) >= 300 :
		raise ValueError("Application does not have access to repo")
	to_return = {
		'repo_id':response.json()['repositories'][0]['id'],
		'org_id':response.json()['repositories'][0]['owner']['id']
	}
	return to_return
