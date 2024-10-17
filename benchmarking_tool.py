import argparse
import os
from src.deployer.deployer import deploy,destroy
import subprocess
from src.invoker.scriptExperiment import runExperiment
import logging
import streamlit as st
from os.path import join, dirname
from pathlib import Path

from src.utils.utils import handle_error

def parse_input():
    parser = argparse.ArgumentParser()

    parser.add_argument("--mode","--mode", choices=['destroy','deploy','analyze','invoke','all'],
                        help="If you choose all it will be first deployed,invoked,and and the analyzer will be started",required=True)

    return parser.parse_args().mode



def tool():
    mode = parse_input()
    dir_path =  Path(__file__).parent
    terr_path = dir_path / 'terraform/'
    if mode  == 'destroy':
        try:
            destroy(dest_terraform_path_folder=terr_path)
            return
        except Exception as e:
            handle_error(e)
            return

    if mode == 'deploy' or mode=='all':
        try:
            deploy(dest_terraform_path_folder=terr_path)
            print("Herer")
        except Exception as e:
            handle_error(e)
            return

    if mode == 'invoke' or mode=='all':
        try:
            runExperiment()
        except Exception as e:
            handle_error()
            return
    if mode=='analyze' or mode=='all':
        subprocess.run(['streamlit','run','./src/analyzer/anaylzer.py'])

if __name__ == "__main__":
    tool()