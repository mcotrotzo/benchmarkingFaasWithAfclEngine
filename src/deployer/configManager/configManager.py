from src.deployer.function.function import Function, Parameter, OutputParameter
import json
from typing import Dict, Union
import os
import logging

class ConfigManager:
    def __loadFromJson(self, config_json: str):
        with open(config_json, 'r') as file:
            return json.load(file)

    def parse_config(self, config_input: str) -> dict:

            config = self.__loadFromJson(config_input)

            deployment_dict = {}


            for function in config['functions']:
                for provider in function['providers']:
                    provider_name = provider['name']

                    if provider_name not in deployment_dict:
                        deployment_dict[provider_name] = {}

                    region_dict = deployment_dict[provider_name]

                    for region in provider['regions']:
                        if region['name'] not in region_dict:
                            region_dict[region['name']] = []

                        input_params = function['additionalInputParameters']
                        output_params = function['additionalOutputParameters']

                        keys = function.keys()
                        new_function = Function(
                            handler=provider['handler'],
                            runtime=provider['runtime'],
                            archive=function['archive'],
                            name=function['name'],
                            timeout=function['timeout'],
                            memory=function['memory'],
                            use_output_bucket=function['useOutputBucket'] if 'useOutputBucket' in keys else False,
                            input_files_folder_path=function['inputFilesFolderPath'] if 'inputFilesFolderPath' in keys else '',
                            input_files=function['inputFiles'] if 'inputFiles' in keys else [
                            ],

                            additional_output_parameters=self.select_by_type(output_params),
                            additional_input_parameters=self.select_by_type(input_params),
                            concurrency=region['concurrency'],
                            repetition = region['repetition'],
                        )

                        region_dict[region['name']].append(new_function)
            return deployment_dict



    def select_by_type(self, input_params):
        res = {}




        return  '[ ' + ', '.join(
                f'{{ "name": "{param["name"]}","type": "{param["type"]}","value": jsonencode({json.dumps(param.get("value",""))})}}'
                for param in input_params
            ) + ' ]'





