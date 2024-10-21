import subprocess
import os
import json
import logging
from ..utils.utils import save_properties_file,load_config,save_json
import sys
from pathlib import Path
from ..settings import COLLECTION,DATABASE,HOST,PASSWORD,PORT,USERNAME
script_dir = Path(__file__).parent



def get_input_json(input_json: str):
    return load_config(script_dir / 'workflowData/' / input_json )

def save_input_with_execution(input_dict: dict, execution: int):
    input_dict['execution'] = execution

    for key, value in input_dict.items():
        if isinstance(value, str):
            try:
                input_dict[key] = json.loads(value)
            except json.JSONDecodeError:
                input_dict[key] = value
                sys.exit(f"Json decoding of {input_dict} failed!")

    save_json(input_dict,script_dir / 'runInput.json',mode='w')

    return 'runInput.json'



def runner(workflow, input_json:str):
    input_dict = get_input_json(input_json)
    repetition = input_dict.get('repetition', 1)

    for rep in range(repetition):
        input_file = save_input_with_execution(input_dict=input_dict, execution=rep+1)

        cw = os.getcwd()
        command = ["java", "-jar", "ee.jar", script_dir / 'workflowData' / workflow, input_file]
        print(command)
        try:
            os.chdir(script_dir)
            subprocess.run(command, check=True)
            os.chdir(cw)
        except subprocess.SubprocessError as e:
            os.chdir(cw)
            logging.error(f"AFCL failed with exit code {e.returncode}: {e}")
            sys.exit("Running Experiment failed")


 

def runExperiment():
    
    save_properties_file(script_dir / 'mongoDatabase.properties',
                         host = HOST,
                         collection = COLLECTION,
                         username=USERNAME,
                         password=PASSWORD,
                         port=PORT,
                         database=DATABASE)
    path = script_dir / 'workflowData'
    experiments = sorted(os.listdir(path))
    for i in range(0, len(experiments), 2):
        workflow = experiments[i]
        input_json = experiments[i+1]

        if workflow.endswith('.json'):
            temp_input = workflow
            workflow = input_json
            input_json = temp_input


        runner(workflow, input_json)

    
if __name__ == "__main__":
    runExperiment()
