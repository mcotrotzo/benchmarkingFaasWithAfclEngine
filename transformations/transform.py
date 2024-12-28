import pandas as pd

def calculateTimeOfDay(df):
    df['output_timeOfDay'] = df['startTime'].apply(
        lambda x: 'Morning' if pd.to_datetime(x).hour < 18 and pd.to_datetime(x).hour >= 6 else 'Evening'
    ).astype(str)
    return df

def checkkColderColdstart(rtt):
    return ((rtt['output_coldStart'] == "ColdStart") and 
            (rtt['output_serviceTime'] >= 5000) and 
            (rtt['output_provider'] == 'GCP') and 
            (rtt['function'] != 'recognition'))

def check_delayedwarmstart(row, group):
    return (row['output_coldStart'] == "WarmStart") and row['Event']=="FUNCTION_END" and (row['output_startExecutionTime'] >= group['output_endExecutionTime'].min())

def markDelayedWarmstarts(data):
    data['startMode'] = data.apply(
        lambda x: 'FakeWarmStart' if check_delayedwarmstart(
            x, data[
                (data['Event']=="FUNCTION_END")&
                (data['output_provider'] == x['output_provider']) &
                (data['output_execution'] == x['output_execution']) &
                (data['output_timeOfDay'] == x['output_timeOfDay']) &
                (data['output_region'] == x['output_region']) &
                (data['Concurrency'] == x['Concurrency']) &
                ((data['function'] == x['function']))
            ]
        ) else 'ColderThanColdStart' if checkkColderColdstart(x) else x['output_coldStart'], 
        axis=1
    )
    return data
def coldStart(data):
    print("Available columns:", data.columns)  # Debugging line
    
    # Check if 'Event' column exists
    if 'Event' not in data.columns:
        print("Warning: 'Event' column is missing. Skipping coldStart processing.")
        return data  # Return unchanged data
    
    # Apply transformation if 'Event' exists
    data['output_coldStart'] = data.apply(
        lambda x: None if x['Event'] != "FUNCTION_END" else 
                  ('ColdStart' if x['output_coldStart'] == 1 else "WarmStart"),
        axis=1
    )
    return data

def filterAWSExtract(data):
    data = data.copy()
    comparison_date = pd.Timestamp('2024-08-22')
    data['startTime'] = pd.to_datetime(data['startTime'])

    print(pd.to_datetime(data['startTime']))

    
    workflows = data[(data['output_provider'] == 'AWS') &
                (data['function'] == 'extract') &
                (data['output_region'] != 'us-east-1') &
                (data['startTime'] >= comparison_date)]['workflow_id']
    data= data[~data['workflow_id'].isin(workflows)]
    
    return data


def replace_values(row, aws_lookup):
    match = aws_lookup[(aws_lookup['RTT'] == row['RTT']) & (aws_lookup['output_provider']==row['output_provider']) & 
                       (aws_lookup['function']==row['function']) & (aws_lookup['Concurrency']==row['Concurrency'])]
    
    if not match.empty:
        
        row['output_execution'] = match['output_execution'].iloc[0]  
        row['output_coldStart'] = match['ColdStart'].iloc[0]     
    return row

def cacl_exec(dframe_aws):
    
    workflow_execution_map = (
        dframe_aws
        .sort_values(by='startTime', ascending=True)  
        .groupby(['output_provider', 'output_region', 'Concurrency', 'function','output_timeOfDay'])[['workflow_id', 'startTime','Event']]
    )
    func_exec_map = {}
    for gr,t in workflow_execution_map:
        print(t)
        for idx,workflow_id in enumerate(t['workflow_id'].unique()):
            func_exec_map[workflow_id] = idx+1


    return func_exec_map
def assign_execution(x,map):
    if x['output_provider'] == "AWS":
        return map.get(x['workflow_id'], x['output_execution'])
    return x['output_execution']

# Update 'output_execution' column in the DataFrame

if __name__ == "__main__":
    df = pd.read_csv('../experiments/experiments20241220-091750.csv').set_index("_id")
    df = df[df['workflow_id']!= 1734619168009]
    df = df[df['workflow_id']!= 1734619130501]
    df = calculateTimeOfDay(df)
    df['function'] = df['functionName']
    df['Concurrency'] = df['maxLoopCounter']+1
    df = coldStart(df)   

    df = markDelayedWarmstarts(df)  
    

    print(df.info())
    df.to_csv(f'../experiments/newAWSDATA2.csv',index="_id")

