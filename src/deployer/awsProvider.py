from src.deployer.bascloud import baseCloud
from src.deployer.credentials.credentials import AWSCredentials
from src.deployer.function.function import Function
from typing import Dict, List
import uuid
import json
class awsProvider(baseCloud):
    def __init__(self, credentials: AWSCredentials, region_func: Dict[str, List[Function]], 
                 module_folder_name: str) -> None:
        super().__init__(credentials, region_func=region_func, module_folder_name=module_folder_name)


    def module_call_tf(self):
        res = ''
        random_stack_id = uuid.uuid4().hex
        

        for region, functions in self.region_func.items():
            res += f"""
module "{region}" {{
  source = "./modules/amazon"
  region = "{region}"
  providers = {{
    aws = aws.{region}
  }}

  functions = [
"""
            
            for function in functions:
                res += f"""
    {{
      name                     = "{function.name}"
      handler                  = "{function.handler}"
      runtime                  = "{function.runtime}"
      archive                  = "{function.archive}"
      memory                   = {function.memory}
      timeout                  = {function.timeout}
      inputFiles               = {json.dumps(function.input_files)}
      additional_input_params   = {function.additional_input_parameters}
      additional_output_params  = {function.additional_output_parameters}
      useOutputBucket          = {"true" if function.use_output_bucket else "false"}
      concurrency           = {function.concurrency}
      repetition = {function.repetition}
      
    }},
"""
            
            res += """
  ]
}
"""
        return res

    def requiered_provider_tf(self):
        return """
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
      }
"""

    def provider_block_tf(self):
        res = ''
        for region in self.region_func.keys():
            res += f"""
provider "aws" {{
  alias      = "{region}"
  region     = "{region}"
  access_key = "{self.credentials.access_key}"
  secret_key = "{self.credentials.secret_key}"
  token      = "{self.credentials.token}"
}} 
"""
        return res
