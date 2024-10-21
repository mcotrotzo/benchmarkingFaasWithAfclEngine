from urllib.parse import quote_plus
from dataclasses import dataclass,field
from pymongo import MongoClient
from ..settings import COLLECTION,DATABASE,HOST,PASSWORD,PORT,USERNAME
import pandas as pd
import json
@dataclass
class MongoDBConnection:
    host: str
    username: str
    password: str
    port: str
    database: str
    connection: MongoClient = field(init=False, default=None)

    def connect_mongo(self):
        if self.username and self.password:
            username = quote_plus(self.username)
            password = quote_plus(self.password)
            mongo_uri = f'mongodb://{username}:{password}@{self.host}:{self.port}/?authSource={self.database}'
            print(mongo_uri)
            self.connection = MongoClient(mongo_uri)
        else:
            self.connection = MongoClient(self.host, self.port)

    def read_collection(self, collection, filter_query=None):
        data = self.connection[self.database][collection]
        if filter_query is None:
            filter_query = {}
        return data.find(filter_query)
    
    

def returnDataframe():
    mn = MongoDBConnection(host=HOST, username=USERNAME, password=PASSWORD, port=int(PORT), database=DATABASE)
    mn.connect_mongo()
    coll = mn.read_collection(collection=COLLECTION)
    
    
    dataframe = pd.DataFrame(list(coll))
    
   
    for col in ['workflowInput', 'output']:
     
        dataframe[col] = dataframe[col].apply(lambda x: json.loads(x) if isinstance(x, str) and x not in [None, "None"] else {})
        
        
        normalized_data = pd.json_normalize(dataframe[col])
        normalized_data.columns = [f"{col}_{sub_col}" for sub_col in normalized_data.columns]
      
        dataframe = pd.concat([dataframe.drop(columns=[col]), normalized_data], axis=1)
    
   
    return dataframe
    

