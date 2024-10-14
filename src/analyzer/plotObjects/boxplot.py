
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd



def getBoxplots(
    data: pd.DataFrame, x:str ,y:str, color: str,facet_row: str, facet_col:str,boxmode:str,height:int,width:int):
    
  
    fig = px.box(
    data,
    x=x,
    y=y,
    color=color,
    boxmode=boxmode,
    facet_col=facet_col,
    facet_row=facet_row
)
    fig.update_layout(height=height,width=width)
    fig.for_each_xaxis(lambda xaxis: xaxis.update(showticklabels=True, matches=None, title_font = dict(size =20), type = 'category'))
    fig.for_each_xaxis(lambda xaxis: xaxis.update(tickangle=10))
    return fig


def getTimeLinePlots(data: pd.DataFrame, x_start:str,x_end:str ,y:str, color: str,facet_row: str, facet_col:str,height:int,width:int):
    data[x_start]= pd.to_datetime(data[x_start])

    fig = px.timeline(data_frame=data, 
                      x_start=x_start, 
                      x_end=x_end, 
                      y=y, 
                      color=color,
                      facet_row=facet_row, facet_col=facet_col,  
    )

    fig.update_layout(
        xaxis_title="Time",
        yaxis_title=f"{str.upper(y)} ID",
        showlegend=True,
        height=height,
        width=width,
        yaxis_type='category'
    )

    fig.update_yaxes(autorange="reversed")
    fig.for_each_yaxis(lambda yaxis: yaxis.update(showticklabels=True))

    fig.update_traces(textposition='none', 
                      insidetextanchor='end')




    return fig 