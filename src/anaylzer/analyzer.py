import tkinter
from .plotly_integration.table import CustomTable


def focus(event,master):
    widget = master.focus_get()
    print(widget, "has focus")
class App(tkinter.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        main_container = tkinter.Frame(self)
        main_container.pack(side="top", fill="both", expand=True)


        self.table = CustomTable(parent=main_container,showtoolbar=True,showtooltip=True)
        self.table.show()


if __name__ == '__main__':
    app = App()
    app.mainloop()
