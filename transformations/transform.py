import pandas as pd

def calculateTimeOfDay(df):
    df['output_timeOfDay'] = df['startTime'].apply(
        lambda x: 'Morning' if pd.to_datetime(x).hour < 18 and pd.to_datetime(x).hour >= 6 else 'Evening'
    ).astype(str)
    return df

def checkkColderColdstart(rtt):
    return ((rtt['output_coldStart'] == 'true') and 
            (rtt['output_serviceTime'] >= 5000) and 
            (rtt['output_provider'] == 'GCP') and 
            (rtt['functionName'] != 'recognition'))

def check_delayedwarmstart(row, group):
    return (row['output_coldStart'] == 0) and (row['output_startExecutionTime'] >= group['output_endExecutionTime'].min())

def markDelayedWarmstarts(data):
    data['output_startMode'] = data.apply(
        lambda x: 'delayedWarm' if check_delayedwarmstart(
            x, data[
                (data['output_provider'] == x['output_provider']) &
                (data['output_execution'] == x['output_execution']) &
                (data['output_timeOfDay'] == x['output_timeOfDay']) &
                (data['output_region'] == x['output_region']) &
                (data['maxLoopCounter'] == x['maxLoopCounter']) &
                ((data['functionName'] == x['functionName']))
            ]
        ) else 'colderColdStart' if checkkColderColdstart(x) else x['output_coldStart'], 
        axis=1
    )
    return data


if __name__ == "__main__":
    df = pd.read_csv('../src/analyzer/experiments/experiments20241019-165156.csv')
    print(df)
    df = calculateTimeOfDay(df)
    df = markDelayedWarmstarts(df)
    print(df.info())
    df.to_csv(f'../src/analyzer/experiments/experimentTransformed.csv')