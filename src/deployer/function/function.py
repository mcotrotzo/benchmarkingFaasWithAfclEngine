from typing import Dict, List, Union
import uuid
from dataclasses import dataclass, asdict
from pydantic import BaseModel, Field,conlist, ValidationError,model_validator
from typing import Optional,Set,Literal
import os,json
import logging

class OutputParameter(BaseModel):
    name: str
    type: str

    @model_validator(mode="after")
    def check_name_and_age(cls, model):
        valid_types =  ['collection','string','boolean','array','number']
        if model.type not in valid_types:
            raise ValueError(f"Type {model.type} is not valid. Please select one of these types: {valid_types}")
        return model  


class Parameter(BaseModel):
    name: str = Field(...,nullable=False)
    type: str = Field(...,nullable=False)
    value: Union[str, int, bool, dict,List,Dict,float] = Field(...,nullable=False)
    
    @model_validator(mode="after")
    def check_name_and_age(cls, model):
        valid_types =  ['collection','string','boolean','array','number']
        if model.type not in valid_types:
            raise ValueError(f"Type {model.type} is not valid. Please select one of these types: {valid_types}")
        return model 

class UseBucket(BaseModel):
    useAsOutPutBucket: bool
    useAsInputBucket: bool
    inputFilePaths: Optional[List[str]] = []
    @model_validator(mode="before")
    def validate_input_file_paths(cls, values):
        use_as_input = values.get('useAsInputBucket', False)
        file_paths = values.get('inputFilePaths', [])
        if use_as_input:
            if not file_paths or file_paths == []:
                raise ValueError("inputFilePaths cannot be empty when useAsInputBucket is True")
            for path in file_paths:
                if not os.path.exists(path):
                    raise ValueError(f"Invalid file path: {path}")

        return values
class Region(BaseModel):
    name: str
    concurrency: int
    repetition: int
 
    @model_validator(mode='before')
    def remove_spaces_in_name(cls, values):
        values['name'] = values.get('name', '').replace(" ", "")
        return values
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, value):
        if isinstance(value,Region):
            return self.name == value.name

        return False

class Providers(BaseModel):
    name: Literal["AWS","GCP"]
    handler: str
    runtime: str
    regions: List[Region]
    
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, value):
        if isinstance(value,Providers):
            return self.name == value.name

        return False
    
    @model_validator(mode="before")
    def unique_providers(cls, values):
        regions = values.get('regions', [])
        seen_names = set()
        for region in regions:
            if region['name'] in seen_names:
                raise ValueError(f"Duplicate region name found: {region['name']}")
            seen_names.add(region['name'])
        
        return values
    

class FunctionModel(BaseModel):
    name: str = Field(...,min_length=1)
    archive: str 
    timeout: int
    memory: int
    useBucket: Optional[UseBucket] = None
    additionalInputParameters: List[Parameter] = []
    additionalOutputParameters: List[OutputParameter] = []
    providers: List[Providers] = Field(..., min_length=1)
    
    @model_validator(mode="before")
    def unique_providers(cls, values):
        providers = values.get('providers', [])
        seen_names = set()
        for provider in providers:
            if provider['name'] in seen_names:
                raise ValueError(f"Duplicate provider name found: {provider['name']}")
            seen_names.add(provider['name'])
        if not os.path.exists(values['archive']):
            raise ValueError(f"Invalid file path: {values['archive']}")
        
        return values
    
    def __hash__(self):
        return hash((self.name))
    
    def __eq__(self, value):
        if isinstance(value,FunctionModel):
            return self.name == value.name

        return False
    

class Functions(BaseModel):
    functions: List[FunctionModel] = Field(..., min_length=1,unique=True)
    
    @model_validator(mode="before")
    def unique_providers(cls, values):
        functions = values.get('functions', [])
        seen_names = set()
        for function in functions:
            if function['name'] in seen_names:
                raise ValueError(f"Duplicate function name found: {function['name']}")
            seen_names.add(function['name'])
        
        return values
    
    def getRegFunctionList(self):
        deployment_dict = {}
        region_dict = {}
        for function in self.functions:
            for provider in function.providers:
                provider_name = provider.name

                if provider_name not in deployment_dict:
                    deployment_dict[provider_name] = {}

                region_dict = deployment_dict[provider_name]

                for region in provider.regions:
                    region_name = region.name
                    if region_name not in region_dict:
                        region_dict[region_name] = []

                    use_bucket = function.useBucket
                    if use_bucket:
                        use_output_bucket = use_bucket.useAsOutPutBucket
                        input_file_paths = use_bucket.inputFilePaths if use_bucket.useAsInputBucket else []
                    else:
                        use_output_bucket = False
                        input_file_paths = []

                    new_function = Function(
                        handler=provider.handler,
                        runtime=provider.runtime,
                        archive=function.archive,
                        name=function.name,
                        timeout=function.timeout,
                        memory=function.memory,
                        use_output_bucket=use_output_bucket,
                        input_files = input_file_paths,
                        additional_output_parameters=self.select_by_type(function.additionalOutputParameters),
                        additional_input_parameters=self.select_by_type(function.additionalInputParameters),
                        concurrency=region.concurrency,
                        repetition=region.concurrency
                    )

                    region_dict[region_name].append(new_function)

        logging.info("Successfully parsed configuration.")
        return deployment_dict
    def select_by_type(self, input_params):
        return '[ ' + ', '.join(
            f'{{ "name": "{param.name}", "type": "{param.type}", "value": {json.dumps(param.value if hasattr(param,"value") else "")} }}'
            for param in input_params
        ) + ' ]'

        
    

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
                 input_files: List[str],
                 use_output_bucket:bool,
                 additional_input_parameters: str,
                 additional_output_parameters: str
                 ):
        self.archive = archive
        self.name = name
        self.timeout = timeout
        self.memory = memory
        self.handler = handler
        self.runtime = runtime
        self.input_files = input_files
        self.additional_input_parameters = additional_input_parameters  
        self.additional_output_parameters = additional_output_parameters
        self.use_output_bucket = use_output_bucket
        self.concurrency = concurrency
        self.repetition = repetition

