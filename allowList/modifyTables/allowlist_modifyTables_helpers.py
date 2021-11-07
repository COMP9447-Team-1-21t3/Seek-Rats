import boto3

def validateID(function):
	def functionWrapper(org_id, *args, **kwargs):
		if not org_id :
			raise ValueError("org_id cannot be None")
		return function(org_id, *args, **kwargs)
	return functionWrapper

