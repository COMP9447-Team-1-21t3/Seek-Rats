
# resource "aws_ssm_parameter" "secret_gitapp_PKey" {
#   name        = "gitapp_PKey"
#   type        = "SecureString"
#   value       = var.gitapp_privateKey
# }

# resource "aws_ssm_parameter" "secret_gitapp_appID" {
#   name        = "gitapp_appID"
#   type        = "String"
#   value       = var.gitapp_appID
# }

# resource "aws_ssm_parameter" "secret_gitapp_clientID" {
#   name        = "gitapp_clientID"
#   type        = "SecureString"
#   value       = var.gitapp_clientID
# }

# resource "aws_ssm_parameter" "secret_gitapp_clientSecret" {
#   name        = "gitapp_clientSecret"
#   type        = "SecureString"
#   value       = var.gitapp_clientSecret
# }
