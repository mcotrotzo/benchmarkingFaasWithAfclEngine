import streamlit as st
import time
import json
import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from plotObjects.boxplot import getBoxplots, getTimeLinePlots
from streamlit_ace import st_ace
from streamlit_dynamic_filters import DynamicFilters


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def syncState(uploaded_session_state: dict):
    if uploaded_session_state == None:
        return
    for key, value in uploaded_session_state.items():
        if key == 'NewPlotButton':
            continue
        st.session_state[key] = value
    return json.dumps(uploaded_session_state)

def uploadState():
    uploaded_file = st.file_uploader("Load inputs from file", type="json", accept_multiple_files=False)
    if uploaded_file is not None:
        state = json.loads(uploaded_file.getvalue())
        return state

def downloadState():
    filename = st.text_input('Enter a Filename for saving the settings!')

    serializable_state = {}
    for key, value in st.session_state.items():
         if key == 'plot_data':
             continue
         if isinstance(value, (str, int, float, list, dict, bool)):
            serializable_state[key] = value

    try:
        state = json.dumps(serializable_state)
        
        st.download_button("Save inputs to file", state, file_name=f'{filename}{time.strftime("%Y%m%d-%H%M%S")}.json')
    except TypeError as e:
        st.error(f"Error serializing session state: {e}")
        return

def getPlot(df, option, idx):
    if df.empty:
        st.write("No query executed. Dataset is empty!")
        return

    if option == 'Box Plot':
        x_axis = st.selectbox("Select X-axis", df.columns, key=f'box_x_axis_{idx}')
        y_axis = st.selectbox("Select Y-axis", df.columns, key=f'box_y_axis_{idx}')
        color_axis = st.selectbox("Select Color (optional)", [None] + list(df.columns), key=f'box_color_axis_{idx}')
        facet_row = st.selectbox("Select Facet Row (optional)", [None] + list(df.columns), key=f'box_facet_row_{idx}')
        facet_col = st.selectbox("Select Facet Column (optional)", [None] + list(df.columns), key=f'box_facet_col_{idx}')
        box_mode = st.selectbox("Select Box Mode", ['group', 'overlay'], key=f'box_mode_{idx}')
        height = st.slider("Height", min_value=100, step=50, max_value=10000, key=f'box_height_{idx}')
        width = st.slider("Width", min_value=100, step=50, max_value=10000, key=f'box_width_{idx}')

        figure = getBoxplots(df, x_axis, y_axis, color_axis, facet_row, facet_col, box_mode, height, width)
        return figure
    
    if option == 'Timeline':
        x_axis = st.selectbox("Select X-axis-start-time", df.columns, key=f'timeline_x_axis_start_{idx}')
        x_axis_end = st.selectbox("Select X-axis-end-time", df.columns, key=f'timeline_x_axis_end_{idx}')
        y_axis = st.selectbox("Select Y-axis", df.columns, key=f'timeline_y_axis_{idx}')
        color_axis = st.selectbox("Select Color (optional)", [None] + list(df.columns), key=f'timeline_color_axis_{idx}')
        facet_row = st.selectbox("Select Facet Row (optional)", [None] + list(df.columns), key=f'timeline_facet_row_{idx}')
        facet_col = st.selectbox("Select Facet Column (optional)", [None] + list(df.columns), key=f'timeline_facet_col_{idx}')
        height = st.slider("Height", min_value=100, step=50, max_value=10000, key=f'timeline_height_{idx}')
        width = st.slider("Width", min_value=100, step=50, max_value=10000, key=f'timeline_width_{idx}')

        figure = getTimeLinePlots(df, x_start=x_axis, x_end=x_axis_end, y=y_axis, color=color_axis, facet_row=facet_row, facet_col=facet_col, height=height, width=width)
        return figure


st.set_page_config(layout='wide')

state = uploadState()
if st.button("Sync state"):
    syncState(state)

if 'plots' not in st.session_state:
    st.session_state['plots'] = 0
if 'plot_data' not in st.session_state:
    st.session_state['plot_data'] = {}


with open('config.json') as f:
    config = json.load(f)
    sql_config = config['sql']
    DATABASE_URL = f"mysql+pymysql://{sql_config['username']}:{sql_config['password']}@{sql_config['host']}:{sql_config['port']}"
    engine = create_engine(DATABASE_URL)
    insp = inspect(engine)
    db_list = insp.get_schema_names()


with st.sidebar:
    database = st.sidebar.selectbox(key='databaseSideBar', label="Please select an option", options=db_list if db_list else ['No Database!'])
    if database:
        tables = insp.get_table_names(schema=database)
        st.sidebar.subheader(f"Tables in {database}:")
        for table in tables:
            st.sidebar.markdown(f'{table}')
            columns = insp.get_columns(table, schema=database)
            st.sidebar.dataframe(columns)


def fetch_data(query, database_url):
    with create_engine(database_url).connect() as conn:
        result = conn.execute(text(query))
        return pd.DataFrame(result.fetchall(), columns=result.keys())


def addNewPlot():
    st.session_state['plots'] += 1

plot_container = st.container()
for idx in range(st.session_state.plots):
    st.subheader(f"SQL Editor for Plot {idx+1}")
    

    query_content = st_ace(language='sql', keybinding='vscode', min_lines=10, key=f"query_{idx}")
    st.write(f"Query for Plot {idx+1}: {query_content}")
    

    if query_content:
        try:
            df = fetch_data(query_content, DATABASE_URL + f"/{database}")
            st.session_state['plot_data'][idx] = df.to_dict()
        except Exception as e:
            st.error(f"An error occurred while fetching data for plot {idx+1}: {str(e)}")

    if idx in st.session_state['plot_data']:
        df = st.session_state['plot_data'][idx]
        df = pd.DataFrame(df)
        st.subheader(f"Query Results for Plot {idx+1}")
        st.dataframe(df)

        option = st.selectbox(label='Select Plot Type', options=('Box Plot', 'Timeline'), key=f'SelectPlot{idx}')
        if option:
            figure = getPlot(df=df, idx=idx, option=option)
            st.plotly_chart(figure, key=f'Figure{idx}')


plot_container.button("Add new plot", key='NewPlotButton', on_click=addNewPlot)

downloadState()
