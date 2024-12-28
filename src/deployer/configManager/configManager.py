from ..function.function import Function,FunctionModel,Functions
import json
from ...utils.utils import handle_error,load_config,save_json
import os
import logging

import json
import os
import logging
from jsonschema import validate, ValidationError, SchemaError

class ConfigManager:

    def __loadFromJson(self, config_json: str) -> dict:
            try:
                config = load_config(config_json)
                logging.info(f"Successfully loaded configuration from {config_json}.")
                return config
            except FileNotFoundError as e:
                handle_error(f"Config file not found {config_json}")

            except Exception as e:
                handle_error(f"Error occured loading config file {e}")


    def parse_config(self, config_input: str) -> dict:
        try:
            config_data = self.__loadFromJson(config_input)

            print("Validate config file....")
            ff = Functions(**config_data)
            return ff.getRegFunctionList()

        except ValidationError as e:
            handle_error(f"Validation error in configuration: {e}")
        except SchemaError as e:
            handle_error(f"Schema error: {e.message}")
        except Exception as e:
            handle_error(f"An error occurred while parsing configuration: {e}")


    def select_by_type(self, input_params):

        return  '[ ' + ', '.join(
                f'{{ "name": "{param["name"]}","type": "{param["type"]}","value": jsonencode({json.dumps(param.get("value",""))})}}'
                for param in input_params
            ) + ' ]'





