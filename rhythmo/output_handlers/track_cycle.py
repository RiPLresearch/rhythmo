
from logger.logger import get_logger

logger = get_logger(__name__)


def output_handler(inputs, _outputs, _parameters) -> None:
    """Do something with the inputs"""

# Outputs the cycle figure:
"""fig = go.Figure()
fig.add_trace(
        go.Scatter(x=hr_resample['timestamp'], 
                   y=hr_resample['value'], 
                   mode='lines', 
                   name='heart rate',
                   line={'color': 'rgb(115,115,115)'}))

fig.add_trace(go.Scatter(x=smoothed_all_hr['timestamp'], 
                         y=smoothed_all_hr['value'], 
                         mode='lines', name=f'{strongest_peak} day cycle', 
                         line={'color': 'tomato'}))

fig.update_layout(xaxis_title='Time',
                  yaxis_title='Heart Rate',
                  showlegend=True)"""
