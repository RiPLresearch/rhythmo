
from logger.logger import get_logger
logger = get_logger(__name__)


def find_reverse_normalization(filtered_data, std_data, mean_data):
    """
    This reverses the normalization of the filtered data.
    """
    data_reverse_normalized = (std_data * filtered_data)/mean_data
    return data_reverse_normalized

std_data = stdev(parameters.resampled_data['value'])
mean_data = np.mean(parameters.resampled_data['value'])
data_reverse_normalized = find_reverse_normalization(filtered_standardized_data, std_data, mean_data)
    # reflecting min/max or variance... standardizing so 0 mean and 1 stdev

def rescale_data(data):
    """
    Rescales the filtered data to the original range. Finds the minimum and maximum of the data. 
    This is for visualization purposes when plotting.
    """
    filtered_min = data.min()
    filtered_max = data.max()
    return filtered_min, filtered_max


def output_handler(_rhythmo_inputs, rhythmo_outputs, parameters) -> None:
    filtered_standardized_data = rhythmo_outputs.filtered_cycle
    
    # Outputs the cycle figure:
    fig = go.Figure()
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
                    showlegend=True)
    return fig
