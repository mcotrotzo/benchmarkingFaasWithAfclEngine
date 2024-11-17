import plotly.express as px
import pandas as pd
from PIL import Image, ImageTk

from .formcreator import ConfigTypes
from .plot import Plot
import tkinter as tk
from tkinter.ttk import Combobox, Checkbutton,Radiobutton
class BoxPlot(Plot):
    def __init__(self, parent_app):
        super().__init__(parent_app)



    def get_plotly_function(self):
       return px.box

class HistPlot(Plot):
    def __init__(self, parent_app):
        super().__init__(parent_app)

    def get_plotly_function(self):
        return px.histogram

class TimeLinePlot(Plot):
    def __init__(self, parent_app):
        super().__init__(parent_app)


    def set_x_field(self):
        cols = self.parent_app.model.df.columns.toList()
        self.plot_options.create_form_member(widget_type=Combobox, id='x_start', title='X_Start',
                                             values=cols,
                                             config_type = ConfigTypes.PLOT,textvariable=tk.StringVar()
                                             )
        self.plot_options.create_form_member(widget_type=Combobox, id='x_end', title='X_End',
                                             values=cols,
                                             textvariable=tk.StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )


    def get_plotly_function(self):

        return px.timeline