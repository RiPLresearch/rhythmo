import numpy as np
import scipy
from scipy.signal import butter, sosfiltfilt, hilbert

from logger.logger import get_logger
logger = get_logger(__name__)

def find_relative_power(peaks, power, glbl_signif):
    """Appends the value of 'relative power' of each peak compared to the global significance threshold"""
    power_relative = [(power - glbl_signif)[i] for i in peaks]
    return power_relative

def find_peak_prominence(peaks, power):
    """Calculates prominence of each peak."""
    peak_prominence = scipy.signal.peak_prominences(power, peaks)[0]
    return peak_prominence

def find_xpeaks(peaks, period):
    """Appends the periods corresponding to the detected peaks."""
    xpeaks = [period[i] for i in peaks]
    return xpeaks

def find_strongest_peak(cycle_selection_method, xpeaks, peak_prominence, power_relative, power):
    """ Finds the strongest peaksmeasure of how much a peak stands out relative to its surrounding data. Used to filter or rank detected peaks based on their prominence."""
    
    if cycle_selection_method == 'prominence':
        strongest_peak = xpeaks[np.argmax(peak_prominence)] # idenitifies the peak w/ highest prominence and stores the period of that peak into strongest_peak
    elif cycle_selection_method == 'relative_power':
        strongest_peak = xpeaks[np.argmax(power_relative)] # idenitifies the peak w/ highest relative power and stores the period of that peak into strongest_peak
    elif cycle_selection_method == 'power':
        strongest_peak = xpeaks[np.argmax(power)] # idenitifies the peak w/ highest power and stores the period of that peak into strongest_peak
    else:
        logger.error(f"Cycle selection method {cycle_selection_method} is not valid. Please either add this functionality or select one of: prominence, relative power, power.", exc_info=True)
        raise ValueError(f"Cycle selection method {cycle_selection_method} is not valid. Please either add this functionality or select one of: prominence, relative power, power.")

    xpeaks = [strongest_peak] # reassigns xpeaks to contain the strongest_peak 
    return xpeaks


def selection(_rhythmo_inputs, rhythmo_outputs, parameters):
    """If the user inputs a cycle period, then the output is the strongest cycle.
    If the user has not provided a cycle period, go through with the cycle_selection_method.
    """
    if not parameters.cycle_period:
        if min_cycle_period < parameters.cycle_period & max_cycle_period > parameters.cycle_period:
            rhythmo_outputs.cycle_period = parameters.cycle_period
        else:
            logger.error(f"Cycle period is not within the minimum {min_cycle_period} or maximum {min_cycle_period} cycle period. Either change the cycle period, or the output will default to the cycle selection method.", exc_info=True)
            raise ValueError(f"Cycle period is not within the minimum {min_cycle_period} or maximum {min_cycle_period} cycle period. Either change the cycle period, or the output will default to the cycle selection method.")
    else:
        power_relative = find_relative_power(parameters.wavelet_data["peaks"], parameters.wavelet_data["power"],parameters.wavelet_data["significance"])
        peak_prominence = find_peak_prominence(parameters.wavelet_data["peaks"], parameters.wavelet_data["power"])
        xpeaks = find_xpeaks(parameters.wavelet_data["peaks"], parameters.wavelet_data["period"])
        strongest_peak = find_strongest_peak(parameters.cycle_selection_method, xpeaks, peak_prominence, power_relative, parameters.wavelet_data["power"])

    rhythmo_outputs.cycle_period = strongest_peak # Stores the period of the peak w/ the highest power
    return rhythmo_outputs