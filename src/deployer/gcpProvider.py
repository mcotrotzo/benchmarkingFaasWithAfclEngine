from src.deployer.bascloud import baseCloud
from src.deployer.credentials.credentials import Credentials, AWSCredentials, GCPCredentials
from src.deployer.function.function import Function
from typing import Dict, List
import uuid
import json
class gcpProvider(baseCloud):

    def __init__(self, credentials: GCPCredentials, region_func: Dict[str, List[Function]], module_folder_name: str) -> None:
        super().__init__(credentials, region_func=region_func, module_folder_name=module_folder_name)

    def module_call_tf(self):
        res = ''
        for region, functions in self.region_func.items():
            res += f"""
module "{region}" {{
  source = "./modules/google"
  region = "{region}"
  providers = {{
    google = google.{region}
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
    google = {
      source  = "hashicorp/google"
      version = "~> 3.5"
    }
"""

    def provider_block_tf(self):
        res = ''
        for region in self.region_func.keys():
            res += f"""
provider "google" {{
  project = "{self.credentials.project_id}"
  region  = "{region}"
  alias   = "{region}"
}}
"""
        return res
    def credentials_afcl(self):
        return f"""
google_sa_key={self.credentials.__dict__}
    """
