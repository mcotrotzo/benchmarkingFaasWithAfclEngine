import tkinter.filedialog
from .formcreator import FormMember, PlotlyFormCreator, ConfigTypes, VariableType,Customframe
import tkinter as tk
from tkinter.ttk import Combobox, Checkbutton,Radiobutton
from tkinter import messagebox,StringVar,IntVar,colorchooser
from PIL import Image, ImageTk
from typing import final
import tempfile


class Plot:
    def __init__(self, parent_app):
        self.individual_config = None
        self.color_map = {}
        self.image_label = None
        self.image_copy = None
        self.img = None
        self.update_y_frame = None
        self.update_x_frame = None
        self.layout_options_frame = None
        self.y_axis_options = None
        self.x_axis_options = None
        self.layout_options = None
        self.plot_options = None
        self.plot_options_frame = None
        self.layout_form = None
        self.config_frame = None
        self.left_frame = None
        self.paned_window = None
        self.parent_app = parent_app
        self.tkimage = None
        self.fig = None
        self.color_window = None
        self.config_window = None
        self.config_axes_button_text = StringVar()
        self.config_axes_button_text.set('Config Axes')

    def open_configuration_window(self):
        if self.config_window is None or not self.config_window.winfo_exists():
            self.config_window = tk.Toplevel(self.parent_app)
            self.config_window.geometry('600x400')

            self.main_frame = tk.Frame(self.config_window)
            self.main_frame.pack(side='top', fill='both', expand=True)


            self.left_scrollable = Customframe(self.main_frame)
            self.plot_scrollable = Customframe(self.main_frame)
            self.right_scrollable = Customframe(self.main_frame)


            self.left_scrollable.pack(side='left', fill=tk.Y, expand=False)
            self.right_scrollable.pack(side='right', fill=tk.Y, expand=False)
            self.plot_scrollable.pack(side='top', fill=tk.BOTH, expand=True)


            config_windos = {
                ConfigTypes.PLOT: self.left_scrollable,
                ConfigTypes.LAYOUT: self.right_scrollable
            }


            self.plot_options = PlotlyFormCreator(
                submit_command=self.create_plot, frames=config_windos, frame_for_submit_button=self.plot_scrollable
            )

        self.config_window.lift()
        self._create_config_window()


    def _create_config_window(self):
        self.get_plot_configuration()
        self.get_layout_configuration()
        self.plot_options.create_form()

    def set_x_field(self):

        self.plot_options.create_form_member(widget_type=Combobox, id='x', title='X_Value',
                                             values=self.parent_app.model.df.columns.tolist(),
                                             textvariable=StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )

    def set_y_field(self):
        self.plot_options.create_form_member(widget_type=Combobox, id='y', title='Y_Value',
                                             values=self.parent_app.model.df.columns.tolist(),
                                             textvariable=StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )

    def set_facet_row(self):
        self.plot_options.create_form_member(widget_type=Combobox, id='facet_row', title='Facet_Row',
                                             values=self.parent_app.model.df.columns.tolist(),
                                             textvariable=StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )

    def set_facet_col(self):
        self.plot_options.create_form_member(widget_type=Combobox, id='facet_col', title='Facet_Col',
                                             values=self.parent_app.model.df.columns.tolist(),
                                             textvariable=StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )
    def set_color_field(self):
        self.plot_options.create_form_member(widget_type=Combobox, id='color', title='Color',
                                             values=self.parent_app.model.df.columns.tolist(),
                                             textvariable=StringVar(),
                                             config_type = ConfigTypes.PLOT
                                             )
    def set_color_discrete_map(self):
        color_widget = self.plot_options.get_widget(ConfigTypes.PLOT,'color')
        if not color_widget:
            return
        if hasattr(self,'menu_bar') and self.menu_bar:
            self.menu_bar.destroy()
            self.color_map = {}

        color_widget.add_bind('<<ComboboxSelected>>',lambda event: self.color_discrete_command(color_widget.get_value()))
        color_widget.add_bind('<Configure>', lambda event: self.handle_color_widget_state(color_widget))


    def handle_color_widget_state(self, color_widget):
        if color_widget.get_is_disabled():
            if hasattr(self,'menu_bar') and self.menu_bar:
                self.menu_bar.destroy()
                self.color_map = {}

    def color_discrete_command(self,selected_color):
        if not selected_color:
            return
        unique_values = self.parent_app.model.df[selected_color].dropna().unique()
        self.color_map = {}
        if hasattr(self,'menu_bar') and self.menu_bar:
            self.menu_bar.destroy()

        self.menu_bar = tk.Menu(self.config_window, tearoff=0)
        self.config_window['menu'] = self.menu_bar
        self.color_menu = tk.Menu(self.menu_bar)
        self.menu_bar.add_cascade(label="Change Color of color categories",menu=self.color_menu)
        for value in unique_values:
            self.color_menu.add_command(label=f"Choose color for '{value}'", command=lambda val=value:self.select_color(val))
    def select_color(self,value):
        color = colorchooser.askcolor(parent=self.config_window,title=f"Choose color for '{value}'")[1]
        if color:
            self.color_map[value] = color


    def set_height_field(self):
        self.plot_options.create_form_member(
            widget_type=tk.Scale, title="Figure Height",
            variable=IntVar(),
            from_=500, to=913, id='height',
            orient='horizontal',config_type=ConfigTypes.LAYOUT
        )

    def set_width_field(self):
        self.plot_options.create_form_member(
            widget_type=tk.Scale, title="Figure Width",
            variable=IntVar(),
            from_=500, to=1600, id='width',
            orient='horizontal',config_type=ConfigTypes.LAYOUT
        )

    def set_title_field(self):
        self.plot_options.create_form_member(
            widget_type=tk.Entry, title="Plot Title",
            textvariable =StringVar(),
            id='title',config_type=ConfigTypes.LAYOUT
        )


    def get_plot_configuration(self):
        self.set_x_field()
        self.set_y_field()
        self.set_facet_row()
        self.set_facet_col()
        self.set_color_field()
        self.set_color_discrete_map()

    def get_layout_configuration(self):
        self.set_height_field()
        self.set_width_field()
        self.set_title_field()


    def get_plotly_function(self):
        pass
    @final
    def plot_setting(self,plot_options,layout_options):
        try:
            if hasattr(self,'color_map') and self.color_map:
                self.fig = self.get_plotly_function()(self.parent_app.model.df,color_discrete_map=self.color_map, **plot_options)
            else:
                self.fig = self.get_plotly_function()(self.parent_app.model.df, **plot_options)

            if self.fig:
                self.fig.update_layout(**layout_options)
                self.plot_image(self.fig)

        except ValueError as e:
            if "wide-form data" in str(e):
                messagebox.showwarning(
                    title="Plot Creation Error",
                    message="It seems that columns have different data types because no x and y values were selected.\n\n"
                            "To avoid this error:\n"
                            "- Ensure at least one x or y value is selected.\n"
                            "- When x and y are empty, the index will be used as x, and all other columns will be used as y.\n"
                            "- If columns have different types, adjust them to be compatible for plotting.",
                    parent=self.config_window,
                )
            else:
                messagebox.showwarning(title="Plot Creation Error",message=str(e),parent=self.config_window)
        except Exception as e:
            messagebox.showwarning(title="Plot Creation Error",message=str(e),parent=self.config_window)

    def plot_image(self,fig):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as png:
            png_path = png.name
            png.write(fig.to_image())
        img = ImageTk.PhotoImage(Image.open(png_path))
        png.close()
        if hasattr(self,'plot') and self.plot and self.plot.winfo_exists():
            self.plot.configure(image=img)
            self.plot.image = img
        else:
            self.plot = tk.Label(self.plot_scrollable, image=img)
            self.plot.image = img
            self.plot_scrollable.add(self.plot)
        if not hasattr(self,'download_button') or not self.download_button:
            self.download_button = tkinter.Button(master=self.plot_scrollable,text="Open in browser to download the plot",
                                                  command=self.open_fig_as_html)
            self.plot_scrollable.add(self.download_button)

    def open_fig_as_html(self):
        if self.fig:
            self.fig.show()
    @final
    def create_plot(self, content,axis:StringVar):
        plot_options = content[ConfigTypes.PLOT]
        layout_options = content[ConfigTypes.LAYOUT]
        self.plot_setting(plot_options,layout_options)
        if self.fig:
            axis.set(str(sorted([e for e in self.fig.layout if e[1:5] == 'axis']+['all_x_axis','all_y_axis'])))











