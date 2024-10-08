import numpy as np
import scipy
from logger.logger import get_logger
logger = get_logger(__name__)


def find_relative_power(power, significance, peak_inds):
    """
    Calculates the 'relative power' of each peak compared to the global significance threshold.
    """
    power_relative = [(power - significance)[i] for i in peak_inds]
    return power_relative

def find_peak_prominence(power, peak_inds):
    """
    Calculates prominence of each peak.
    """
    #print(f'ERROR: {scipy.signal.peak_prominences(power, peak_inds)}')
    peak_prominence = scipy.signal.peak_prominences(power, peak_inds)[0]
    return peak_prominence

def find_power(power, peak_inds):
    """
    Calculates the power of each peak.
    """
    peak_power = [power[i] for i in peak_inds]
    return peak_power

def find_strongest_peak(cycle_selection_method, wavelet_data):

    """
    Finds the strongest peaks using either the prominence, relative power or power method:

    prominence: measure of how much a peak stands out relative to its surrounding data
    relative power: the power of the peak relative to the global significance threshold
    power: the power of the peak
    """
    peak_inds = np.where(wavelet_data["peaks"].to_numpy())[0] # finds the indicies of the peaks in the wavelet data (previously calculated in decomp())

    if cycle_selection_method == 'prominence':
        #  idenitifies the peak w/ highest prominence and stores the period of that peak into strongest_peak
        peak_prominence = find_peak_prominence(wavelet_data["power"].to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(peak_prominence)]

    elif cycle_selection_method == 'relative_power':
        # idenitifies the peak w/ highest relative power and stores the period of that peak into strongest_peak
        power_relative = find_relative_power(wavelet_data["power"].to_numpy(), wavelet_data["significance"].to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(power_relative)]

    elif cycle_selection_method == 'power':
        power = find_power(wavelet_data["power"].to_numpy(), peak_inds)
        strongest_peak_ind = peak_inds[np.argmax(power)] # idenitifies the peak w/ highest power and stores the period of that peak into strongest_peak
    
    else:
        error_message = f"Cycle selection method {cycle_selection_method} is not valid. Please either add this functionality or select one of: prominence, relative power, power."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    # convert the indice of the strongest peak to the period of the peak
    strongest_peak = wavelet_data["period"].iloc[strongest_peak_ind]
    return strongest_peak


def selection(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Selects the period of the cycle to use in Rhythmo.
    If the user inputs a cycle period, then the output is the strongest cycle.
    If the user has not provided a cycle period, go through with the cycle_selection_method.
    """
    if parameters.cycle_period is not None:
        if parameters.cycle_period >= parameters.min_cycle_period and parameters.cycle_period <= parameters.max_cycle_period:
            rhythmo_outputs.cycle_period = parameters.cycle_period
        else:
            error_message = f"Cycle period is not within the minimum {parameters.min_cycle_period} or maximum {parameters.min_cycle_period} expected cycle period. Either change the cycle period or parameters, or use a cycle selection method."
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message)
    else:
        strongest_peak = find_strongest_peak(parameters.cycle_selection_method, rhythmo_outputs.wavelet_data)
        rhythmo_outputs.cycle_period = strongest_peak

    return rhythmo_outputs
