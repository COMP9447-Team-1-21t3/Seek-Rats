import boto3


def validateID(function):
	"""[summary]

	Args:
		function ([type]): [description]
	"""

	def functionWrapper(repo_id, *args, **kwargs):
		if not repo_id :
			raise ValueError("repo_id cannot be None")
		tableName = f'allowList_repo_{repo_id}'
		return function(str(repo_id), *args, **kwargs)

	return functionWrapper

