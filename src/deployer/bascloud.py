from abc import ABC, abstractmethod
from src.deployer.credentials.credentials import Credentials,AWSCredentials,GCPCredentials,GCPClientCredentials
from src.deployer.function.function import Function
from typing import Dict,List
class baseCloud(ABC):
    
    def __init__(self,credentials:Credentials,region_func:Dict[str,List[Function]],module_folder_name:str) -> None:
        super().__init__()
        self.credentials = credentials
        self.region_func = region_func
        self.module_folder_name = module_folder_name
    @abstractmethod
    def module_call_tf(self):
        pass
    @abstractmethod
    def requiered_provider_tf(self):
        pass
    @abstractmethod
    def provider_block_tf(self):
        pass 
    
    def save_file_to_module_folder(self,path_to_module_folder:str,content:str,name_of_module_file):
        with open(f"{path_to_module_folder}/{self.module_folder_name}/{name_of_module_file}.tf", "w") as outfile:
            outfile.write(content)

    def additionalParameterHelper(self,type:str,value):
        if type == 'string':
            return str(value)
        else:
            return value