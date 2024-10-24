import scipy.signal as signal
import numpy as np
import pandas as pd
from logger.logger import get_logger
logger = get_logger(__name__)

def find_peak_values(projected_cycle, num_peaks, projected_timestamps):
    """
    Finds the peaks of the projected cycle.
    """
    peaks, _ = signal.find_peaks(projected_cycle)
    peaks_selection = peaks[:num_peaks]
    peak_values = projected_timestamps[peaks_selection]
    return peak_values

def find_trough_values(projected_cycle, num_troughs, projected_timestamps):
    """
    Finds the troughs of the projected cycle.
    """
    troughs, _ = signal.find_peaks(-projected_cycle)
    troughs_selection = troughs[:num_troughs]
    trough_values = projected_timestamps[troughs_selection]
    return trough_values

def find_rising_falling_values(projected_cycle, num_rising, num_falling, projected_timestamps):
    """
    Finds the rising and falling values of the projected cycle.
    """
    dy = np.gradient(projected_cycle, projected_timestamps)
    rising_values = dy > 0
    falling_values = dy < 0

    rising_timestamps = projected_timestamps[rising_values]
    falling_timestamps = projected_timestamps[falling_values]
    rising_values = rising_timestamps[:num_rising]
    falling_values = falling_timestamps[:num_falling]

    return rising_values, falling_values

def find_regular_samples(projected_cycle, number_of_future_phases, projected_timestamps):
    """
    Finds regular samples to capture all phases on the projected cycle.
    """
    indices = np.linspace(0, len(projected_cycle) - 1, number_of_future_phases, dtype = int)
    regular_samples = projected_timestamps[indices]
    return regular_samples

def find_rising_falling(peak_values, trough_values):
    for peak in peak_values:
        for trough in trough_values:
            if peak > trough:
                rising = trough_values + (peak_values - trough_values) / 2
                falling = peak_values + (trough_values - peak_values) / 2
            else:
                rising = peak_values + (trough_values - peak_values) / 2
                falling = trough_values + (peak_values - trough_values) / 2

    return rising, falling

def schedule(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    """
    timing_of_future_phases = parameters.timing_of_future_phases
    number_of_future_phases = parameters.number_of_future_phases

    projected_cycle = rhythmo_outputs.future_cycle.value
    projected_timestamps = rhythmo_outputs.future_cycle.timestamps

    if number_of_future_phases < 1:
        error_message = f"Number of future phases must be greater than 1. Please enter a value greater than 1."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)
    else:
        
        if timing_of_future_phases == 'regular_sampling':
            regular_samples = find_regular_samples(projected_cycle, number_of_future_phases, projected_timestamps)
            regular_samples = pd.to_datetime(regular_samples, unit='ms')

            future_phases = pd.DataFrame({"regular_samples": regular_samples})

        elif timing_of_future_phases == 'peak_trough':
            if number_of_future_phases > 8:
                error_message = f"Number of future phases {number_of_future_phases} is not valid. For this option peak_trough, the maximum number of future phases is 8 (i.e., no more than 4x cycle duration)."
                logger.error(error_message, exc_info=True)
                raise ValueError(error_message)
            
            num_peaks = num_troughs = number_of_future_phases // 2
            if number_of_future_phases % 2 != 0:
                num_peaks += 1

            peak_values = find_peak_values(projected_cycle, num_peaks, projected_timestamps)
            trough_values = find_trough_values(projected_cycle, num_troughs, projected_timestamps)

            peak_values, trough_values = (pd.to_datetime(values, unit='ms') for values in (peak_values, trough_values))

            future_phases = pd.DataFrame({"peaks": peak_values, "troughs": trough_values})

        elif timing_of_future_phases == 'peak_trough_rising_falling':
            if number_of_future_phases > 16 or number_of_future_phases < 4:
                error_message = f"Number of future phases {number_of_future_phases} is not valid. For this option peak_trough_rising_falling, the maximum number of future phases is 16 (i.e., no more than 4x cycle duration) and minimum number is 4 (i.e., no less than 1x cycle duration)."
                logger.error(error_message, exc_info=True)
                raise ValueError(error_message)
            num_peaks = num_troughs = num_rising = num_falling = number_of_future_phases // 4

            remainder = number_of_future_phases % 4
            if remainder > 0:
                num_peaks += 1
            if remainder > 1:
                num_falling += 1
            if remainder > 2:
                num_troughs += 1

            peak_values = find_peak_values(projected_cycle, num_peaks, projected_timestamps)
            trough_values = find_trough_values(projected_cycle, num_troughs, projected_timestamps)
            rising_values, falling_values = find_rising_falling_values(projected_cycle, num_rising, num_falling, projected_timestamps)
            rising, falling = find_rising_falling(peak_values, trough_values)
            peak_values, trough_values, rising_date, falling_date = (pd.to_datetime(values, unit='ms') for values in (peak_values, trough_values, rising, falling))
            
            peak_values, trough_values, rising_values, falling_values = (pd.to_datetime(values, unit='ms') for values in (peak_values, trough_values, rising_values, falling_values))

            future_phases = pd.DataFrame({"peaks": peak_values, "troughs": trough_values, "rising": rising_values, "falling": falling_values})

        else:
            error_message = f"Timing of future phases {timing_of_future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message)
    
    rhythmo_outputs.future_phases = future_phases
    return rhythmo_outputs