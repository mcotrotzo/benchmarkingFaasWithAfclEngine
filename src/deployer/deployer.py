from src.deployer.function.function import Function
from src.deployer.awsProvider import awsProvider
from src.deployer.gcpProvider import gcpProvider
from src.deployer.credentials.credentials import Credentials, AWSCredentials,GCPCredentials
from src.deployer.bascloud import baseCloud
from src.deployer.awsProvider import awsProvider
from src.deployer.gcpProvider import gcpProvider
from src.deployer.configManager.configManager import ConfigManager
from typing import Dict,List
import uuid
from dataclasses import dataclass
import subprocess
import os
from python_terraform  import Terraform
from dotenv import load_dotenv


@dataclass
class TerraformManager():
    conig_manager:ConfigManager
    data_dict = Dict[str,baseCloud]
    maintf:str
    providertf:list[str]
    
    def __init__(self,config,credentials_path):
        print("here")
        self.data_dict = {}
        self.maintf = ''
        self.providertf = []
        data = ConfigManager().parse_config(config)
        for prov,region in data.items():
            deployer = None
            if prov == 'AWS':
                credentials = AWSCredentials(credentials_path=credentials_path,key='aws_credentials')
                deployer = awsProvider(credentials=credentials,region_func=region,module_folder_name='amazon')
            if prov == 'GCP':
                credentials = GCPCredentials(credentials_path=credentials_path,key='gcp_credentials')
                deployer = gcpProvider(credentials=credentials,region_func=region,module_folder_name='google')
            self.data_dict[prov] = deployer
    
    
    def produce_deployment(self):
        self.produce_required_provider()
        self.produce_module_calls()
        self.produce_providers()
        self.save_content_as_tf_file(self.maintf,'main.tf')
        self.save_provider_content_as_tf_file(self.providertf,'providers.tf')
    
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
            self.data_dict[prov].save_file_to_module_folder('./modules',required_providertf,'providers')
        self.maintf+=required_providertf

    def save_provider_content_as_tf_file(self, content: list[str], name: str):


        existing_content = ''
        if os.path.exists(name):
            with open(name, 'r') as file:
                existing_content = file.read()
        for prov in content:
            if prov not in existing_content:
                existing_content+=prov

        self.save_content_as_tf_file(existing_content,name)


    def save_content_as_tf_file(self, content: str, name: str):

        with open(f"{name}", 'w') as outfile:
            outfile.write(content)


import json
def write_credentials_in_experiment_script():
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)
        with open('src/invoker/credentials.json', 'w') as dest:
            json.dump(credentials, dest, indent=4)

def write_database_properties():
    host = os.getenv('MONGO_HOST')
    port = os.getenv('MONGO_PORT')
    database = os.getenv('MONGO_INITDB_DATABASE')
    collection = os.getenv('MONGO_COLLECTION')
    username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
    password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
    sql_host = os.getenv('MYSQL_HOST', 'localhost')
    sql_port = os.getenv('MYSQL_PORT', '3306')
    sql_database = os.getenv('MYSQL_DATABASE')
    sql_username = os.getenv('MYSQL_USER')
    sql_password = os.getenv('MYSQL_PASSWORD')

    database_json = {
    "mongodb": {
        "host": f"{host}",
        "db_name": f"{database}",
        "username": f"{username}",
        "password": f"{password}",
        "port": f"{port}",
        "collection": f"{collection}"
    },
    "sql": {
        "host": f"{sql_host}",
        "db_name": f"{sql_database}",
        "username": f"{sql_username}",
        "password": f"{sql_password}",
        "port": f"{sql_port}"
    }
}
    mongo_properties = f"""
host={os.getenv('MONGO_HOST')}
port={os.getenv('MONGO_PORT')}
database={os.getenv('MONGO_INITDB_DATABASE')}
collection={os.getenv('MONGO_COLLECTION')}
username={os.getenv('MONGO_INITDB_ROOT_USERNAME')}
password={os.getenv('MONGO_INITDB_ROOT_PASSWORD')}
"""
    with open('src/invoker/mongoDatabase.properties', 'w') as mongo_file:
        mongo_file.write(mongo_properties.strip())
    with open('src/invoker/dataManager/config.json', 'w') as mongo_file:
        json.dump(database_json, mongo_file, indent=4)
    with open('src/analyzer/config.json', 'w') as mongo_file:
            json.dump(database_json, mongo_file, indent=4)

def deploy():
    load_dotenv()
    write_credentials_in_experiment_script()
    write_database_properties()
    manager = TerraformManager(config='config.json',credentials_path='credentials.json')
    manager.produce_deployment()
    tf = Terraform(working_dir='.')
    tf.init(capture_output=False)
    tf.apply(auto_approve=True,capture_output=False)
def destroy():
    subprocess.run(['terraform', 'destroy', '-auto-approve'],check=True)