resource "aws_lambda_layer_version" "modifyTables_python38" {
  filename   = "${path.module}/../lambda_layers/deployment_modifyTables.zip"
  layer_name = "modifyTables"

  compatible_runtimes = ["python3.8"]
}

resource "aws_lambda_layer_version" "generateToken_python38" {
  filename   = "${path.module}/../lambda_layers/deployment_generateToken.zip"
  layer_name = "generateToken"

  compatible_runtimes = ["python3.8"]
}

data "archive_file" "status_tracking_CRUD" {
  type = "zip"

  source_dir = "${path.module}/../lambda_layers/status_tracking_CRUD"
  output_path = "${path.module}/../lambda_layers/deployment_status_tracking.zip"
}

resource "aws_lambda_layer_version" "status_tracking_CRUD_python38" {
  filename   = data.archive_file.status_tracking_CRUD.output_path
  layer_name = "status_tracking_CRUD"

  compatible_runtimes = ["python3.8"]
}