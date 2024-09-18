import numpy as np
import scipy
from scipy.signal import butter, sosfiltfilt, hilbert

xpeaks = []; power_relative = [] # Initializes two empty lists
peak_prominence = scipy.signal.peak_prominences(var * glbl_power, ind_peaks)[0] # calculates prominence of each peak found at indices in ind_peaks

for i in ind_peaks:
    xpeaks.append(period[i]) # appends the periods corresponding to the detected peaks
    power_relative.append([var * glbl_power - glbl_signif][0][i]) # appends the value of 'relative power' of each peak compared to global significance threshold to power_relative

def strongest_peak():
    """ Finds the strongest peaksmeasure of how much a peak stands out relative to its surrounding data. Used to filter or rank detected peaks based on their prominence."""
    
    if STRONGEST_PEAK == 'prominence':
        strongest_peak = xpeaks[np.argmax(peak_prominence)] # idenitifies the peak w/ highest prominence and stores the period of that peak into strongest_peak
    elif STRONGEST_PEAK == 'relative_power':
        strongest_peak = xpeaks[np.argmax(power_relative)] # idenitifies the peak w/ highest relative power and stores the period of that peak into strongest_peak

    xpeaks = [strongest_peak] # reassigns xpeaks to contain the strongest_peak 
    return xpeaks


def selection(_rhythmo_inputs, rhythmo_outputs, parameters):
    """If the user inputs a cycle period, then the output is the filtered signal.
    If the user has not provided a cycle period, go through with the cycle_selection_method.
    """
    if parameters.cycle_period = None:
        rhythmo_outputs = # filtered signal
    else

    
    rhythmo_outputs =  ## some dataframe
    return rhythmo_outputs