resource "random_pet" "lambda_bucket_allow_list_get_url" {
  prefix = "skrts-report-updater"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket_allow_list_get_url" {
  bucket = random_pet.lambda_bucket_allow_list_get_url.id

  acl           = "private"
  force_destroy = true
}

data "archive_file" "skrts_allow_list_get_url" {
  type = "zip"

  source_dir  = "${path.module}/../allowList/lambda_functions/add_terms_with_info"
  output_path = "${path.module}/../allowList/lambda_functions/add_terms_with_info.zip"
}

resource "aws_s3_bucket_object" "seek_rats_allow_list_get_url" {
  bucket = aws_s3_bucket.lambda_bucket_allow_list_get_url.id

  key    = "seek_rats_allow_list_get_url.zip"
  source = data.archive_file.skrts_allow_list_get_url.output_path

  etag = filemd5(data.archive_file.skrts_allow_list_get_url.output_path)
}

resource "aws_lambda_function" "seek_rats_allow_list_get_url_lambda_function" {
  function_name = "allowlist_get_list_from_url"

  s3_bucket = aws_s3_bucket.lambda_bucket_allow_list_get_url.id
  s3_key    = aws_s3_bucket_object.seek_rats_allow_list_get_url.key

  runtime = "python3.8"
  handler = "allowlist_add_terms_with_info.lambda_handler"

  source_code_hash = data.archive_file.skrts_allow_list_get_url.output_base64sha256

  role = aws_iam_role.lambda_exec_allowlist_url.arn

  layers = [
    aws_lambda_layer_version.generateToken_python38.arn,
    aws_lambda_layer_version.modifyTables_python38.arn
  ]

  timeout = 10
}

resource "aws_cloudwatch_log_group" "skrts_allow_list_get_url" {
  name = "/aws/lambda/${aws_lambda_function.seek_rats_allow_list_get_url_lambda_function.function_name}"

  retention_in_days = 30
}

resource "aws_apigatewayv2_api" "lambda_allow_list_get_url" {
  name          = "skrts_allow_list_get_url"
  protocol_type = "HTTP"
}


resource "aws_cloudwatch_log_group" "api_gw_allowlist_get_url" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda_allow_list_get_url.name}"

  retention_in_days = 30
}


resource "aws_apigatewayv2_stage" "lambda_allow_list_get_url" {
  api_id = aws_apigatewayv2_api.lambda_allow_list_get_url.id

  name        = "serverless_lambda_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw_allowlist_get_url.arn

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

resource "aws_apigatewayv2_integration" "skrts_api_gateway_integrate_allowlist_url" {
  api_id = aws_apigatewayv2_api.lambda_allow_list_get_url.id

  integration_uri    = aws_lambda_function.seek_rats_allow_list_get_url_lambda_function.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "skrts_allowlist_url_route" {
  api_id = aws_apigatewayv2_api.lambda_allow_list_get_url.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.skrts_api_gateway_integrate_allowlist_url.id}"
}

resource "aws_lambda_permission" "api_allowlist_url" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.seek_rats_allow_list_get_url_lambda_function.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda_allow_list_get_url.execution_arn}/*/*"
}

output "allowlist_update_url_api_endpoint" {
  value = aws_apigatewayv2_stage.lambda_allow_list_get_url.invoke_url
}

resource "aws_iam_role" "lambda_exec_allowlist_url" {
  name = "allowlist_get_from_url"

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

resource "aws_iam_role_policy_attachment" "allowlist_url_webhook_basicexecute" {
  role       = "${aws_iam_role.lambda_exec_allowlist_url.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "allowlist_url_policy_allowlist_access" {
  role       = "${aws_iam_role.lambda_exec_allowlist_url.name}"
  policy_arn = "${aws_iam_policy.policy_allowlist_access.arn}"
}
