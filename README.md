# Benchmarking Tool for Terraform and FaaS with AFCL Engine

This tool allows you to deploy, invoke, analyse and destroy cloud infrastructure using Terraform and Function-as-a-Service (FaaS) for benchmarking purposes. It supports multiple modes such as deployment, invocation and analysis.
The invocation is done using the xAfCL engine. You can benchmark your serverless application. This tool is for white box testing. You can add performance measurements to your serverless functions and return the value. The xAFCL engine stores the result in a MongoDB.
You can specify the concurrency and repetition of the benchmark.
## Features

- **Deploy** cloud infrastructure using Terraform.
- **Invoke** functions and services in the deployed environment with the xAFCL enactmentengine.
- **Analyze** results by opening a `pandasgui` editor for user-driven analysis
- **Destroy** all deployed resources.
- **All**: A complete cycle that performs deployment, invocation and analysis in sequence.

## Prerequisites

Make sure you have the following installed:
- Python 3.7+
- Terraform
- Cloud provider credentials
- Java for the invocation
- MongoDB

## Installation

### 1. Create a Python Virtual Environment

First, set up a virtual environment to isolate your dependencies.

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install required Python packages (use your actual dependencies here)
pip install -r requirements.txt
```
### Configuration

All configuration files should be placed in the root directory of the repository.

### `config.json` Schema Overview

The `config.json` file allows you to configure key parameters for deploying and invoking serverless functions, specifying performance metrics, cloud providers, and input/output configurations. Below is a breakdown of the settings you can define.

#### Top-level Properties

- **`functions`** (required): A list of functions to be deployed and invoked during benchmarking. Each function is represented as an object with the following properties:

    - **`name`** (required, string): The name of the function. The name must be unique in the configuration file.
    - **`archive`** (required, string): The path to the archive (e.g., a `.zip` file) containing the code for your function.
    - **`timeout`** (required, integer): The maximum time (in seconds) allowed for the function to execute before timing out.
    - **`memory`** (required, integer): The memory (in MB) allocated to the function.
    - **`useBucket`** (optional, object): Defines whether the function will use a cloud storage bucket for input and/or output. One bucket is created for each region. Contains the following properties:

        - **`useAsOutPutBucket`** (boolean): Set to `true` if the bucket's address will be passed as a parameter to the request. In your FaaS, you can access the bucket with the key `'outputBucket'`.
        - **`useAsInputBucket`** (boolean): Set to `true` if the bucket will be used to upload input data.
        - **`inputFilePaths`** (array of strings): Specifies the local file paths that should be uploaded to the input bucket if `useAsInputBucket` is set to `true`.

      > **Note:**
      > - If the bucket is used for input, you must provide `inputFilePaths`. If only output is needed, no file paths are required.
      > - When `useAsInputBucket` is set to `true`, the bucket is passed to the request as a parameter with a key. The key is the name of the input file you have provided, and this file is accessible in your FaaS with the same name.

    - **`additionalInputParameters`** (optional, array): A list of custom input parameters for the function, defined as objects with:
        - **`name`** (required, string): The name of the input parameter.
        - **`type`** (required, string): The data type (JSON data types) (e.g., `string`, `number`, `boolean`).
        - **`value`** (required, string/number/boolean/array/object): The value of the input parameter.
      > **Note:**
      > - The values are passed to the request as a parameter with a key. The key is the `name` property,

    - **`additionalOutputParameters`** (optional, array): A list of custom output parameters, defined similarly to input parameters:
        - **`name`** (required, string): The name of the output parameter.
        - **`type`** (required, string): The data type (JSON data types) (e.g., `string`, `number`, `boolean`).

      > **Note:**
      > - When you define output parameters, your FaaS should return those parameters with the key name exactly as defined in the `name` property.

    - **`providers`** (required, array): Defines the cloud provider(s) and function details. Each provider is represented by:
        - **`name`** (required, string): The cloud provider's name (either `AWS` or `GCP`).
        - **`handler`** (required, string): The handler that defines the entry point for the function.
        - **`runtime`** (required, string): The runtime environment (e.g., `python3.8`, `nodejs14.x`).
        - **`regions`** (required, array): A list of regions where the function will be deployed. Each region is defined by:
            - **`name`** (required, string): The name of the region (e.g., `us-west-1`, `eu-central-1`).
            - **`concurrency`** (required, integer): The number of concurrent executions for benchmarking.
            - **`repetition`** (required, integer): The number of times the function will be invoked for benchmarking.

### Example `config.json`

```json
{
  "functions": [
    {
      "name": "myFunction",
      "archive": "path/to/function.zip",
      "timeout": 60,
      "memory": 512,
      "useBucket": {
        "useAsOutPutBucket": false,
        "useAsInputBucket": true,
        "inputFilePaths": ["path/to/inputFile1.txt", "path/to/inputFile2.txt"]
      },
      "additionalInputParameters": [
        { "name": "param1", "type": "string", "value": "value1" }
      ],
      "additionalOutputParameters": [
        { "name": "result", "type": "string" }
      ],
      "providers": [
        {
          "name": "aws",
          "handler": "myHandler",
          "runtime": "python3.8",
          "regions": [
            {
              "name": "us-west-1",
              "concurrency": 10,
              "repetition": 5
            }
          ]
        }
      ]
    }
  ]
}
```
### `credentials.json` Schema Overview
```json
{
  "aws_credentials": {
    "access_key": "",
    "secret_key": "",
    "token": ""
  },
  "gcp_credentials": {
    "type": "",
    "project_id": "",
    "private_key_id": "",
    "private_key": "",
    "client_email": "",
    "client_id": "",
    "auth_uri": "",
    "token_uri": "",
    "auth_provider_x509_cert_url": "",
    "client_x509_cert_url": "",
    "universe_domain": ""
  },
  "gcp_client_credentials": {
    "account": "",
    "client_id": "",
    "client_secret": "",
    "quota_project_id": "",
    "refresh_token": "",
    "type": "",
    "universe_domain": ""
  }
}
```
### `.env` Schema Overview
```properties
MONGO_INITDB_ROOT_USERNAME=
MONGO_INITDB_ROOT_PASSWORD=
MONGO_INITDB_DATABASE=
MONGO_HOST=
MONGO_PORT=
MONGO_COLLECTION=
CREDENTIALS_JSON_PATH=
CONFIG_PATH=
```
