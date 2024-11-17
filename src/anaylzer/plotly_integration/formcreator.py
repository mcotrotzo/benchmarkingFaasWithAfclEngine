import tkinter
import tkinter.simpledialog
from tkinter import Tk, PanedWindow, Button, Label, Entry, StringVar, IntVar, BooleanVar, DoubleVar, Variable
import enum
from typing import Dict, Tuple, List
from tkinter.ttk import Combobox
from tkinter import messagebox, commondialog
import awesometkinter
from tkinter.scrolledtext import ScrolledText
import yaml


class VariableType(enum.Enum):
    STRING = 'string'
    INTEGER = 'int'
    BOOLEAN = 'bool'
    DOUBLE = 'double'


class ConfigTypes(enum.Enum):
    PLOT = 'Plot Configuration'
    LAYOUT = 'Layout_Configuration'


class Customframe(awesometkinter.ScrollableFrame):
    def __init__(self, parent, orientation='vertical', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.widgets = []
        self.orientation = orientation

    def add(self, widget):

        self.widgets.append(widget)
        for widget in self.widgets:
            widget.pack_forget()
        for widget in self.widgets:
            if self.orientation == 'vertical':
                widget.pack(pady=5)
            elif self.orientation == 'horizontal':
                widget.pack(side='left', padx=5)

        return widget

    def destroy_widget(self, widget):

        self.widgets = [w for w in self.widgets if w != widget]
        widget.destroy()


class FormMember:
    var: Variable

    def __init__(self, widget_type, title, id, frame: Customframe = None, *args, **kwargs):
        dict = {}
        if 'textvariable' in kwargs.keys():
            dict['textvariable'] = kwargs['textvariable']
            self.var = kwargs['textvariable']
        elif 'variable' in kwargs.keys():
            dict['variable'] = kwargs['variable']
            self.var = kwargs['variable']
        else:
            raise KeyError('Widget needs variable or textvariable')

        self.widget_type = widget_type
        self.title = title
        self.id = id
        self.customframe = frame
        self.widget = None
        self.label = None
        self.clear_button = None
        self.args = args
        self.kwargs = kwargs
        self.disable_button = None
        self.is_disabled = False
        self.bind = []

    def set_paned_window(self, frame: Customframe):
        self.customframe = frame

    def get_widgets(self):

        self.label = Label(self.customframe, text=self.title)
        self.widget = self.widget_type(self.customframe, *self.args, **self.kwargs)
        for bind in self.bind:
            self.widget.bind(bind[0], bind[1])
        self.disable_button = Button(self.customframe, text='Disable', command=self._dis_enable)
        self.customframe.add(self.label)
        self.customframe.add(self.widget)
        self.customframe.add(self.disable_button)

    def add_bind(self, sequence, func):
        self.bind.append((sequence, func))

    def get_value(self):

        return self.var.get()

    def set_value(self, value):
        self.var.set(value)

    def destroy(self):

        if self.label: self.customframe.destroy_widget(self.label)
        if self.widget: self.customframe.destroy_widget(self.widget)
        if self.disable_button: self.customframe.destroy_widget(self.disable_button)

    def set_default_value(self):
        if isinstance(self.var, StringVar):
            self.set_value('')
        if isinstance(self.var, IntVar):
            self.set_value(0)
        if isinstance(self.var, DoubleVar):
            self.set_value(0.0)
        if isinstance(self.var, BooleanVar):
            self.set_value(False)

    def _dis_enable(self):
        if not self.is_disabled:
            self.widget['state'] = 'disabled'
            self.disable_button.configure(text='Disabled')
            self.is_disabled = True
            self.set_default_value()

        else:
            self.widget['state'] = 'normal'
            self.disable_button.configure(text='Enabled')
            self.is_disabled = False

    def get_is_disabled(self):
        return self.is_disabled

    def exist(self):
        if not self.label and not self.widget and not self.disable_button:
            return False
        return self.label.winfo_exists() and self.widget.winfo_exists() and self.disable_button.winfo_exists()


class PlotlyFormCreator:
    def __init__(self, frames: Dict[ConfigTypes, Customframe], frame_for_submit_button: Customframe,
                 submit_command=None):

        self.saved_kwargs = {}
        self.table = None
        self.submit_command = submit_command or (lambda: None)
        self.form_members = {}
        self.submit_button = None
        self.config_titles = {}
        self.frames = frames
        self.frame_for_submit_button = frame_for_submit_button
        self.custom_kwargs_add_button = {}
        self.table_entries = {}
        self.axis_list = StringVar()
        self.axis_list.set('[]')
        self.selected_axis = StringVar()

    def create_form_member(self, widget_type, title, id, config_type: ConfigTypes, *args, **kwargs):

        member = self._destroy_old_member(config_type, id)
        form_member = FormMember(widget_type, title, id, self.frames[config_type], *args, **kwargs)
        if member:
            form_member.set_value(member.get_value())
        self.add_form_member(config_type, form_member)

    def _destroy_old_member(self, config_type, id):
        if config_type in self.form_members:
            for member in self.form_members[config_type]:
                if member.id == id:
                    member.destroy()
                    self.form_members[config_type].remove(member)
                    return member
                    break

    def add_form_member(self, config_type, form_member):
        if config_type not in self.form_members:
            self.form_members[config_type] = []
        self.form_members[config_type].append(form_member)

    def create_form(self):
        for config_type, members in self.form_members.items():
            frame = self.frames[config_type]
            if config_type in self.config_titles:
                frame.destroy_widget(self.config_titles[config_type])
            title_widget = Label(frame, text=config_type.value)
            self.config_titles[config_type] = title_widget
            frame.add(title_widget)

            for member in members:
                if member.exist():
                    continue
                member.get_widgets()

            if config_type in self.custom_kwargs_add_button.keys():
                frame.destroy_widget(self.custom_kwargs_add_button[config_type])

            self.custom_kwargs_add_button[config_type] = Button(frame, text='Add custom kwargs', command=lambda w=frame,
                                                                                                                config=config_type: self.open_custom_kwargs_dialog(
                w, config))
            frame.add(self.custom_kwargs_add_button[config_type])

        if self.submit_button is None:
            self.submit_button = Button(self.frame_for_submit_button, text="Submit", command=self._on_submit)
            self.frame_for_submit_button.add(self.submit_button)

    def get_content(self):
        content = {}
        for config_type, members in self.form_members.items():
            content[config_type] = {}
            for memb in members:
                if (memb.is_disabled) or not memb.get_value():
                    continue
                content[config_type][memb.id] = memb.get_value()

            for param, value,selected_axis in self.saved_kwargs.get(config_type, []):
                if selected_axis != '':
                    if selected_axis not in content[config_type]:
                        content[config_type][selected_axis] = {}
                    content[config_type][selected_axis][param] = value

                else:
                    content[config_type][param] = value
        print(content)
        return content

    def get_widget(self, config_type, id: str):
        if config_type not in self.form_members.keys():
            return None
        for memb in self.form_members[config_type]:
            if memb.id == id:
                return memb
        return None

    def _on_submit(self):
        content = self.get_content()
        self.submit_command(content, self.axis_list)

    def open_custom_kwargs_dialog(self, window, config_type):
        if config_type not in self.table_entries or not self.table_entries[config_type][1].winfo_exists():

            dialog = tkinter.Toplevel(window)
            dialog.title("Add Custom KWArgs")
            dialog.grab_set()

            table_window = PanedWindow(dialog, orient='horizontal')
            table_window.pack(fill='both', expand=True)

            table = tkinter.ttk.Treeview(table_window, columns=['parameter', 'value', 'selected_axis'],
                                         show='headings')
            table.heading('parameter', text='Parameter')
            table.heading('value', text='Value')
            table.heading('selected_axis', text='Selected_Axis')
            table_window.add(table, stretch='always')

            add_button = Button(table_window, text="Add Kwargs",
                                command=lambda: self.ask_params(table, config_type, table_window))
            table_window.add(add_button)

            clear_button = Button(table_window, text="Clear Row", command=lambda: self.clear_row(table, config_type))
            table_window.add(clear_button)

            if config_type in self.saved_kwargs.keys():
                for param, value, type, axis_config in self.saved_kwargs[config_type]:
                    table.insert("", "end", values=(param, value,axis_config))
            table.get_children()

            self.table_entries[config_type] = (dialog, table, add_button, clear_button)


        else:
            dialog, table, add_button, clear_button = self.table_entries[config_type]
            dialog.deiconify()
            dialog.lift()
            dialog.focus_force()

    def ask_params(self, table, config_type, window):
        ask_axis_config = False
        axis_selected = StringVar()
        if config_type == ConfigTypes.LAYOUT:
            ask_axis_config = messagebox.askyesno(parent=table, title="Config Axis", message="Config individual axis?")
            if ask_axis_config:
                self.open_axis_config_dialog(axis_selected)
        if ask_axis_config == True and not axis_selected.get():
            return
        param = tkinter.simpledialog.askstring(parent=table, title="Parameter", prompt="Enter parameter name:")
        if param is None:
            return
        try:
            value = self._askValue(table, window)
        except Exception as e:
            messagebox.showerror("Type Error", f"An unexpected error occurred: {str(e)}", parent=table)
            return

        if axis_selected.get() == 'all_y_axis':
            for y_axis in eval(self.axis_list.get()):
                if y_axis == 'all_y_axis' or y_axis == 'all_x_axis' or 'xaxis' in y_axis:
                    continue
                table.insert("", "end", values=(param, value, y_axis))
                if config_type not in self.saved_kwargs:
                    self.saved_kwargs[config_type] = []
                self.add_kwargs(config_type, param, value, y_axis)
            return

        if axis_selected.get() == 'all_x_axis':
            for x_axis in eval(self.axis_list.get()):
                if x_axis == 'all_y_axis' or x_axis == 'all_x_axis' or 'yaxis' in x_axis:
                    continue
                table.insert("", "end", values=(param, value, x_axis))
                if config_type not in self.saved_kwargs:
                    self.saved_kwargs[config_type] = []
                self.add_kwargs(config_type, param, value, x_axis)
            return

        table.insert("", "end", values=(param, value, axis_selected.get()))
        if config_type not in self.saved_kwargs:
            self.saved_kwargs[config_type] = []
        self.add_kwargs(config_type, param, value, axis_selected.get())

    def _askValue(self, parent, window, notes=None):
        result = StringVar()
        open_value_window = tkinter.Toplevel(window)
        open_value_window.grab_set()
        text = ScrolledText(master=open_value_window)
        text.pack(fill='both', expand=True)

        def submit(result: StringVar):
            result.set(text.get("1.0", tkinter.END))
            open_value_window.destroy()

        submit_button = tkinter.Button(master=open_value_window, text="Submit", command=lambda: submit(result))
        submit_button.pack(fill='x', side=tkinter.BOTTOM)

        open_value_window.wait_window()
        return yaml.safe_load(result.get())

    def clear_row(self, table, config_type):
        selected_item = table.selection()
        if selected_item:
            item_index = table.index(selected_item[0])
            table.delete(selected_item)
            if config_type in self.saved_kwargs and 0 <= item_index < len(self.saved_kwargs[config_type]):
                self.saved_kwargs[config_type].pop(item_index)

    def add_kwargs(self, config_type, param, value, notes):
        if config_type not in self.saved_kwargs:
            self.saved_kwargs[config_type] = []
        self.saved_kwargs[config_type].append((param, value, notes))

    def open_axis_config_dialog(self, axis_selected: StringVar = None):
        dialog = tkinter.Toplevel()
        dialog.title("Config Axis")
        dialog.grab_set()

        select_axis = Combobox(dialog, textvariable=axis_selected, values=eval(self.axis_list.get()))
        select_axis.pack(side='top', pady=10)

        trace_id = self.axis_list.trace_add("write",
                                            lambda name, index, operation: self.update_axis_combobox(select_axis))

        label = Label(dialog, text="Axis Configuration")
        label.pack(side='top', pady=10)

        ok_button = Button(
            dialog,
            text="OK",
            command=lambda: self.close_axis_dialog(dialog, select_axis, axis_selected, trace_id),
        )
        ok_button.pack(side='bottom', pady=10)

        dialog.protocol(
            "WM_DELETE_WINDOW",
            lambda: self.close_axis_dialog(dialog, select_axis, axis_selected, trace_id),
        )
        dialog.wait_window()
        return axis_selected

    def update_axis_combobox(self, select_axis):

        if select_axis and select_axis.winfo_exists():
            select_axis['values'] = eval(self.axis_list.get())

    def close_axis_dialog(self, dialog, select_axis, axis_selected, trace_id):
        axis_selected.set(select_axis.get() if select_axis.winfo_exists() else "")
        self.axis_list.trace_remove("write", trace_id)
        dialog.destroy()
