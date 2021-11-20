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

  source_dir  = "${path.module}/../Github_Bot/skrts_report_updater"
  output_path = "${path.module}/../Github_Bot/skrts_report_updater.zip"
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

  runtime = "python3.8"
  handler = "report_updater.lambda_handler"

  source_code_hash = data.archive_file.skrts_report_updater.output_base64sha256

  role = aws_iam_role.lambda_exec.arn

  layers = [
    aws_lambda_layer_version.status_tracking_CRUD_python38.arn, 
    aws_lambda_layer_version.generateToken_python38.arn,
    aws_lambda_layer_version.modifyTables_python38.arn
  ]

  timeout = 10
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
    filename = "${path.module}/../Github_Bot/Webpage/reportfront/src/components/update_api_url.txt"
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

output "report_updater_api_endpoint" {
  value = aws_apigatewayv2_stage.lambda_updater.invoke_url
}
