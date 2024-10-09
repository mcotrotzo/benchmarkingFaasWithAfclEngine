import subprocess
import os
import json
from src.invoker.dataManager.dataManager import tranformData
script_dir = os.path.dirname(os.path.abspath(__file__))


def get_input_json(input_json: str):
    print(input_json)
    with open(f'{script_dir}/workflowData/{input_json}', 'r') as file:
        json_dict = json.load(file)
    return json_dict

def save_input_with_execution(input_dict: dict, execution: int):
    input_dict['execution'] = execution

    for key, value in input_dict.items():
        if isinstance(value, str):
            try:
                input_dict[key] = json.loads(value)
            except json.JSONDecodeError:
                input_dict[key] = value

    with open(f'{script_dir}/runInput.json', 'w') as file:
        json.dump(input_dict, file, indent=4)

    return 'runInput.json'



def runner(workflow, input_json:str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    input_dict = get_input_json(input_json)
    repetition = input_dict.get('repetition', 1)

    for rep in range(repetition):
        input_file = save_input_with_execution(input_dict=input_dict, execution=rep+1)
        command = ["java", "-jar", "ee.jar", f'./workflowData/{workflow}', input_file]
        subprocess.run(command)
        print(command)


def runExperiment():
    path = os.path.join(script_dir, './workflowData')
    experiments = sorted(os.listdir(path))
    for i in range(0, len(experiments), 2):
        workflow = experiments[i]
        input_json = experiments[i+1]

        if workflow.endswith('.json'):
            temp_input = workflow
            workflow = input_json
            input_json = temp_input


        runner(workflow, input_json)
    tranformData()

if __name__ == "__main__":
    runExperiment()
