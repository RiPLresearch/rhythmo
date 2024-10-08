import numpy as np

import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go 
from logger.logger import get_logger
logger = get_logger(__name__)

def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    """
    
    """
    resampled_data = rhythmo_outputs.resampled_data
    #data_standardized = rhythmo_outputs.standardized_data
    #filtered_standardized_data = rhythmo_outputs.filtered_cycle
    filtered_cycle = rhythmo_outputs.filtered_cycle
    # projected_cycle = rhythmo_outputs.projected_cycle
    strongest_peak = rhythmo_outputs.cycle_period


    fig = go.Figure()
    fig.add_trace(
            go.Scatter(x = resampled_data['timestamp'], 
                    y = resampled_data['value'], 
                    mode = 'lines', 
                    name = 'heart rate',
                    line = {'color': 'rgb(115,115,115)'}))

    fig.add_trace(go.Scatter(x = filtered_cycle['timestamp'], 
                            y = filtered_cycle['value'], 
                            mode = 'lines', name=f'{strongest_peak} day cycle', 
                            line = {'color': 'tomato'}))
    
    fig.update_layout(xaxis_title='Time',
                  yaxis_title='Heart Rate',
                  showlegend=True)
    
    fig.show()