
resource "aws_ssm_parameter" "secret" {
  name        = "gitapp_PKey"
  type        = "SecureString"
  value       = var.gitapp_privateKey
}

resource "aws_ssm_parameter" "secret" {
  name        = "gitapp_appID"
  type        = "String"
  value       = var.gitapp_appID
}

resource "aws_ssm_parameter" "secret" {
  name        = "gitapp_clientID"
  type        = "SecureString"
  value       = var.gitapp_clientID
}

resource "aws_ssm_parameter" "secret" {
  name        = "gitapp_clientSecret"
  type        = "SecureString"
  value       = var.gitapp_clientSecret
}
