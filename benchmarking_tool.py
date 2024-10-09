import argparse
import os
from src.deployer.deployer import deploy,destroy
from src.analyzer.anaylzer import open_jupyter_notebook
from src.invoker.scriptExperiment import runExperiment
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def parse_input():
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode","--mode", choices=['destroy','deploy','analyze','invoke','all'],
                        help="If you choose all it will be first deployed,invoked,and and the analyzer will be started",required=True)

    return parser.parse_args().mode



def tool():
    mode = parse_input()
    if mode  == 'destroy':
        destroy()
        return

    if mode == 'deploy' or mode=='all':
        deploy()
    if mode == 'invoke' or mode=='all':
        runExperiment()
    if mode=='analyze' or mode=='all':
        open_jupyter_notebook()

if __name__ == "__main__":
    tool()