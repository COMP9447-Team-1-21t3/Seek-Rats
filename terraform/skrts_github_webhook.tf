resource "random_pet" "lambda_bucket_name_github_webhook" {
  prefix = "skrts-github-webhook"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket_github_webhook" {
  bucket = random_pet.lambda_bucket_name_github_webhook.id

  acl           = "private"
  force_destroy = true
}

data "archive_file" "skrts_github_webhook" {
  type = "zip"

  source_dir  = "${path.module}/../skrts_github_webhook"
  output_path = "${path.module}/../skrts_github_webhook.zip"
}

resource "aws_s3_bucket_object" "seek_rats_github_webhook" {
  bucket = aws_s3_bucket.lambda_bucket_github_webhook.id

  key    = "skrts_github_webhook.zip"
  source = data.archive_file.skrts_github_webhook.output_path

  etag = filemd5(data.archive_file.skrts_github_webhook.output_path)
}

resource "aws_lambda_function" "skrts_github_webhook" {
  function_name = "GHWebhookListener"

  s3_bucket = aws_s3_bucket.lambda_bucket_github_webhook.id
  s3_key    = aws_s3_bucket_object.seek_rats_github_webhook.key

  runtime = "python3.8"
  handler = "skrts_webhook_listener.lambda_handler"

  source_code_hash = data.archive_file.skrts_github_webhook.output_base64sha256

  role = aws_iam_role.lambda_exec_webhook.arn

  layers = [
    aws_lambda_layer_version.status_tracking_CRUD_python38.arn, 
    aws_lambda_layer_version.generateToken_python38.arn,
    aws_lambda_layer_version.modifyTables_python38.arn
  ]

  timeout = 10
}

resource "aws_cloudwatch_log_group" "skrts_github_webhook" {
  name = "/aws/lambda/${aws_lambda_function.skrts_github_webhook.function_name}"

  retention_in_days = 30
}

resource "aws_apigatewayv2_api" "lambda_gh_webhook_listener" {
  name          = "seekrats_gh_webhook_listener_api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda_gh_webhook_listener" {
  api_id = aws_apigatewayv2_api.lambda_gh_webhook_listener.id

  name        = "serverless_lambda_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gh_listener.arn
      format = jsonencode({
      requestId               = "$context.requestId"
      sourceIp                = "$context.identity.sourceIp"
      requestTime             = "$context.requestTime"
      protocol                = "$context.protocol"
      httpMethod              = "$context.httpMethod"
      resourcePath            = "$context.resourcePath"
      routeKey                = "$context.routeKey"
      status                  = "$context.status"
      responseLength          = "$context.responseLength"
      integrationErrorMessage = "$context.integrationErrorMessage"
      }
    )
  }
}

resource "aws_apigatewayv2_integration" "skrts_gh_listener" {
  api_id = aws_apigatewayv2_api.lambda_gh_webhook_listener.id

  integration_uri    = aws_lambda_function.skrts_github_webhook.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "skrts_gh_listener" {
  api_id = aws_apigatewayv2_api.lambda_gh_webhook_listener.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.skrts_gh_listener.id}"
}

resource "aws_cloudwatch_log_group" "api_gh_listener" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda_gh_webhook_listener.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "lambda_gw_listener" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.skrts_github_webhook.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda_gh_webhook_listener.execution_arn}/*/*"
}

output "gh_webhook_listener_endpoint" {
  value = aws_apigatewayv2_stage.lambda_gh_webhook_listener.invoke_url
}

resource "aws_iam_role" "lambda_exec_webhook" {
  name = "gh_exec_webhook"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_exec_webhook_basicexecute" {
  role       = aws_iam_role.lambda_exec_webhook.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "github_webhook_role_secret_access" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy_secret_access.arn}"
}

resource "aws_iam_role_policy_attachment" "github_webhook_role_tracking_access" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy_tracking_access.arn}"
}

resource "aws_iam_role_policy_attachment" "github_webhook_allowlist_access" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy_allowlist_access.arn}"
}

resource "aws_iam_role_policy_attachment" "ssm_access_gh_webhook" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy.arn}"
}

resource "aws_iam_role_policy_attachment" "gh_wh_allowlist_createDynamo" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy_allowlist_createDynamo.arn}"
}

resource "aws_iam_role_policy_attachment" "gh_wh_policy_allowlist_setupRepo" {
  role       = "${aws_iam_role.lambda_exec_webhook.name}"
  policy_arn = "${aws_iam_policy.policy_allowlist_setupRepo.arn}"
}