resource "random_pet" "lambda_bucket_name" {
  prefix = "skrts-report"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = random_pet.lambda_bucket_name.id

  acl           = "private"
  force_destroy = true
}

data "archive_file" "skrts_report_server_zip" {
  type = "zip"

  source_dir  = "${path.module}/../Github_Bot/skrts_report_server"
  output_path = "${path.module}/../Github_Bot/skrts_report_server.zip"
}

resource "aws_s3_bucket_object" "seek_rats_server" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "skrts_report_server.zip"
  source = data.archive_file.skrts_report_server_zip.output_path

  etag = filemd5(data.archive_file.skrts_report_server_zip.output_path)
}

resource "aws_lambda_function" "skrts_report_server_lambda" {
  function_name = "SeekRatsReportServer"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_bucket_object.seek_rats_server.key

  runtime = "python3.8"
  handler = "seek_rats_server.lambda_handler"

  source_code_hash = data.archive_file.skrts_report_server_zip.output_base64sha256

  role = aws_iam_role.lambda_exec_skrts_server.arn

  layers = [
    aws_lambda_layer_version.status_tracking_CRUD_python38.arn, 
    aws_lambda_layer_version.generateToken_python38.arn
  ]

  timeout = 10
}

resource "aws_cloudwatch_log_group" "skrts_report_server" {
  name = "/aws/lambda/${aws_lambda_function.skrts_report_server_lambda.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_apigatewayv2_api" "lambda" {
  name          = "seekrats_reportbackendapi_lambda"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda" {
  api_id = aws_apigatewayv2_api.lambda.id

  name        = "serverless_lambda_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw.arn

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

resource "local_file" "skrts_report_server_data" {
    content  = aws_apigatewayv2_stage.lambda.invoke_url
    filename = "${path.module}/../Github_Bot/Webpage/reportfront/src/components/server_api_url.txt"
}

resource "aws_apigatewayv2_integration" "skrts_report_server" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.skrts_report_server_lambda.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "skrts_report_server" {
  api_id = aws_apigatewayv2_api.lambda.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.skrts_report_server.id}"
}

resource "aws_cloudwatch_log_group" "api_gw" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.skrts_report_server_lambda.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}

output "server_api_endpoint" {
  value = aws_apigatewayv2_stage.lambda.invoke_url
}

resource "aws_iam_role" "lambda_exec_skrts_server" {
  name = "skrts_server"

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

resource "aws_iam_role_policy_attachment" "skrts_server_webhook_basicexecute" {
  role       = aws_iam_role.lambda_exec_skrts_server.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "skrts_server_role_secret_access" {
  role       = "${aws_iam_role.lambda_exec_skrts_server.name}"
  policy_arn = "${aws_iam_policy.policy_secret_access.arn}"
}

resource "aws_iam_role_policy_attachment" "skrts_server_role_tracking_access" {
  role       = "${aws_iam_role.lambda_exec_skrts_server.name}"
  policy_arn = "${aws_iam_policy.policy_tracking_access.arn}"
}

resource "aws_iam_role_policy_attachment" "ssm_access_skrts_server" {
  role       = "${aws_iam_role.lambda_exec_skrts_server.name}"
  policy_arn = "${aws_iam_policy.policy.arn}"
}