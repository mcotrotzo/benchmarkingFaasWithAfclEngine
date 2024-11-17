import argparse

from src.deployer.deployer import deploy,destroy

from src.invoker.scriptExperiment import runExperiment
from src.mongo_to_csv_converter.mongoDB import returnDataframe

from pathlib import Path
import time
from src.utils.utils import handle_error
import pandas as pd
from src.anaylzer.analyzer import App

def parse_input():
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode","--mode", choices=['destroy','deploy','analyze','invoke','all'],
                        help="If you choose all it will be first deployed,invoked,and and the analyzer will be started",required=True)

    return parser.parse_args().mode



def tool():
    mode = parse_input()
    dir_path =  Path(__file__).parent
    terr_path = dir_path / 'terraform/'
    df = pd.DataFrame({})
    if mode  == 'destroy':
        try:
            print(terr_path)
            destroy(dest_terraform_path_folder=terr_path)
            return
        except Exception as e:
            handle_error(e)
            return

    if mode == 'deploy' or mode=='all':
        try:
            deploy(dest_terraform_path_folder=terr_path)

        except Exception as e:
            handle_error(e)
            return

    if mode == 'invoke' or mode=='all':
        try:
            runExperiment()
            output_dir = 'experiments'
            output_file = f'experiments{time.strftime("%Y%m%d-%H%M%S")}.csv'
            output_path = dir_path / output_dir / output_file
            df = returnDataframe()
            df.to_csv(f'{output_path}')
        except Exception as e:
            handle_error(e)
            return
        
    if mode=='analyze' or mode=='all':
        app = App()
        app.mainloop()

if __name__ == "__main__":
    tool()