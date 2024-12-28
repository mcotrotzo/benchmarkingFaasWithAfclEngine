import streamlit as st
from .data import FileManager,Data
from .sessionManager import SessionManger
import pandas as pd
from .plot import BoxPlot,HistPlot,TimeLinePlot,LinePlot,ScatterPlot,BarPlot,PiePlot,ViolinPlot,ScatterPlot3D


class MenuBar:
    def __init__(self, sheet_key: int,tab,df:SessionManger):
        self.sheet_key = sheet_key
        self.tab = tab
        self.df = df

    def load(self):
        col1,col2= self.tab.columns(2)
        file = FileManager(col1,self.df,self.sheet_key)
        selected = col1.selectbox(label="File",options=file.get_options(),key=f'File_selection{self.sheet_key}')
        if selected:
            file.get_func_options(selected)
        data = Data(col2,dataframe_session_manager=self.df,sheet_key=self.sheet_key)
        data_selected = col2.selectbox(label="Data",options=data.get_options(),key=f'Data_selection{self.sheet_key}')
        if data_selected:
            data.get_func_options(data_selected)

class Sheet:
    def __init__(self, key_id,tab,sheet_manager_session):
       
        self.key_id = key_id
        self.tab = tab
        self.sheet_manager_session = sheet_manager_session
        self.dataframe_session_manager = SessionManger(f"{self.key_id}_dataframe",default_value=pd.DataFrame({}))
    

    def load_sheet(self):
        menubar = MenuBar(sheet_key=self.key_id,tab=self.tab,df=self.dataframe_session_manager)
        menubar.load()
        df = self.dataframe_session_manager.get_state_func()()
        st.data_editor(self.dataframe_session_manager.get_state_func()(),key=f"Table{self.key_id}")
        
        plot_type = self.tab.selectbox(
        "Select Plot Type", ["Box Plot", "Histogram", "Timeline", "Line Plot", "Scatter Plot","Bar Plot","Pie Plot","Violin Plot","Scatter 3D"], key=f"SelectionPlot{self.key_id}"
        )
        plot = None
        if plot_type == "Box Plot":
            plot = BoxPlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type == "Histogram":
            plot = HistPlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type == "Timeline":
            plot = TimeLinePlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type == "Line Plot":
            plot = LinePlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type == "Scatter Plot":
            plot = ScatterPlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type == "Bar Plot":
            plot = BarPlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type =="Pie Plot":
            plot = PiePlot(df=df,container=self.tab,sheet_key=self.key_id)
        elif plot_type=="Violin Plot":
            plot = ViolinPlot(df=df,container=self.tab,sheet_key=self.key_id)
        else:
            plot = ScatterPlot3D(df=df,container=self.tab,sheet_key=self.key_id)
        plot.get_form()
        plot.render()
class SheetManager:
    
    def __init__(self):
        self.sheet_manager_session_key = 'Sheets_Analyzer'
        self.session_manager = SessionManger(self.sheet_manager_session_key,['Sheet_1'])
        self.sheets = self.session_manager.get_state_func()
        

    def load(self):
        st.sidebar.button(label="Add New Sheet", on_click=self.add_new_sheet, key="add_sheet_button")
        self.load_sheets()


    def load_sheets(self):
        tabs = st.tabs(self.sheets())
        for idx,tab in enumerate(tabs):
            with tab:
                sheet = Sheet(key_id=f"Sheet_{idx+1}",tab=tab,sheet_manager_session=self.session_manager)
                sheet.load_sheet()
    def add_new_sheet(self):
        idx = len(self.sheets())
        new_tab = f"Sheet_{idx+1}"
        self.session_manager.set_state(self.sheets() + [new_tab])
        
        
    