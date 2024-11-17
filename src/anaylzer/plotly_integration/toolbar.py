from pandastable import ToolBar, addButton,ChildToolBar,images

plotly_button = lambda self : addButton(self, 'Plotly', self.parentapp.plotly, None, 'Plotly')


class CustomToolbar(ToolBar):
    def __init__(self, parent=None, parentapp=None):
        super().__init__(parent=parent,parentapp=parentapp)
        self.parentframe = parent
        self.parentapp = parentapp
        img = images.importcsv()
        plotly_button(self)
        addButton(self,"PANDAS_SQL_QUERY",self.parentapp.pandas_sql_query, img, 'PANDAS_SQL_QUERY')
        img = images.importcsv()
        addButton(self, 'Export_CSV', self.parentapp.export_csv, img, 'Export_csv')

class CustomChildToolBar(ChildToolBar):
    def __init__(self, parent=None, parentapp=None):
        super().__init__(parent, parentapp)
        img = images.cross()
        addButton(self, 'Close', self.parentapp.remove, img, 'close')