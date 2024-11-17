from pandastable import Table, TableModel, ImportDialog, ToolBar
from .boxplot import BoxPlot,TimeLinePlot,Plot,HistPlot
import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import PanedWindow,Combobox
from tkinter.filedialog import asksaveasfile,askopenfilename
from pandasql import sqldf
import pandas as pd

from .toolbar import CustomToolbar, ChildToolBar, CustomChildToolBar


class CustomTable(Table):
    def __init__(self, parent=None, model=None, dataframe=None, width=None, height=None,
                 rows=20, cols=5, showtoolbar=False, showstatusbar=False,
                 editable=True, enable_menus=True, **kwargs):
        self.plotly_pf = None
        self.sql_window  = None
        self.select_plot_window = None

        super().__init__(parent=parent,
                         showtoolbar=showtoolbar,
                         showstatusbar=showstatusbar,
                         model=model,
                         dataframe=dataframe,
                         width=width,
                         height=height,
                         editable=editable, enable_menus=enable_menus, rows=rows, cols=cols, **kwargs)
        self.unbind_all("<Return>")

    def test(self,event):
        print(event.widget)
    def import_dialog(self):
        file_path = askopenfilename(defaultextension='.csv',title='Import csv file',filetypes=[("CSV Document","*.csv")])
        if file_path:
            df = pd.read_csv(file_path)
            self.updateModel(TableModel(df))
            self.redraw()
    def show(self, callback=None):
        super().show(callback=callback)
        if hasattr(self, 'toolbar'):
            self.toolbar.destroy()
            self.toolbar = CustomToolbar(parent=self.parentframe, parentapp=self)
            self.toolbar.grid(row=0, column=3, rowspan=2, sticky='news')


    def createChildTable(self, df, title=None, index=False, out=False):
        self.closeChildTable()
        if out == True:
            win = tk.Toplevel()
            x, y, w, h = self.getGeometry(self.master)
            win.geometry('+%s+%s' % (int(x + w / 2), int(y + h / 2)))
            if title != None:
                win.title(title)
        else:
            win = tk.Frame(self.parentframe)
            win.grid(row=self.childrow, column=0, columnspan=2, sticky='news')
        self.childframe = win
        newtable = self.__class__(win, dataframe=df, showtoolbar=0, showstatusbar=1)
        newtable.parenttable = self
        newtable.adjustColumnWidths()
        newtable.show()
        toolbar = CustomChildToolBar(win, newtable)
        toolbar.grid(row=0, column=3, rowspan=2, sticky='news')
        self.child = newtable
        if hasattr(self, 'pf'):
            newtable.pf = self.pf
        if index == True:
            newtable.showIndex()
        return

    def open_config_window(self):
        if self.select_plot_window and self.select_plot_window.winfo_exists():
            self.select_plot_window.destroy()
        self.select_plot_window = tk.Toplevel(self)
        self.select_plot_window.geometry("300x150")
        paned_window = PanedWindow(self.select_plot_window)
        paned_window.pack(fill='both', expand=True)
        plot_type_var = tk.StringVar(value="BoxPlot")

        plot_label = tk.Label(paned_window, text="Choose Plot Type:")
        paned_window.add(plot_label)

        plot_types = ["BoxPlot", "HistPlot", "TimeLinePlot"]
        plot_dropdown = Combobox(self.select_plot_window, textvariable=plot_type_var, values=plot_types)

        paned_window.add(plot_dropdown)

        submit_button = tk.Button(self.select_plot_window, text="Submit", command=lambda: self.confirm_plot_type(plot_type_var.get()))
        paned_window.add(submit_button)
    def confirm_plot_type(self, plot_type):
       if self.plotly_pf and self.plotly_pf.config_window and  self.plotly_pf.config_window.winfo_exists():
           self.plotly_pf.config_window.destroy()
       if plot_type == "BoxPlot":
           self.plotly_pf = BoxPlot(self)
       elif plot_type == "HistPlot":
           self.plotly_pf = HistPlot(self)
       elif plot_type == "TimeLinePlot":
           self.plotly_pf = TimeLinePlot(self)

       self.select_plot_window.destroy()
       self.plotly_pf.open_configuration_window()



    def execute_query(self):
        df = self.model.df
        query = self.query_text.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("Warning",parent=self.sql_window, message="Please enter a SQL query.")
            return
        try:
            result_df = sqldf(query, locals())
            result = messagebox.askquestion("Query is valid!","Create a new table!",parent=self.sql_window)
            if result and result == 'no':
                self.updateModel(TableModel(result_df))
                self.redraw()
                return
            self.createChildTable(result_df, 'Query result', index=True)
        except Exception as e:
            messagebox.showerror("Error", parent = self.sql_window,message=f"An error occurred:\n{e}")
    def pandas_sql_query(self):
        if self.sql_window and self.sql_window.winfo_exists():
            self.sql_window.destroy()
        self.sql_window = tk.Toplevel(self)
        self.sql_window.grab_set()
        self.paned_window = tk.PanedWindow(self.sql_window,orient='vertical')
        self.paned_window.pack(fill=tk.BOTH,expand=True)

        self.query_label = tk.Label(self.paned_window, text="Enter SQL Query! Note: Syntax is SQL-lite and the table is called df! For example SELECT * from df")
        self.paned_window.add(self.query_label,stretch='never')

        self.upload_query_button = tk.Button(self.paned_window,text='Upload Query',command=self.upload_query)
        self.paned_window.add(self.upload_query_button)

        self.query_text = tk.Text(self.paned_window, height=5, width=80)
        self.paned_window.add(self.query_text,stretch='always')

        self.execute_button = tk.Button(self.paned_window, text="Execute SQL Query", command=self.execute_query)
        self.paned_window.add(self.execute_button,stretch='never')

        self.download_query_button = tk.Button(self.paned_window,text='Download Query',command=self.download_query)
        self.paned_window.add(self.download_query_button,stretch='never')


    def upload_query(self):
        filepath = askopenfilename(parent=self.sql_window,defaultextension='.txt',title='Import query txt file',filetypes=[("Text Document","*.txt")])

        with open(filepath, 'r') as file:
            query_content = file.read()
            self.query_text.delete(1.0, tk.END)
            self.query_text.insert(tk.END, query_content)
    def download_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        file_path = asksaveasfile(parent=self.sql_window,initialfile='query.txt',defaultextension=".txt",filetypes=[("Text Document","*.txt")])
        if file_path:
            file_path.write(query)

    def plotly(self):
        self.open_config_window()
    def remove_empty_rows(self):

        self.model.df.dropna(how="all", inplace=True)
        self.model.df.reset_index(drop=True, inplace=True)

    def export_csv(self):
        df = self.model.df.dropna(how="all")
        file_path = asksaveasfile(initialfile="Export.csv",defaultextension=".csv",filetypes=[("CSV Documents","*.csv")])
        if file_path:
            df.to_csv(file_path,index=False)
    def redraw(self, event=None, callback=None):
        super().redraw(event, callback)
        if hasattr(self, 'plotly_pf') and self.plotly_pf and self.plotly_pf.config_window and self.plotly_pf.config_window.winfo_exists():
            self.plotly_pf.open_configuration_window()

