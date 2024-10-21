


variable "region" {
  description = "AWS Region"
  type        = string
}

variable "functions" {
  description = "List of functions"
  type        = list(object({
    name                     = string
    handler                  = string
    runtime                  = string
    archive                  = string
    memory                   = number
    timeout                  = number
    concurrency = number
    repetition =number
    inputFiles               = list(string)
    additional_input_params   = list(object({
      name  = string
      type  = string
      value = string
    }))
    additional_output_params  = list(object({
      name = string
      type = string
    }))
    useOutputBucket          = bool

  }))
}

resource "random_id" "region" {
  byte_length = 8
}

data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

resource "aws_s3_bucket" "deployment_bucket" {
  bucket        = "deployment-packages-${var.region}-${random_id.region.hex}"
  force_destroy = true
}

resource "aws_s3_bucket" "bucket" {
  count = length([for func in var.functions : func if (length(func.inputFiles) > 0) || (func.useOutputBucket == true)]) ? 1 : 0
  bucket        = "bucket_benchmarking_tool_profile_BaaS-${var.region}"
  force_destroy = true
}

locals {

  function_input_files = flatten([
    for func in var.functions : [
      for file in func.inputFiles : {
        func_name  = func.name
        file_name  = basename(file)
        file_path  = file
      }
    ]
  ])
}

resource "aws_s3_object" "input_files" {
  for_each = { for idx, file in local.function_input_files : "${file.func_name}-${file.file_name}" => file }

  bucket = aws_s3_bucket.bucket[0].id
  key    = each.value.file_name
  source = each.value.file_path
  acl    = "private"
}

resource "aws_s3_object" "deployment_packages" {
  for_each = { for function in var.functions : function.name => function }

  bucket = aws_s3_bucket.deployment_bucket.id

  key    = "${each.key}.${endswith(each.value.archive, ".jar") ? "jar" : "zip"}"
  acl    = "private"
  source = "${each.value.archive}"
  etag   = filemd5("${each.value.archive}")
}

resource "aws_lambda_function" "lambda_functions" {
  for_each = { for function in var.functions : function.name => function }

  function_name    = each.key
  s3_bucket        = aws_s3_object.deployment_packages[each.key].bucket
  s3_key           = aws_s3_object.deployment_packages[each.key].key
  runtime          = each.value.runtime
  handler          = each.value.handler
  source_code_hash = filebase64sha256(aws_s3_object.deployment_packages[each.key].source)
  role             = data.aws_iam_role.lab_role.arn
  timeout          = each.value.timeout
  memory_size      = each.value.memory

  ephemeral_storage {
    size = 512
  }
}

module "workflow" {
  source = "../workflow_module"
  for_each = { for func in var.functions: func.name => func }
  inputBucketFileAddress = length(aws_s3_bucket.bucket) > 0 ? "https://${aws_s3_bucket.bucket[0].bucket}.s3.amazonaws.com/":""


  additional_input_params = each.value.additional_input_params
  additional_output_params = each.value.additional_output_params
  funcName = each.key
  funcUrl = aws_lambda_function.lambda_functions[each.key].arn
  prov = "AWS"
  region = var.region
  useOutPutBucket = each.value.useOutputBucket
  inputFiles = [for file in each.value.inputFiles : basename(file)]
  concurrency = each.value.concurrency
  repetition = each.value.repetition
}
