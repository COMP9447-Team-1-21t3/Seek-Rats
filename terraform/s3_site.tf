resource "random_pet" "seek_rats_site_updater" {
  prefix = "seek-rats-site"
  length = 2
}

resource "aws_s3_bucket" "seek_rats_site" {
  bucket = random_pet.seek_rats_site_updater.id
  acl    = "public-read"

  website {
      index_document = "index.html"
      error_document = "index.html"
  }
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = aws_s3_bucket.seek_rats_site.id
  policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
      {
          Sid       = "PublicReadGetObject"
          Effect    = "Allow"
          Principal = "*"
          Action    = "s3:GetObject"
          Resource = [
          aws_s3_bucket.seek_rats_site.arn,
          "${aws_s3_bucket.seek_rats_site.arn}/*",
          ]
      },
      ]
  })
}

output "website_bucket_end" {
  value = aws_s3_bucket.seek_rats_site.website_endpoint
}

resource "local_file" "website_bucket_endpoint_webhook" {
    content  = aws_s3_bucket.seek_rats_site.website_endpoint
    filename = "${path.module}/../skrts_github_webhook/config.txt"
}

resource "local_file" "website_bucket_endpoint_updater" {
    content  = aws_s3_bucket.seek_rats_site.website_endpoint
    filename = "${path.module}/../Github_Bot/skrts_github_updater/config.txt"
}