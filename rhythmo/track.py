import pycwt as cwt # continuous wavelet spectral analysis
from scipy.signal import butter, sosfiltfilt, hilbert # tools for signal processing (filtering, fourier transforms, wavelets)

# Bandpass filtering
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
    butter(order, [low, high], btype='bandpass', output='sos'): array of float
        butter bandpass filter parameters (order, frequency range, type of filter)
    """
    nyq = 0.5 * fs # Nyquist freq is equal to half the sampling rate of a discrete signal processing system. Sampling rate (# samples per second)
    low = lowcut / nyq # lower cut off frequency 
    high = highcut / nyq # higher cut off frequency 
    return butter(order, [low, high], btype='bandpass', output='sos') 
 
 
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
    filtered_signal = sosfiltfilt(sos, data) 
            
    return filtered_signal

#def track(rhythmo_inputs, rhythmo_outputs, parameters):