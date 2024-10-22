import pandas as pd
import numpy as np
import pycwt as cwt
import scipy

from logger.logger import get_logger
logger = get_logger(__name__)

def find_peak_prominence(power, peak_inds):
    """
    Calculates prominence of each peak.
    """
    peak_prominence = scipy.signal.peak_prominences(power, peak_inds)[0]
    return peak_prominence

def find_prominence_width(power, peak_inds):
    """
    Calculates the prominence width of each peak.
    """
    peak_prominence_width = scipy.signal.peak_widths(power, peak_inds)[0]
    return peak_prominence_width

def find_relative_power(power, significance, peak_inds):
    """
    Calculates the 'relative power' of each peak compared to the global significance threshold.
    """
    power_relative = [[power - significance][0][i] for i in peak_inds]
    return power_relative

def find_power(power, peak_inds):
    """
    Calculates the power of each peak.
    """
    peak_power = [power[i] for i in peak_inds]
    return peak_power

def find_minimum_error(standardized_data, peak_inds, wavelet, scales, SAMPLES_PER_DAY):
    wave = standardized_data.to_numpy()
    mean_data = standardized_data.mean()
    std_data = standardized_data.std()
    std_signal = (standardized_data - mean_data) / std_data
    dj = 1 / 12
    dt = 1 / SAMPLES_PER_DAY

    minimum_error = [
       np.square(np.subtract(std_signal, np.real(
           cwt.icwt(np.array(wave[peak_option]).reshape(1, -1),
                    np.array([scales[peak_option]]),
                    dt, dj, wavelet) * std_data))).mean()
       for peak_option in peak_inds
    ]        
    return minimum_error

def find_strongest_peak(cycle_selection_method, peaks, period, power, significance, scales, wavelet, SAMPLES_PER_DAY, standardized_data):

    """
    Finds the strongest peaks using either the prominence, relative power or power method:

    prominence: measure of how much a peak stands out relative to its surrounding data
    prominence-width: #TODO
    relative power: the power of the peak relative to the global significance threshold
    power: the power of the peak
    minimum error: #TODO
    """
    peak_inds = np.where(peaks.to_numpy())[0] # finds the indicies of the peaks in the wavelet data (previously calculated in decomp())

    if cycle_selection_method == 'prominence':
        # idenitifies the peak w/ highest prominence and stores the period of that peak into strongest_peak
        peak_prominence = find_peak_prominence(power.to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(peak_prominence)]
    
    elif cycle_selection_method == 'prominence_width':
        # identifies the peak with the highest prominence to width ratios and stores the period of that peak into strongest_peak
        peak_prominence = find_peak_prominence(power.to_numpy(), peak_inds)
        peak_prominence_width = find_prominence_width(power.to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(peak_prominence/peak_prominence_width)]
    
    elif cycle_selection_method == 'relative_power':
        # idenitifies the peak w/ highest relative power and stores the period of that peak into strongest_peak
        power_relative = find_relative_power(power.to_numpy(), significance.to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(power_relative)]

    elif cycle_selection_method == 'power':
        # idenitifies the peak w/ highest power and stores the period of that peak into strongest_peak
        power = find_power(power.to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(power)] 
    
    elif cycle_selection_method == 'minimum_error':
        # TODO
        minimum_error = find_minimum_error(standardized_data['value'], peak_inds, wavelet, scales, SAMPLES_PER_DAY)
        strongest_peak_ind = peak_inds[np.argmin(minimum_error)]

    else:
        error_message = f"Cycle selection method {cycle_selection_method} is not valid. Please either add this functionality or select one of: prominence, prominence-width, relative_power, power, minimum_error."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    # convert the indice of the strongest peak to the period of the peak
    strongest_peak = period.iloc[strongest_peak_ind]
    return strongest_peak


def selection(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Selects the period of the cycle to use in Rhythmo.
    If the user inputs a cycle period, then the output is the strongest cycle.
    If the user has not provided a cycle period, go through with the cycle_selection_method.
    """
    wavelet_outputs = rhythmo_outputs.wavelet_outputs
    peaks = pd.Series(wavelet_outputs.peaks)
    power = pd.Series(wavelet_outputs.power)
    significance = pd.Series(wavelet_outputs.significance)
    period = pd.Series(wavelet_outputs.period)
    wavelet = wavelet_outputs.wavelet
    scales = wavelet_outputs.scales
    SAMPLES_PER_DAY = wavelet_outputs.SAMPLES_PER_DAY
    
    if parameters.cycle_period is not None:
        if parameters.cycle_period >= parameters.min_cycle_period and parameters.cycle_period <= parameters.max_cycle_period:
            rhythmo_outputs.cycle_period = parameters.cycle_period
        else:
            error_message = f"Cycle period is not within the minimum {parameters.min_cycle_period} or maximum {parameters.min_cycle_period} expected cycle period. Either change the cycle period or parameters, or use a cycle selection method."
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message)
    else:
        strongest_peak = find_strongest_peak(parameters.cycle_selection_method, peaks, period, power, significance, scales, wavelet, SAMPLES_PER_DAY, rhythmo_outputs.standardized_data)
        rhythmo_outputs.cycle_period = strongest_peak

    return rhythmo_outputs
