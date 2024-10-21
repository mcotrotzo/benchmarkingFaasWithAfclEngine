import os
import json
import logging
import sys



    

def load_config(file_path):
    
    if not os.path.exists(file_path):
        raise FileNotFoundError
    
    with open(file_path, 'r') as config_file:
        return json.load(config_file)

def save_json(dict:dict,path,mode:str):
    
    with open(path, mode) as config_file:
        return json.dump(dict, config_file, indent=4)
    

def save_properties_file(file_path,content:str='',**kwargs):
    prop = content
    for key, value in kwargs.items():
        print(value)
        prop += f"{key}={value}\n" 
    with open(file_path, "w") as file:
        file.write(prop)
    
    with open(file_path,'w') as properties:
        properties.write(prop) 

def handle_error(error_message):
    logging.error(f"Error: {error_message}")
    sys.exit(error_message)
    

def get_env(env:str):
    res = os.getenv(env)
    #if res == None or res == '':
     #   sys.exit(f"{env.upper()} is not present in the .env file!")
    return res
        