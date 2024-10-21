variable "prov" {}

variable "funcName" {}

variable "funcUrl" {}

variable "region" {}

variable "inputBucketFileAddress" {}
variable "concurrency" {}
variable "repetition" {}

variable "inputFiles" {

  type = list(string)
}


variable "additional_input_params" {
  type = list(object({
    name  = string
    type  = string
    value = string
  }))
}

variable "additional_output_params" {
  type = list(object({
    name = string
    type = string
  }))
}



variable "useOutPutBucket" {
  type = bool
}



locals {
  additional_inputs_input_section = join(
    "\n",
    [
      for param in var.additional_input_params :
      "- name: \"${param.name}\"\n  type: \"${param.type}\"\n  source: \"${param.name}\""
    ]
  )

  additional_inputs_parallel_input_section = join(
    "\n",
    [
      for param in var.additional_input_params :
      "    - name: \"${param.name}\"\n      type: \"${param.type}\"\n      source: \"${var.funcName}Experiment/${param.name}\"\n      constraints:\n      - name: \"distribution\"\n        value: \"REPLICATE(*)\""
    ]
  )

  additional_inputs_function_input_section = join(
    "\n",
    [
      for param in var.additional_input_params :
      "        - name: \"${param.name}\"\n          type: \"${param.type}\"\n          source: \"ParallelFor/${param.name}\"\n"
    ]
  )

  additional_outputs_function = join(
    "\n",
    [
      for param in var.additional_output_params :
      "          - name: \"${param.name}\"\n            type: \"${param.type}\"\n"
    ]
  )

  additional_outputs = join(
    "\n",
    [
      for param in var.additional_output_params :
      "      - name: \"${param.name}\"\n        type: \"collection\"\n        source: \"${var.funcName}/${param.name}\""
    ]
  )




}

locals {

  conditionalInputFile = (var.inputBucketFileAddress != "") && (var.inputBucketFileAddress != null) ? join("\n", [
    for file in var.inputFiles :
    "- name: \"${split(".", file)[0]}\"\n  type: \"string\"\n  source: \"${split(".", file)[0]}\""
  ]) : ""

  # Conditional output bucket (fixed multi-line and loop issues)
  conditionalOutputBucket = var.useOutPutBucket ? join("\n", [
    "- name: \"outputBucket\"",
    "  type: \"string\"",
    "  source: \"outputBucket\""
  ]) : ""

  conditionalParallelInputFile = (var.inputBucketFileAddress != "") && (var.inputBucketFileAddress != null) ? join("\n", [
    for file in var.inputFiles :
    "    - name: \"${split(".", file)[0]}\"\n      type: \"string\"\n      source: \"${var.funcName}Experiment/${split(".", file)[0]}\"\n      constraints:\n      - name: \"distribution\"\n        value: \"REPLICATE(*)\""
  ]) : ""

  conditionalFunntionInputFile = (var.inputBucketFileAddress != "") && (var.inputBucketFileAddress != null) ? join("\n", [
    for file in var.inputFiles :
    "        - name: \"${split(".", file)[0]}\"\n          type: \"string\"\n          source: \"ParallelFor/${split(".", file)[0]}\"\n"
  ]) : ""

  conditionalOutputBucketParallel = var.useOutPutBucket ? join("\n", [
    "    - name: \"outputBucket\"\n      type: \"string\"\n      source: \"${var.funcName}Experiment/outputBucket\"\n      constraints:\n      - name: \"distribution\"\n        value: \"REPLICATE(*)\""
  ]) : ""

  cconditionalOutputBucketFunction = var.useOutPutBucket ? join("\n", [
    "        - name: \"outputBucket\"\n          type: \"string\"\n          source: \"ParallelFor/outputBucket\"\n"
  ]) : ""

}



resource "local_file" "workflow_yaml" {
  filename   = "${path.module}/../../../src/invoker/workflowData/${var.prov}_${var.region}_${var.funcName}.yaml"
  content    = <<EOF
name: "${var.funcName}Experiment"
dataIns:
${local.conditionalInputFile}
${local.conditionalOutputBucket}
- name: "provider"
  type : "string"
  source: "provider"
- name: "region"
  type: "string"
  source: "region"
- name: "concurrency"
  type: "number"
  source: "concurrency"
- name: "execution"
  type: "number"
  source: "execution"

${local.additional_inputs_input_section}

workflowBody:
- parallelFor:
    name: "ParallelFor"
    dataIns:
    - name: "region"
      type: "string"
      source: "${var.funcName}Experiment/region"
      constraints:
      - name: "distribution"
        value: "REPLICATE(*)"
    - name: "provider"
      type: "string"
      source: "${var.funcName}Experiment/provider"
      constraints:
      - name: "distribution"
        value: "REPLICATE(*)"
    - name: "execution"
      type: "number"
      source: "${var.funcName}Experiment/execution"
      constraints:
        - name: "distribution"
          value: "REPLICATE(*)"
${local.conditionalParallelInputFile}
${local.conditionalOutputBucketParallel}
${local.additional_inputs_parallel_input_section}
    loopCounter:
      type: "number"
      from: "0"
      to: "${var.funcName}Experiment/concurrency"
      step: "1"
    loopBody:
    - function:
        name: "${var.funcName}"
        type: "${var.funcName}Type"
        dataIns:
        - name: "provider"
          type: "string"
          source: "ParallelFor/provider"
        - name: "region"
          type: "string"
          source: "ParallelFor/region"
        - name: "execution"
          type: "number"
          source: "ParallelFor/execution"
${local.conditionalFunntionInputFile}
${local.cconditionalOutputBucketFunction}
${local.additional_inputs_function_input_section}
        dataOuts:
${local.additional_outputs_function}
        properties:
          - name: "resource"
            value: "${var.funcUrl}"
    dataOuts:
      - name: "region"
        type: "collection"
        source: "${var.funcName}/region"
      - name: "provider"
        type: "collection"
        source: "${var.funcName}/provider"
      - name: "execution"
        type: "collection"
        source: "${var.funcName}/execution"
${local.additional_outputs}
EOF

}





module "input" {
  source = "../inputWorkflow"


  concurrency             = var.concurrency
  inputBucketFileAddress  = var.inputBucketFileAddress
  inputFiles              = var.inputFiles
  prov                    = var.prov
  region                  = var.region
  repetition              = var.repetition
  useOutPutBucket         = var.useOutPutBucket
  jsonPath = "${path.module}/../../../src/invoker/workflowData/${var.prov}_${var.region}_${var.funcName}.json"
  additional_input_params = var.additional_input_params
}






