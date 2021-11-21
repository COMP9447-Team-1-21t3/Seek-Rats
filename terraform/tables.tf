resource "aws_dynamodb_table" "tracking_db" {
  name           = "tracking"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "reportURL"
  range_key      = "reviewerID"

  attribute {
    name = "reportURL"
    type = "S"
  }

  attribute {
    name = "reviewerID"
    type = "S"
  }
}

resource "aws_dynamodb_table" "secrets_db" {
  name           = "secret"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "reportURL"
  range_key      = "secretNum"

  attribute {
    name = "reportURL"
    type = "S"
  }

  attribute {
    name = "secretNum"
    type = "S"
  }
}