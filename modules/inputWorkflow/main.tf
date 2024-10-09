

variable "prov" {}

variable "region" {}

variable "inputBucketFileAddress" {}

variable "concurrency" {}

variable "repetition" {}

variable "inputFiles" {}

variable "useOutPutBucket" {}
variable "jsonPath" {}

variable "additional_input_params" {
  type = list(object({
    name  = string
    type  = string
    value = string
  }))
}


locals {
  modified_json = merge(
    {
      region = jsonencode(var.region)
      provider = jsonencode(var.prov)
      concurrency = var.concurrency
      repetition = var.repetition
    },
    {
      for param in var.additional_input_params :
      param.name => param.value
    },
    {
      for file in var.inputFiles :
      split(".", file)[0] => jsonencode("${var.inputBucketFileAddress}/${file}")
    },
    {
      outputBucket = var.useOutPutBucket ? jsonencode("${var.inputBucketFileAddress}/") : jsonencode(false)
    }
  )
}
resource "local_file" "inputFile" {
  filename   = var.jsonPath
  content    = jsonencode(local.modified_json)
}
