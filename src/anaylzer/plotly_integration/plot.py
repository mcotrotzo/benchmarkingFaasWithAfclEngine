import streamlit as st
import plotly.express as px
import pandas as pd
import yaml
from dataclasses import dataclass
from typing import Union



class BasePlot:
    def __init__(self, df, container,sheet_key):
        self.df = df
        self.sheet_key = sheet_key
       
        self.plot_options = {}
        self.layout_options = {}
        self.plot_kwargs_options = {}
        self.layout_kwargs_options = {}
        
        self.container = container
        self.fig = None
        
        self.unshared_x_axis = False
        self.unshared_y_axis = False
        self.show_x_tick_labels = False
        self.show_y_tick_labels = False
  
    
    
    def get_layout_options(self):
        self.layout_options['height'] = st.slider("Height", 400, 900, 600, key=f"{self.sheet_key}height")
        self.layout_options['width'] = st.slider("Width", 400, 1200, 900, key=f"{self.sheet_key}width")
        self.layout_options['title'] = st.text_input("Plot Title", "My Plot", key=f"{self.sheet_key}title")
        self.unshared_x_axis = st.checkbox(label="Shared X",value=False,key=f"{self.sheet_key}_shared_x")
        self.unshared_y_axis = st.checkbox(label="Shared Y",value=False,key=f"{self.sheet_key}_shared_y")
        self.show_x_tick_labels = st.checkbox(label="ShowTickLabels X",value=False,key=f"{self.sheet_key}_tick_label_x")
        self.show_y_tick_labels = st.checkbox(label="ShowTickLabels Y",value=False,key=f"{self.sheet_key}_tick_label_y")

    def get_plot_options(self):
        self.plot_options['x'] = st.selectbox("X-Axis", options=[None] + list(self.df.columns), key=f"{self.sheet_key}x_axis")
        self.plot_options['y'] = st.selectbox("Y-Axis", options=[None] + list(self.df.columns), key=f"{self.sheet_key}y_axis")
        self.plot_options['color'] = st.selectbox("Color", options=[None] + list(self.df.columns), key=f"{self.sheet_key}color")
        self.plot_options['facet_row'] = st.selectbox("Facet_Row", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_row")
        self.plot_options['facet_col'] = st.selectbox("Facet Col", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_col")
        
        self.create_color_asker('color')
        
    def create_color_asker(self,color):
        color_column = st.session_state.get(f"{self.sheet_key}{color}",None)
       
        if color_column:
            unique_categories = self.df[color_column].dropna().unique()
            category_colors = self.plot_options['color_discrete_map'] if 'color_discrete_map' in self.plot_options else {}

            st.write("Customize Colors for Categories")
            for category in unique_categories:
                color_key = f"{self.sheet_key}_color_{category}"
                category_colors[category] = st.color_picker(f"Color for {category}", category_colors.get(category, "#000000"), key=f'{color_key}{self.sheet_key}')

          
            self.plot_options['color_discrete_map'] = category_colors

    def get_form(self):
        with self.container:
            form = st.form(key=f"{self.sheet_key}Plotly Form")
            col1, col2 = form.columns(2)
            with form:
                with col1:
                    st.write("Plot Configurations")
                    self.get_plot_options()

                with col2:
                    st.write("Layout Configurations")
                    self.get_layout_options()

                submitted = st.form_submit_button(label=f"Plot")
                
    def get_plotly_function(self):
        """Must be implemented in subclasses."""
        raise NotImplementedError

    def render(self):
       
       
        if not self.plot_options and not self.layout_options:
            self.container.warning("Please configure the plot.")
            return

        plot_func = self.get_plotly_function()

        self.container.write(str(self.plot_options))
        self.container.write(str(self.layout_options))
        
    
        try:
            fig = plot_func(self.df, **self.plot_options,**self.plot_kwargs_options)
            fig.update_layout(**self.layout_options,**self.layout_kwargs_options)
            
            
            if self.unshared_x_axis:
                fig.for_each_xaxis(lambda xaxis: xaxis.update(matches=None,showticklabels = self.show_x_tick_labels))
            if self.unshared_y_axis:
                fig.for_each_yaxis(lambda xaxis: xaxis.update(matches=None,showticklabels = self.show_y_tick_labels))
            self.container.plotly_chart(fig,key=f'Plotly{self.sheet_key}')
            
   
        except ValueError as e:
            if "wide-form data" in str(e):
                self.container.warning("Plot Creation Error: Ensure compatible data types or select X/Y values.")
            else:
                self.container.warning(f"Plot Creation Error: {e}")
        except Exception as e:
            self.container.warning(f"Error rendering plot: {e}")


class BoxPlot(BasePlot):
    def get_plotly_function(self):
        return px.box

class HistPlot(BasePlot):
    def get_plot_options(self):
       
        super().get_plot_options()
        self.plot_options['histnorm'] = st.selectbox("Histnorm", options=[None] + ['percent', 'probability', 'density', 'probability density'], key=f"{self.sheet_key}histnorm")
        self.plot_options['histfunc'] = st.selectbox("Histfunc", options=[None] + ['count', 'sum', 'avg', 'min', 'max'], key=f"{self.sheet_key}histfunc")
    def get_plotly_function(self):
        return px.histogram

class TimeLinePlot(BasePlot):
    def get_plot_options(self):
       
        self.plot_options['x_start'] = st.selectbox("X-Start", options=[None] + list(self.df.columns), key=f"{self.sheet_key}x_start")
        self.plot_options['x_end'] = st.selectbox("X-End", options=[None] + list(self.df.columns), key=f"{self.sheet_key}x_end")
        self.plot_options['y'] = st.selectbox("Y-Axis", options=[None] + list(self.df.columns), key=f"{self.sheet_key}y_axis")
        self.plot_options['color'] = st.selectbox("Color", options=[None] + list(self.df.columns), key=f"{self.sheet_key}color")
        self.plot_options['facet_row'] = st.selectbox("Facet_Row", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_row")
        self.plot_options['facet_col'] = st.selectbox("Facet Col", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_col")
        self.create_color_asker('color')
      
        
    def get_plotly_function(self):
        return px.timeline

class LinePlot(BasePlot):
    def get_plotly_function(self):
        return px.line

class ScatterPlot(BasePlot):
    def get_plotly_function(self):
        return px.scatter
    
class ScatterPlot3D(BasePlot):
    
    def get_plot_options(self):
       
        self.plot_options['x'] = st.selectbox("X-Start", options=[None] + list(self.df.columns), key=f"{self.sheet_key}x_start")
        self.plot_options['y'] = st.selectbox("Y-Axis", options=[None] + list(self.df.columns), key=f"{self.sheet_key}y_axis")
        self.plot_options['z'] = st.selectbox("Z-Axis", options=[None] + list(self.df.columns), key=f"{self.sheet_key}z_axis")
        self.plot_options['color'] = st.selectbox("Color", options=[None] + list(self.df.columns), key=f"{self.sheet_key}color")
        self.create_color_asker('color')
    def get_plotly_function(self):
        return px.scatter_3d
    
class BarPlot(BasePlot):
    def get_plotly_function(self):
        return px.bar

class PiePlot(BasePlot):
    def get_plot_options(self):
        self.plot_options['values'] = st.selectbox("Values", options=[None] + list(self.df.columns), key=f"{self.sheet_key}values")
        self.plot_options['names'] = st.selectbox("Names", options=[None] + list(self.df.columns), key=f"{self.sheet_key}names")
        self.plot_options['color'] = st.selectbox("Color", options=[None] + list(self.df.columns), key=f"{self.sheet_key}color")
        self.plot_options['facet_row'] = st.selectbox("Facet_Row", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_row")
        self.plot_options['facet_col'] = st.selectbox("Facet Col", options=[None] + list(self.df.columns), key=f"{self.sheet_key}facet_col")
        self.create_color_asker('color')
    def get_plotly_function(self):
        return px.pie
    
class ViolinPlot(BasePlot):
    def get_plotly_function(self):
        return px.violin


