from statistics import stdev
import numpy as np
import pycwt as cwt # continuous wavelet spectral analysis
import scipy
from scipy.signal import butter, sosfiltfilt, hilbert # tools for signal processing (filtering, fourier transforms, wavelets)

def butter_bandpass_filter_params(lowcut: float,
                                  highcut: float,
                                  fs: float,
                                  order: int = 2):
    """
    Gets numerator and denominator of a filter.
    
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
    Gets bandpass filtered values for a list of values.
 
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


def find_filter_sampling_rate(data_resampling_rate):
    if data_resampling_rate == '1D':
        fs = 1
    elif data_resampling_rate == '1H':
        fs = 24
    elif data_resampling_rate == '1Min':
        fs = 24 * 60
    elif data_resampling_rate == '5Min':
        fs = 24 * 12 
    else:
        raise Exception(f"{data_resampling_rate} is not a valid sampling rate, please either add the functionality or use one of: 1D, 1H, 1Min, 5Min")
    return fs

def track(_rhythmo_inputs, rhythmo_outputs, parameters):
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
