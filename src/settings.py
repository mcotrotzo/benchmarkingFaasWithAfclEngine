import os
from os.path import join, dirname
from dotenv import load_dotenv
from .utils.utils import handle_error,get_env
dotenv_path = join(dirname(__file__),'../')
dotenv_path = join(dotenv_path ,'.env')



try:
    load_dotenv(dotenv_path)
    HOST = get_env('MONGO_HOST')
    PORT=get_env('MONGO_PORT')
    DATABASE=get_env('MONGO_INITDB_DATABASE')
    COLLECTION=get_env('MONGO_COLLECTION')
    USERNAME=get_env('MONGO_INITDB_ROOT_USERNAME')
    PASSWORD=get_env('MONGO_INITDB_ROOT_PASSWORD')
    CREDENTIALSPATH = os.path.normpath(get_env('CREDENTIALS_JSON_PATH'))
    CONFIG_PATH =os.path.normpath(get_env('CONFIG_PATH'))

except Exception as e:
    handle_error(e)
    raise
    

