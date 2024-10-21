import scipy.signal as signal
import numpy as np
import pandas as pd
from rhythmo.data import MILLISECONDS_IN_A_DAY

from logger.logger import get_logger
logger = get_logger(__name__)

def find_peak_values(projected_cycle):
    """
    Finds the peaks of the projected cycle.
    """
    peaks, _ = signal.find_peaks(projected_cycle)
    peak_values = projected_cycle[peaks]
    return peak_values

def find_trough_values(projected_cycle):
    """
    Finds the troughs of the projected cycle.
    """
    troughs, _ = signal.find_peaks(-projected_cycle)
    trough_values = projected_cycle[troughs]
    return trough_values

def find_rising_falling_values(projected_cycle):
    """
    Finds the rising and falling values of the projected cycle.
    """
    dy = np.diff(projected_cycle)
    dy = np.concatenate([[0], dy])
    rising_values = dy > 0
    falling_values = dy < 0
    return rising_values, falling_values

def find_regular_samples(projected_cycle, number_of_future_phases):
    """
    Finds regular samples to capture all phases on the projected cycle.
    """
    indices = np.linspace(0, len(projected_cycle) - 1, number_of_future_phases, dtype = int)
    regular_samples = projected_cycle.iloc[indices]
    return regular_samples

def schedule(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    """
    timing_of_future_phases = parameters.timing_of_future_phases
    number_of_future_phases = parameters.number_of_future_phases
    projected_cycle = rhythmo_outputs.projected_cycle

    if number_of_future_phases < 1:
        error_message = f"Number of future phases must be greater than 1. Please enter a value greater than 1."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)
    else:
        if timing_of_future_phases == 'regular_sampling':
            regular_samples = find_regular_samples(projected_cycle, number_of_future_phases)
            future_phases = pd.DataFrame({"regular_samples": regular_samples})
        elif timing_of_future_phases == 'peak_trough':
            peak_values = find_peak_values(projected_cycle)
            trough_values = find_trough_values(projected_cycle)
            future_phases = pd.DataFrame({"peaks": peak_values, "troughs": trough_values})
        elif timing_of_future_phases == 'peak_trough_rising_falling':
            peak_values = find_peak_values(projected_cycle)
            trough_values = find_trough_values(projected_cycle)
            rising_values, falling_values = find_rising_falling_values(projected_cycle)
            future_phases = pd.DataFrame({"peaks": peak_values, "troughs": trough_values, "rising": rising_values, "falling": falling_values})
        else:
            error_message = f"Timing of future phases {timing_of_future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message)
    
    rhythmo_outputs.future_phases = future_phases
    return rhythmo_outputs