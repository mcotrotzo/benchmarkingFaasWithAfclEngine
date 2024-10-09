import json
import os
import pandas as pd
import pygwalker as pyg
from pygwalker.data_parsers.database_parser import Connector
import subprocess
def generate_visualization():
    with open(f'config.json') as f:
        config = json.load(f)
    sql_config = config['sql']
    DATABASE_URL = f"mysql+pymysql://{sql_config['username']}:{sql_config['password']}@{sql_config['host']}:{sql_config['port']}/{sql_config['db_name']}"
    conn = Connector(
        f"{DATABASE_URL}",
        "SELECT * FROM workflows"
    )
    walker = pyg.walk(conn)


    html_code = walker.to_html()

    return html_code

def open_jupyter_notebook():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    subprocess.Popen(["jupyter", "notebook"])

if __name__ == "__main__":
    open_jupyter_notebook()

