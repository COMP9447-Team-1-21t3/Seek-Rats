terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

resource "random_pet" "lambda_bucket_name" {
  prefix = "skrts-report"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = random_pet.lambda_bucket_name.id

  acl           = "private"
  force_destroy = true
}

data "archive_file" "skrts_report_server" {
  type = "zip"

  source_dir  = "${path.module}/skrts_report_server"
  output_path = "${path.module}/skrts_report_server.zip"
}

provider "aws" {
  profile = "default"
  region  = "ap-southeast-2"
}

resource "aws_s3_bucket_object" "seek_rats_server" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "skrts_report_server.zip"
  source = data.archive_file.skrts_report_server.output_path

  etag = filemd5(data.archive_file.skrts_report_server.output_path)
}

resource "aws_lambda_function" "skrts_report_server" {
  function_name = "SeekRatsReportServer"

  s3_bucket = aws_s3_bucket.lambda_bucket.id
  s3_key    = aws_s3_bucket_object.seek_rats_server.key

  runtime = "python3.9"
  handler = "seek_rats_server.lambda_handler"

  source_code_hash = data.archive_file.skrts_report_server.output_base64sha256

  role = aws_iam_role.lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "skrts_report_server" {
  name = "/aws/lambda/${aws_lambda_function.skrts_report_server.function_name}"

  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

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
    filename = "${path.module}/Webpage/reportfront/src/components/config.txt"
}

resource "aws_apigatewayv2_integration" "skrts_report_server" {
  api_id = aws_apigatewayv2_api.lambda.id

  integration_uri    = aws_lambda_function.skrts_report_server.invoke_arn
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
  function_name = aws_lambda_function.skrts_report_server.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda.execution_arn}/*/*"
}








resource "random_pet" "lambda_bucket_name_updater" {
  prefix = "skrts-report-updater"
  length = 4
}

resource "aws_s3_bucket" "lambda_bucket_updater" {
  bucket = random_pet.lambda_bucket_name_updater.id

  acl           = "private"
  force_destroy = true
}

data "archive_file" "skrts_report_updater" {
  type = "zip"

  source_dir  = "${path.module}/skrts_report_updater"
  output_path = "${path.module}/skrts_report_updater.zip"
}

resource "aws_s3_bucket_object" "seek_rats_report_updater" {
  bucket = aws_s3_bucket.lambda_bucket_updater.id

  key    = "skrts_report_updater.zip"
  source = data.archive_file.skrts_report_updater.output_path

  etag = filemd5(data.archive_file.skrts_report_updater.output_path)
}


resource "aws_lambda_function" "skrts_report_updater" {
  function_name = "SeekRatsReportUpdater"

  s3_bucket = aws_s3_bucket.lambda_bucket_updater.id
  s3_key    = aws_s3_bucket_object.seek_rats_report_updater.key

  runtime = "python3.9"
  handler = "report_updater.lambda_handler"

  source_code_hash = data.archive_file.skrts_report_updater.output_base64sha256

  role = aws_iam_role.lambda_exec.arn
}

resource "aws_cloudwatch_log_group" "skrts_report_updater" {
  name = "/aws/lambda/${aws_lambda_function.skrts_report_updater.function_name}"

  retention_in_days = 30
}

resource "aws_apigatewayv2_api" "lambda_updater" {
  name          = "seekrats_reportupdater_api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "lambda_updater" {
  api_id = aws_apigatewayv2_api.lambda_updater.id

  name        = "serverless_lambda_stage"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gw_updater.arn

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

resource "local_file" "skrts_report_updater_file" {
    content  = aws_apigatewayv2_stage.lambda_updater.invoke_url
    filename = "${path.module}/Webpage/reportfront/src/components/config2.txt"
}

resource "aws_apigatewayv2_integration" "skrts_report_updater" {
  api_id = aws_apigatewayv2_api.lambda_updater.id

  integration_uri    = aws_lambda_function.skrts_report_updater.invoke_arn
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
}

resource "aws_apigatewayv2_route" "skrts_report_updater" {
  api_id = aws_apigatewayv2_api.lambda_updater.id

  route_key = "ANY /"
  target    = "integrations/${aws_apigatewayv2_integration.skrts_report_updater.id}"
}

resource "aws_cloudwatch_log_group" "api_gw_updater" {
  name = "/aws/api_gw/${aws_apigatewayv2_api.lambda_updater.name}"

  retention_in_days = 30
}

resource "aws_lambda_permission" "api_gw_updater" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.skrts_report_updater.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.lambda_updater.execution_arn}/*/*"
}