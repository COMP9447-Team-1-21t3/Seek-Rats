data "aws_caller_identity" "current" {}

locals {
  aws-account-id = data.aws_caller_identity.current.account_id
}

output "aws-account_id" {
  value = local.aws-account-id
}


resource "aws_iam_policy" "policy_allowlist_readAndDelete" {
  name        = "allowlist_readAndDelete"
  path        = "/"
  description = "A policy that allows a resource to read from dynamoDB and delete from it only if the tables name starts with allowlist_organization_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "dynamodb:Query",
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*/index/*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:BatchWriteItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query"
                ],
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*"
            }
        ]
    }
  )
}

resource "aws_iam_policy" "policy_allowlist_access" {
  name        = "allowlist_accessPolicy"
  path        = "/"
  description = "An access policy for allowlist lambda functions, which need to be able to access any tables with the prefix allowlist_organization_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:BatchWriteItem",
                    "dynamodb:PutItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:UpdateItem"
                ],
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": "dynamodb:Query",
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*/index/*"
            }
        ]
    }
  )
}

resource "aws_iam_policy" "policy_allowlist_createDynamo" {
  name        = "allowlist_createDynamoDBTable"
  path        = "/"
  description = "A policy that allows a resource to create a dynamoDB table with a name like allowlist_organization_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "dynamodb:CreateTable",
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*"
            }
        ]
    }
  )
}

resource "aws_iam_policy" "policy_allowlist_setupRepo" {
  name        = "allowlist_setupRepo"
  path        = "/"
  description = "A policy to allow a resource to access dynamoDB to query it and putitem, only if the name of the database these operations are on begins with allowlist_organization_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "dynamodb:Query",
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*/index/*"
            },
            {
                "Sid": "VisualEditor1",
                "Effect": "Allow",
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:Query"
                ],
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*"
            }
        ]
    }
  )
}

resource "aws_iam_policy" "policy_allowlist_deleteTable" {
  name        = "allowlist_deleteTable"
  path        = "/"
  description = "A policy to allow a resource to access dynamoDB and delete tables with names like allowlist_organization_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "dynamodb:DeleteTable",
                "Resource": "arn:aws:dynamodb:*:${local.aws-account-id}:table/allowlist_organization_*"
            }
        ]
    }
  )
}


resource "aws_iam_policy" "policy" {
  name        = "gitApp_accessParamStore"
  path        = "/"
  description = "Allows resource to access parameters from SSM that start with gitapp_"

  policy = jsonencode(
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "VisualEditor0",
                "Effect": "Allow",
                "Action": "ssm:GetParameter",
                "Resource": "arn:aws:ssm:*:${local.aws-account-id}:parameter/gitapp_*"
            }
        ]
    }
  )
}
