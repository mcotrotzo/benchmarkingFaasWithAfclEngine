import argparse
import os
from src.deployer.deployer import deploy,destroy
import subprocess
from src.invoker.scriptExperiment import runExperiment
import logging
import streamlit as st
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        try:
            deploy()
        except Exception as e:
            logging.error(e)
            return

    if mode == 'invoke' or mode=='all':
        try:
            runExperiment()
        except Exception as e:
            logging.error(e)
            return
    if mode=='analyze' or mode=='all':
        subprocess.run(['streamlit','run','./src/analyzer/anaylzer.py'])

if __name__ == "__main__":
    tool()