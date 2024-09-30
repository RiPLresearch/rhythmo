from statistics import stdev
import numpy as np
import pycwt as cwt # continuous wavelet spectral analysis
import scipy
from scipy.signal import butter, sosfiltfilt, hilbert # tools for signal processing (filtering, fourier transforms, wavelets)
from logger.logger import get_logger
logger = get_logger(__name__)

def find_filter_sampling_rate(data_resampling_rate):
    """
    Finds the filter sampling rate based on the user's desired sampling rate.
    This takes in sampling rates of: 1 day, 1 hour, 1 minute, and 5 minutes.
    Default sampling rate is hourly.

    Parameters 
    ------------
    data_resampling_rate: string
        data resampling rate

    Returns
    -------
    fs: float
        sampling rate
    """
    if data_resampling_rate == '1D':
        fs = 1
    elif data_resampling_rate == '1H':
        fs = 24
    elif data_resampling_rate == '1Min':
        fs = 24 * 60
    elif data_resampling_rate == '5Min':
        fs = 24 * 12 
    else:
        error_message = f"Data resampling rate {data_resampling_rate} is not valid. Please either add this functionality or select one of: 1D, 1H, 1Min, 5Min."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)
    return fs

def butter_bandpass_filter_params(lowcut: float,
                                  highcut: float,
                                  fs: float,
                                  order: int = 2):
    """
    Finds and returns parameters for the butterworth bandpass filter.
    
    Parameters
    ------------
    lowcut: float
        lowpass frequency
    highcut: float
        highpass frequency
    fs: float
        sampling rate
    order: int (default = 2)
        bandpass filter order

    Returns
    -------
    sos: array of float
        matrix of coefficients for SOS (second-order sections) filter
    """
    nyq = 0.5 * fs # Nyquist frequency:
    low = lowcut / nyq # lower cut off frequency 
    high = highcut / nyq # higher cut off frequency 
    sos = butter(order, [low, high], btype='bandpass', output='sos') 
    return sos
 
 
def butter_bandpass_filter(data: list,
                           lowcut: float,
                           highcut: float,
                           fs: float,
                           order: int = 2):
    """
    Inputs unfiltered standardized data and returns filtered data using a butterworth bandpass filter.
 
    Parameters
    ----------
    data: array of float
        data to be filtered
    lowcut: float
        lowpass frequency
    highcut: float
        highpass frequency
    fs: float
        sampling rate
    order: int (default = 2)
        bandpass filter order
 
    Returns
    -------
    filtered_signal: array of float
        filtered continuous signal
    """

    sos = butter_bandpass_filter_params(lowcut, highcut, fs, order=order)
    filtered_data = sosfiltfilt(sos, data) 
            
    return filtered_data

def track(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Filters the standardized data over the period in which the strongest peak was found.
    The user is able to select the specific cutoff percentages on either side of the cycle period.
    The user is also able to select the rate at which the data is sampled.
    """
    strongest_peak = rhythmo_outputs.cycle_period

    cutoff_percentage = parameters.bandpass_cutoff_percentage

    lowcut = ((1 - cutoff_percentage/100) * strongest_peak)
    highcut = ((1 + cutoff_percentage/100) * strongest_peak) 
    fs = find_filter_sampling_rate(parameters.data_resampling_rate)
    order = 2 # input for the user? could change 

    standardized_data = rhythmo_outputs.standardized_data['value']
    filtered_standardized_data = butter_bandpass_filter(standardized_data, lowcut, highcut, fs, order)

    rhythmo_outputs.filtered_cycle = filtered_standardized_data
    return rhythmo_outputs
