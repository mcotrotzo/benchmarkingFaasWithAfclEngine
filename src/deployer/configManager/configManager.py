from ..function.function import Function
import json
from ...utils.utils import handle_error,load_config,save_json
import os
import logging

import json
import os
import logging
from jsonschema import validate, ValidationError, SchemaError

class ConfigManager:
    
    SCHEMA = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "functions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" },
                        "archive": { "type": "string" },
                        "timeout": { "type": "integer" },
                        "memory": { "type": "integer" },
                        "useBucket": {
                            "type": "object",
                            "properties": {
                                "useAsOutPutBucket": {
                                    "type": "boolean",
                                    "description": "Set to true if the bucket is used for output.",
                                    "default":False
                                },
                                "useAsInputBucket": {
                                    "type": "boolean",
                                    "description": "Set to true if the bucket is used for input. If true you have to specify file paths to your local input files. They will be uploaded to the bucket",
                                    "default":False
                                },
                                "inputFilePaths": {
                                    "type": "array",
                                    "items": {
                                        "type": "string",
                                        "description": "Path to the local input file. The file will be uploaded to the bucket, and its URL will be added to the request. The workflow key will be then the name of basename of the inputFile"
                                    },
                                    "description": "Specify file paths if the bucket is used for input.",
                                    "minItems": 1
                                }
                            },
                            "required":['useAsOutPutBucket','useAsInputBucket'],
                            "if": {
                                "properties": {  "useAsOutPutBucket": { "const": False },"useAsInputBucket": { "const": True } },
                                "required":['useAsOutPutBucket','useAsInputBucket'],
                            },
                            "then": {
                                "required": ["inputFilePaths"],
                                "description":"You need to specify a list of file paths. These files are uploaded to the bucket. if you only need the bucket address you can set useAsInputBucket false you can set useAsInputBucket to false. A bucket is created and the URL is passed to the request. The workflow key is outputBucket"
                            },
                            "else": {
                                "if": {
                                    "properties": {  "useAsOutPutBucket": { "const": True },"useAsInputBucket": { "const": True } },
                                    "required":['useAsOutPutBucket','useAsInputBucket'],
                                },
                                "then": {
                                    "required": ["inputFilePaths"],
                                    "description":"You need to specify a list of file paths. These files are uploaded to the bucket. if you only need the bucket address you can set useAsInputBucket false you can set useAsInputBucket to false. A bucket is created and the URL is passed to the request. The workflow key is outputBucket"

                                },
                                "else":{
                                    "not": {"required": ["inputFilePaths"]}
                                }
                            },
                            "description": "Specify whether the bucket will be used as input, output, or both."
                        },
                        "additionalInputParameters": {
                            "description": "A list of input parameters.",
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": { "type": "string" },
                                    "type": { "type": "string" },
                                    "value": {
                                        "oneOf": [
                                            { "type": "string" },
                                            { "type": "number" },
                                            { "type": "boolean" },
                                            { "type": "array" },
                                            { "type": "object" }
                                        ]
                                    }
                                },
                                "required": ["name", "type", "value"]
                            }
                        },
                        "additionalOutputParameters": {
                            "description": "A list of output parameters.",
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": { "type": "string" },
                                    "type": { "type": "string" }
                                },
                                "required": ["name", "type"]
                            }
                        },
                        "providers": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": { "type": "string" },
                                    "handler": { "type": "string" },
                                    "runtime": { "type": "string" },
                                    "regions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": { "type": "string" },
                                                "concurrency": { "type": "integer" },
                                                "repetition": { "type": "integer" }
                                            },
                                            "required": ["name", "concurrency", "repetition"]
                                        }
                                    }
                                },
                                "required": ["name", "handler", "runtime", "regions"]
                            }
                        }
                    },
                    "required": ["name", "archive", "timeout", "memory", "providers"]
                }
            }
        },
        "required": ["functions"]
    }


    def __loadFromJson(self, config_json: str) -> dict:
            try:
                config = load_config(config_json)
            except FileNotFoundError as e:
                handle_error(f"Config file not found {config_json}")
            except Exception as e:
                handle_error(f"Error occured loading config file {e}")
                
            logging.info(f"Successfully loaded configuration from {config_json}.")
            return config

    def parse_config(self, config_input: str) -> dict:
        try:
            config_data = self.__loadFromJson(config_input)

            print("Validate config file....")
            validate(instance=config_data, schema=self.SCHEMA)
            logging.info("Validate config file success!")

            deployment_dict = {}
            keep_function_unique = []
            for function in config_data['functions']:
                function_name = function['name']


                if function_name in keep_function_unique:
                    raise ValidationError(f"Function names should be unique! Duplicate found: {function_name}")
                keep_function_unique.append(function_name)

                for provider in function['providers']:
                    provider_name = provider['name']

                    if provider_name not in deployment_dict:
                        deployment_dict[provider_name] = {}

                    region_dict = deployment_dict[provider_name]

                    for region in provider['regions']:
                        region_name = region['name']
                        if region_name not in region_dict:
                            region_dict[region_name] = []

                        use_bucket = function.get('useBucket', {})
                        use_output_bucket = use_bucket.get('useAsOutPutBucket', False)


                        input_file_paths = use_bucket.get('inputFilePaths', [])
                        new_function = Function(
                            handler=provider['handler'],
                            runtime=provider['runtime'],
                            archive=function['archive'],
                            name=function['name'],
                            timeout=function['timeout'],
                            memory=function['memory'],
                            use_output_bucket=use_output_bucket,
                            input_files = input_file_paths,
                            additional_output_parameters=self.select_by_type(function.get('additionalOutputParameters',[])),
                            additional_input_parameters=self.select_by_type(function.get('additionalInputParameters',[])),
                            concurrency=region.get('concurrency', 1),
                            repetition=region.get('repetition', 1)
                        )

                        region_dict[region_name].append(new_function)

            logging.info("Successfully parsed configuration.")
            return deployment_dict

        except ValidationError as e:
            handle_error(f"Validation error in configuration: {e.message}")
        except SchemaError as e:
            handle_error(f"Schema error: {e.message}")
        except Exception as e:
            handle_error(f"An error occurred while parsing configuration: {e}")


    def select_by_type(self, input_params):
        res = {}




        return  '[ ' + ', '.join(
                f'{{ "name": "{param["name"]}","type": "{param["type"]}","value": jsonencode({json.dumps(param.get("value",""))})}}'
                for param in input_params
            ) + ' ]'





