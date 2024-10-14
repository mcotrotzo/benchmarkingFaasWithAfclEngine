


variable "region" {
  description = "GCP Region"
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



resource "google_storage_bucket" "deployment_bucket" {
  name          = "deployment-packages-${var.region}-${random_id.region.hex}"
  location      = var.region
  force_destroy = true
}

resource "google_storage_bucket" "input_file_test_bucket" {
  count = length([for func in var.functions : func if length(func.inputFiles) > 0]) > 0 ? 1 : 0
  name          = "inputfilestestbucket-${var.region}${random_id.region.hex}"
  location      = var.region
  force_destroy = true
}

locals {

  input_files = flatten([
    for func in var.functions : [
      for file in func.inputFiles : {
        func_name  = func.name
        file_name  = basename(file)
        file_path  = file
      }
    ]
  ])
}

resource "google_storage_bucket_object" "input_files" {
  for_each = { for idx, file in local.input_files : "${file.func_name}-${file.file_name}" => file }

  bucket = google_storage_bucket.input_file_test_bucket[0].name
  name   = each.value.file_name
  source = each.value.file_path

  timeouts {
    create = "60m"
    update = "60m"
    delete = "60m"
  }
}

data "archive_file" "function_deployment_package" {
  for_each = {
    for func in var.functions :
    func.name => func
    if !endswith(func.archive, ".zip")
  }

  type        = "zip"
  source_file = "${abspath(path.root)}/${each.value.archive}"
  output_path = "${abspath(path.root)}/${trimsuffix(each.value.archive, ".jar")}.zip"
}

resource "google_storage_bucket_object" "deployment_packages" {
  for_each = { for func in var.functions : func.name => func }

  bucket = google_storage_bucket.deployment_bucket.name
  name   = "${each.key}.zip"
  source = endswith(each.value.archive, ".zip") ? "${abspath(path.root)}/${each.value.archive}" : data.archive_file.function_deployment_package[each.key].output_path

  timeouts {
    create = "60m"
    update = "60m"
    delete = "60m"
  }
}

resource "google_cloudfunctions_function" "lambda_functions" {
  for_each = { for func in var.functions : func.name => func }

  name                  = each.key
  runtime               = each.value.runtime
  available_memory_mb   = each.value.memory
  source_archive_bucket = google_storage_bucket.deployment_bucket.name
  source_archive_object = google_storage_bucket_object.deployment_packages[each.key].name
  trigger_http          = true
  entry_point           = each.value.handler
  timeout               = each.value.timeout
}

resource "google_cloudfunctions_function_iam_member" "invoker" {
  for_each = google_cloudfunctions_function.lambda_functions

  project        = each.value.project
  region         = var.region
  cloud_function = each.value.name
  role           = "roles/cloudfunctions.invoker"
  member         = "allUsers"
}

output "function_urls" {
  value = { for func in google_cloudfunctions_function.lambda_functions : func.name => func.https_trigger_url }
}

module "workflow" {
  source = "../workflow_module"
  for_each = { for func in var.functions : func.name => func }


  inputBucketFileAddress = "https://storage.cloud.google.com/${google_storage_bucket.input_file_test_bucket[0].name}"



  additional_input_params = each.value.additional_input_params
  additional_output_params = each.value.additional_output_params
  funcName                = each.key
  funcUrl                 = google_cloudfunctions_function.lambda_functions[each.key].https_trigger_url
  prov                    = "GCP"
  region                  = var.region
  useOutPutBucket         = each.value.useOutputBucket
  inputFiles              = [for file in each.value.inputFiles : basename(file)]
  concurrency = each.value.concurrency
  repetition = each.value.repetition
}
