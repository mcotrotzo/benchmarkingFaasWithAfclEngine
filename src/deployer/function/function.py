from typing import Dict, List, Union
import uuid
from dataclasses import dataclass, asdict

@dataclass
class OutputParameter:
    name: str
    type: str

    def to_dict(self):
        """Converts the Parameter to a dictionary."""
        return asdict(self)

@dataclass
class Parameter:
    name: str
    type: str
    value: Union[str, int, bool, dict,List[Union[str,int,bool,dict]]]  

    def to_dict(self):
        return asdict(self)

class Function:
    def __init__(self, 
                 archive: str,
                 concurrency:int,
                 repetition:int,
                 name: str,
                 timeout: int, 
                 memory: int, 
                 handler: str, 
                 runtime: str, 
                 input_files_folder_path: str, 
                 input_files: List[str],
                 use_output_bucket:bool,
                 additional_input_parameters: list[dict],
                 additional_output_parameters: list[dict]
                 ):
        self.archive = archive
        self.name = name
        self.timeout = timeout
        self.memory = memory
        self.handler = handler
        self.runtime = runtime
        self.input_files_folder_path = input_files_folder_path
        self.input_files = input_files
        self.additional_input_parameters = additional_input_parameters  
        self.additional_output_parameters = additional_output_parameters
        self.use_output_bucket = use_output_bucket
        self.concurrency = concurrency
        self.repetition = repetition

