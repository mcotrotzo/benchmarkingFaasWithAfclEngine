from .function.function import Function
from .awsProvider import awsProvider
from .gcpProvider import gcpProvider
from .credentials.credentials import Credentials, AWSCredentials,GCPCredentials
from .bascloud import baseCloud
from .awsProvider import awsProvider
from .gcpProvider import gcpProvider
from .configManager.configManager import ConfigManager
from typing import Dict,List
from ..utils.utils import save_json,handle_error
from ..settings import CREDENTIALSPATH,CONFIG_PATH
from dataclasses import dataclass
import subprocess
import os
from python_terraform  import Terraform
from dotenv import load_dotenv
from os.path import join, dirname
from pathlib import Path
import shutil
@dataclass
class TerraformManager():
    conig_manager:ConfigManager
    data_dict = Dict[str,baseCloud]
    maintf:str
    providertf:list[str]
    
    def __init__(self,config,credentials_path,dest_path_folder):
        try:
            self.dest_path_folder =dest_path_folder
            self.data_dict = {}
            self.maintf = ''
            self.providertf = []
            data = ConfigManager().parse_config(config)
            
            for prov,region in data.items():
                deployer = None
                if prov == 'AWS':
                    credentials = AWSCredentials(credentials_path=credentials_path,key='aws_credentials')
                    deployer = awsProvider(credentials=credentials,region_func=region,module_folder_name='amazon')
                    self.data_dict[prov] = deployer
                    return
                if prov == 'GCP':
                    credentials = GCPCredentials(credentials_path=credentials_path,key='gcp_credentials')
                    deployer = gcpProvider(credentials=credentials,region_func=region,module_folder_name='google')
                    self.data_dict[prov] = deployer
                    return
                raise ValueError(f"Provider{prov} is at the moment not avaiable!")
        except Exception as e:
            handle_error(f"Initalizing TerraformManager failed {e}")
    
    def produce_deployment(self):
        self.produce_required_provider()
        self.produce_module_calls()
        self.produce_providers()
        try:
            self.save_content_as_tf_file(self.maintf,'main.tf')
            self.save_provider_content_as_tf_file(self.providertf,'providers.tf')
        except Exception as e:
            handle_error(f"Error saving tf file: {e}")
    def produce_providers(self):
        for prov in self.data_dict.keys():
            deployer = self.data_dict[prov]
            self.providertf.append(deployer.provider_block_tf())
    def produce_module_calls(self):
        for prov in self.data_dict.keys():
            deployer = self.data_dict[prov]
            self.maintf+=deployer.module_call_tf()
        
       
        
    def produce_required_provider(self):
        required_providertf = 'terraform {\n  required_providers {\n'
        for prov in self.data_dict.keys():
            required_providertf+=self.data_dict[prov].requiered_provider_tf()
        required_providertf += """
  }
}
"""     
        
        for prov in self.data_dict.keys():
            self.data_dict[prov].save_file_to_module_folder(self.dest_path_folder / 'modules',required_providertf,'providers')
        self.maintf+=required_providertf

    def save_provider_content_as_tf_file(self, content: list[str], name: str):
        existing_content = ''
        if os.path.exists(self.dest_path_folder / name):
            with open(self.dest_path_folder / name, 'r') as file:
                existing_content = file.read()
        existing_lines = existing_content.strip()

        for prov in content:

            prov = prov.strip()
            if not prov in existing_lines:
                print(prov)
                print(existing_lines)
                existing_lines += "\n"+prov

        self.save_content_as_tf_file(existing_lines, name)


    def save_content_as_tf_file(self, content: str, name: str):
        with open(f"{self.dest_path_folder}/{name}", 'w') as outfile:
            outfile.write(content)
    @staticmethod
    def clean_folders_and_all_terraform_files(dest_path_folder):
        try:
            with os.scandir(dest_path_folder) as entries:
                for entry in entries:
                    if entry.is_file():
                        print(entry.name)
                        os.unlink(entry.path)
                    if entry.name == 'modules':
                        continue
                    elif entry.is_dir():
                        try:
                            shutil.rmtree(entry.path)
                        except FileNotFoundError:
                            print(f"Directory not found: {entry.path}")
            print("All files and subdirectories of terraform deleted successfully.")
        except OSError as e:
            print("Error occurred while deleting files and subdirectories.")
            print(e)

        



def deploy(dest_terraform_path_folder: str):

    try:
        manager = TerraformManager(config=CONFIG_PATH, credentials_path=CREDENTIALSPATH, dest_path_folder=dest_terraform_path_folder)
        manager.produce_deployment()
       
        tf = Terraform(working_dir=dest_terraform_path_folder)
        state = tf.init(capture_output=False)
        if state[0] != 0:
            raise Exception()
        state = tf.apply(auto_approve=True, capture_output=False)
        
        if state[0] != 0:
            raise Exception()
    except Exception as e:
        handle_error(f"Deployment error: {e}")
    return manager

def destroy(dest_terraform_path_folder: str):
    try:
        cw = os.getcwd()
        os.chdir(dest_terraform_path_folder)
        state = subprocess.run(['terraform', 'destroy'],check=True)
        os.chdir(cw)
        state.check_returncode()
        TerraformManager.clean_folders_and_all_terraform_files(dest_path_folder=dest_terraform_path_folder)
    except Exception as e:
        handle_error(f"Destruction error: {e}")
    
    
    