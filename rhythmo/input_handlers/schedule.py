import scipy.signal as signal
import numpy as np
import pandas as pd
from logger.logger import get_logger
logger = get_logger(__name__)

def find_regular_samples(projected_cycle, number_of_future_phases, projected_timestamps):
    """
    Finds regular samples to capture all phases on the projected cycle.
    """
    indices = np.linspace(0, len(projected_cycle) - 1, number_of_future_phases, dtype = int)
    regular_samples = projected_timestamps[indices]
    return regular_samples

def find_peak_values(projected_cycle, num_peaks, projected_timestamps):
    """
    Finds the peaks of the projected cycle.
    """
    peak_indices, _ = signal.find_peaks(projected_cycle)
    all_peak_values = projected_timestamps[peak_indices]
    peak_values = all_peak_values[:num_peaks]
    return peak_values, all_peak_values

def find_trough_values(projected_cycle, num_troughs, projected_timestamps):
    """
    Finds the troughs of the projected cycle.
    """
    trough_indices, _ = signal.find_peaks(-projected_cycle)
    all_trough_values = projected_timestamps[trough_indices]
    trough_values = all_trough_values[:num_troughs]
    return trough_values, all_trough_values

def find_rising_falling_values(all_peak_values, all_trough_values, num_rising, num_falling):
    """
    Finds the rising and falling values of the projected cycle.
    """

    if all_trough_values[0] < all_peak_values[0]:
        rising_timestamps = np.round((all_trough_values + all_peak_values)/2)
        falling_timestamps = np.round((all_peak_values[:-1] + all_trough_values[1:])/2)
    else:
        falling_timestamps = np.round((all_trough_values + all_peak_values)/2)
        rising_timestamps = np.round((all_trough_values[:-1] + all_peak_values[1:])/2)

    rising_values = rising_timestamps[:num_rising]
    falling_values = falling_timestamps[:num_falling]

    return rising_values, falling_values

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
            regular_samples = pd.to_datetime(regular_samples, unit='ms').date

            future_phases = pd.DataFrame({"regular_sampling": regular_samples})

        elif timing_of_future_phases == 'peak_trough':
            if number_of_future_phases > 8:
                error_message = f"Number of future phases {number_of_future_phases} is not valid. For this option peak_trough, the maximum number of future phases is 8 (i.e., no more than 4x cycle duration)."
                logger.error(error_message, exc_info=True)
                raise ValueError(error_message)
            
            num_peaks = num_troughs = number_of_future_phases // 2
            if number_of_future_phases % 2 != 0:
                num_peaks += 1

            peak_values, _ = find_peak_values(projected_cycle, num_peaks, projected_timestamps)
            trough_values, _ = find_trough_values(projected_cycle, num_troughs, projected_timestamps)

            peak_values, trough_values = (pd.to_datetime(values, unit='ms').date for values in (peak_values, trough_values))

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

            peak_values, all_peak_values = find_peak_values(projected_cycle, num_peaks, projected_timestamps)
            trough_values, all_trough_values = find_trough_values(projected_cycle, num_troughs, projected_timestamps)
            if all_trough_values.shape != all_peak_values.shape:
                arr_length = min(all_trough_values.size, all_peak_values.size)
                rising_values, falling_values = find_rising_falling_values(all_peak_values[:arr_length], all_trough_values[:arr_length], num_rising, num_falling)
            else:
                rising_values, falling_values = find_rising_falling_values(all_peak_values, all_trough_values, num_rising, num_falling)
            peak_values, trough_values, rising_values, falling_values = (pd.to_datetime(values, unit='ms').date for values in (peak_values, trough_values, rising_values, falling_values))
            future_phases = pd.DataFrame({"peaks": peak_values, "troughs": trough_values, "rising": rising_values, "falling": falling_values})

        else:
            error_message = f"Timing of future phases {timing_of_future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
            logger.error(error_message, exc_info=True)
            raise ValueError(error_message)
    
    rhythmo_outputs.future_phases = future_phases
    return rhythmo_outputs