output "lambda_bucket_name" {
  description = "Bucket Id"
  value       = aws_s3_bucket.lambda_bucket.id
}
