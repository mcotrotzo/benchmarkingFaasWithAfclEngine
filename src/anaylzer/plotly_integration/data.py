import streamlit as st
import streamlit_ace as st_ace
from streamlit_ace import LANGUAGES
import pandasql as psql
import pandas as pd
from .sessionManager import SessionManger
def run_query(query, dataframe):
    return psql.sqldf(query, locals())



class Component:
    def __init__(self,tab,dataframe_session_manager:SessionManger,sheet_key) -> None:
        self.container = tab
        self.df_manager = dataframe_session_manager
        self.options = {}
        self.sheet_key = sheet_key
        
    def set_dataframe(self,df):
        
        self.df_manager.set_state(df)
    
    def get_dataframe(self):
        
        return self.df_manager.get_state_func()()
    
    def get_options(self):
        return self.options.keys()
    def get_func_options(self,options):
        return self.options[options]()
    
class Data(Component):
    
    def __init__(self,tab,dataframe_session_manager:SessionManger,sheet_key) -> None:
        super().__init__(tab=tab,sheet_key=sheet_key,dataframe_session_manager=dataframe_session_manager)
        self.options = {"SQL_QUERY":self.sql_query,"Aggregate":self.aggregate}
        
    def sql_query(self):
        with self.container:
            if f"{self.sheet_key}query_sql" not in st.session_state:
                st.session_state[f"{self.sheet_key}query_sql"] = ""
            if self.get_dataframe().empty:
                st.warning("No Data please upload a csv file!")
                return

            query_content = st_ace.st_ace(language=LANGUAGES[145], keybinding='vscode',placeholder="The datatable is called dataframe! For Example: SELECT * from dataframe", 
                                          min_lines=10, key=f"{self.sheet_key}query_sql",value=st.session_state[f"{self.sheet_key}query_sql"])
            st.button(label="Run Query",key=f"RunQueryButton{self.sheet_key}",on_click=self.do_query,args=[query_content])
                
    
    def do_query(self,query_content):
        if query_content:
            try:
                result = run_query(query_content, self.get_dataframe())
                self.set_dataframe(result)
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter a SQL query.")
            
    def aggregate(self):
        with self.container:
            col1,col2,col3 = self.container.columns(3)
           
            with col1:

                group_by_col = st.multiselect(
                    label="Group By Column",
                    options=self.get_dataframe().columns.tolist(),
                    key=f"{self.sheet_key}group_by_col"
                )
            with col2:
                agg_col = st.multiselect(
                    label="Aggregate Column",
                    options=self.get_dataframe().columns.tolist(),
                    key=f"{self.sheet_key}agg_col"
                )
            with col3:
                agg_func = st.multiselect(
                    label="Aggregation Function",
                    options=["sum", "mean", "max", "min", "count","median","std"],
                    key=f"{self.sheet_key}agg_func"
                )
            button = st.button(label="Aggregate", key=f"AggregationButton{self.sheet_key}",on_click=self.do_aggregate,args=[group_by_col,agg_col,agg_func])
       
                
    def do_aggregate(self,group_by_col,agg_col,agg_func):
        if group_by_col and agg_col and agg_func:
            try:
                agg_dict = {
                    col: agg_func for col in agg_col
                }
                
                aggregated_df = (
                    self.get_dataframe().groupby(group_by_col)
                    .agg(agg_dict)
                )

                aggregated_df.columns= ['_'.join(x) for x in list(zip(aggregated_df.columns.get_level_values(0), aggregated_df.columns.get_level_values(1)))]
                aggregated_df = aggregated_df.reset_index()
                
                self.set_dataframe(aggregated_df)
            except Exception as e:
                st.error(f"Error during aggregation: {e}")
        else:
            st.warning("Please select all required options.")

            
                
class FileManager(Component):
    def __init__(self,tab,dataframe_session_manager:SessionManger,sheet_key) -> None:
        super().__init__(tab,dataframe_session_manager=dataframe_session_manager,sheet_key=sheet_key)
        
        self.options = {'Upload CSV':self.upload_csv,"Download Query":self.download_query,"Upload_Query":self.upload_query}
        
    
    def upload_file(self,type,label,key,func_onchange):
        st.file_uploader(
            label=label,
            type=type,
            accept_multiple_files=False,
            key=f"{key}",
            on_change=func_onchange
        )
    def process_upload(self):
            uploaded_file = st.session_state.get(f"{self.sheet_key}_uploaded_file")
            if uploaded_file:
                try:
                    df = self._load_csv(uploaded_file)
                    self.set_dataframe(df)
                    st.success(f"File '{uploaded_file.name}' uploaded and processed successfully!")
                except Exception as e:
                    st.error(f"Failed to read CSV: {str(e)}")
            
    def upload_csv(self):
        with self.container:
            self.upload_file(type=['csv'],label="Upload CSV",key=f"{self.sheet_key}_uploaded_file",func_onchange=self.process_upload)
 
    def _load_csv(self,_file):
        return pd.read_csv(_file)
    
    def download_query(self):
       
        query_content = st.session_state.get(f"{self.sheet_key}query_sql",'')
        if query_content:
                st.download_button(
                    label="Download Query Content",
                    data=query_content,
                    file_name=f"query_{self.sheet_key}.txt",
                    mime="text/plain",
                    key=f"DownloadQueryContent{self.sheet_key}"
                )

    def parse_query(self):
        uploaded_file = st.session_state.get(f"{self.sheet_key}UploadQuery")
        if uploaded_file:
            try:
                content = uploaded_file.getvalue().decode("utf-8")
                st.session_state[f"{self.sheet_key}query_sql"] = content
                st.success("Query content uploaded and updated successfully!")
            except Exception as e:
                st.error(f"Error processing uploaded query file: {e}")
    
    def upload_query(self):
        with self.container:
            self.upload_file(type=['txt'],label="Upload Query",key=f"{self.sheet_key}UploadQuery",func_onchange=self.parse_query)
            
    
    
            
        