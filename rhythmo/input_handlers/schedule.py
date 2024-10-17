import scipy.signal as signal
import pandas as pd
from logger.logger import get_logger
logger = get_logger(__name__)

def find_min_projection_period(timing_of_future_phases, projected_cycle):
    peaks, _ = signal.find_peaks(projected_cycle)
    troughs, _ = signal.find_peaks(-projected_cycle)
    peak_values = projected_cycle[peaks]
    trough_values = projected_cycle[troughs]
    rising = 1
    falling = 1
    regular_samples = 1

    return peak_values, trough_values, rising, falling, regular_samples

def schedule(_rhythmo_inputs, rhythmo_outputs, parameters):

    timing_of_future_phases = parameters.timing_of_future_phases
    number_of_future_phases = parameters.number_of_future_phases
    projection_duration = parameters.projection_duration
    projected_cycle = rhythmo_outputs.projected_cycle
    
    peaks, troughs, rising, falling, samples = find_min_projection_period(timing_of_future_phases, projected_cycle)

    future_phases = pd.DataFrame({"peaks": peaks, "troughs": troughs, "rising": rising, "falling": falling, "regular_samples": samples})

    rhythmo_outputs.future_phases = future_phases
    return rhythmo_outputs