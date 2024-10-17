
from dataclasses import dataclass, field
from pymongo import MongoClient
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database,drop_database
import json
import pandas as pd
import os
import logging

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
    def write_collection(self, collection, data):
        db = self.connection[self.database]
        collection = db[collection]
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)

def expand_output_column(df):
    if('output' not in df.columns):
        return df
    df['output'] = df['output'].apply(lambda x: json.loads(x) if pd.notnull(x) else {})

    output_df = df['output'].apply(pd.Series)
    df = df.drop(columns=['output']).join(output_df)
    ot = pd.DataFrame()
    df = df.join(ot)

    return df
def extract_region_provider_execution_from_input(workflow_input):
    parsed_data = json.loads(workflow_input)


    region = provider = execution = None

    region = parsed_data['region']
    provider = parsed_data['provider']
    execution = parsed_data['execution']

    return region, provider, execution
def checkkColderColdstart(rtt):
    return ((rtt['coldStart']==1) and (rtt['serviceTime'] >= 5000) and (rtt['provider']=='GCP') and (rtt['functionName']!='recognition'))

def check_delayedwarmstart(row, group):
        
        return (row['coldStart'] == 0) and (row['startExecutionTime'] >= group['endExecutionTime'].min())

def markDelayedWarmstarts(data):

    data['startMode'] = data.apply(
        lambda x: 'delayedWarm' if check_delayedwarmstart(x, data[(data['provider'] == x['provider'])&(data['execution'] == x['execution'])&(data['timeOfDay'] == x['timeOfDay'])&(data['region'] == x['region'])&(data['concurrentFunctions'] == x['concurrentFunctions'])])
        else 'colderColdStart' if checkkColderColdstart(x) else x['coldStart'], axis=1
    )
  
    return data
def createDatabase(database_url):
    engine = create_engine(database_url)
    if database_exists(engine.url):
        drop_database(engine.url)
    create_database(engine.url)
    return engine

def save_as_sql(collection:pd.DataFrame,engine):
    grouped = collection.groupby('workflow_id')
    empty_data_frame =[]

    for workflow_id, group in grouped:
        if 'FUNCTION_END' not in list(group['Event']):
            continue
        functions = group[group['Event'] == 'FUNCTION_END']
        functions = expand_output_column(functions)
        for col in functions.columns:
            if functions[col].apply(lambda x: isinstance(x, dict)).any():
                functions[col] = functions[col].apply(json.dumps)
        start_time_workflow_start = group[group['Event'] == 'WORKFLOW_START'].iloc[0]['startTime']
        end_time_workflow_start = group[group['Event'] == 'WORKFLOW_START'].iloc[0]['endTime']
        round_trip_time_workflow_start = group[group['Event'] == 'WORKFLOW_START'].iloc[0]['RTT']
        start_time_workflow_end = group[group['Event'] == 'WORKFLOW_END'].iloc[0]['startTime']
        end_time_workflow_end = group[group['Event'] == 'WORKFLOW_END'].iloc[0]['endTime']
        round_trip_time_workflow_end = group[group['Event'] == 'WORKFLOW_END'].iloc[0]['RTT']
        concurrent_functions = len(functions)
        region, provider, execution = extract_region_provider_execution_from_input(
            group[group['Event'] == 'WORKFLOW_START'].iloc[0]['workflowInput']
        )
        function_name = functions.iloc[0]['functionName']
        for _, func_row in functions.iterrows():
            columns_to_exclude = [
                'workflow_id', 'workflowContent', 'workflowInput', 'function_id',
                'deployment', 'functionName', 'functionType', 'Event','output',
                'RTT', 'cost', 'success', 'loopCounter',
                'maxLoopCounter', 'startTime', 'endTime', 'type', 'done','_id',
                'region', 'provider', 'execution'
            ]
            additional_data = func_row[func_row.index.difference(columns_to_exclude)].to_dict()
            func_execution_record = {
                '_id': group[group['Event'] == 'WORKFLOW_START'].iloc[0]['_id'],
                'startTimeWorkflowStart': start_time_workflow_start,
                'endTimeWorkflowStart': end_time_workflow_start,
                'roundTripTimeWorkflowStart': round_trip_time_workflow_start,
                'startTimeWorkflowEnd': start_time_workflow_end,
                'endTimeWorkflowEnd': end_time_workflow_end,
                'roundTripTimeWorkflowEnd': round_trip_time_workflow_end,
                'provider': provider,
                'concurrentFunctions': concurrent_functions,
                'execution': execution,
                'functionName': function_name,
                'functionCount': concurrent_functions,
                'workflow_id': workflow_id,
                'function_id': str(func_row['_id']),
                'region': region,
                'roundTripTime': func_row['RTT'],
                'endTime': func_row['endTime'],
                'startTime': func_row['startTime'],
            }
            for key,value in additional_data.items():
                func_execution_record[key] = value

            empty_data_frame.append(func_execution_record)
    output = pd.DataFrame(empty_data_frame)
    if not output.empty:
        
        output.to_sql("workflows", con=engine, if_exists='replace', index=False)
    else:

        logging.info("DataFrame is empty or there is no successful function execution; The sql database is only filled with successful executions.")



def tranformData():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    with open('config.json') as f:
        config = json.load(f)

        mongo_config = config['mongodb']
        encoded_password = mongo_config['password']
        mn = MongoDBConnection(
        host=mongo_config['host'],
        database=mongo_config['db_name'],
        username=mongo_config['username'],
        password=encoded_password,
        port=mongo_config['port'],
    )

        mn.connect_mongo()


        collection_data = mn.read_collection(mongo_config['collection'])
        df = pd.DataFrame(collection_data)
        if df.empty:

            raise ValueError("MongoDB is empty you have to run experiments or check the properties file!")

        sql_config = config['sql']
        DATABASE_URL = f"mysql+pymysql://{sql_config['username']}:{sql_config['password']}@{sql_config['host']}:{sql_config['port']}/{sql_config['db_name']}"
        save_as_sql(df,createDatabase(DATABASE_URL))
        
        

if __name__ == '__main__':
    tranformData()
    