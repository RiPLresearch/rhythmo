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
    butter(order, [low, high], btype='bandpass', output='sos'): array of float
        butter bandpass filter parameters (order, frequency range, type of filter)
    """
    nyq = 0.5 * fs # Nyquist frequency:
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




loc_peak = np.where(period == strongest_peak)[0][0] # finds and stores indices of location of strongest peak in array
power_peak = power[loc_peak]  # extracts the value of power at the location of a peak, specified by the indices above
cycle_repeats = 3 # how many tmes the strongest cycle/period repeats
time_duration = int(strongest_peak*cycle_repeats) # total tiem duration of the cycle

# Initializing the variables:
avg_power = 0 # average power
best_segment = 0 # segment w/ highest avg power
for start_segment in range(len(power_peak) - time_duration):
    """ Goes through the power data, during the specified time duration. """
    end_segment = start_segment + time_duration #setting the end of the current segment we are on
    test_segment = power_peak[start_segment:end_segment] # segments out the segment were are looking at from the power_peak data
    avg_power_segment = np.mean(test_segment) # calculates avg power of the current segment
    if avg_power_segment > avg_power: # if average power of the current segment is higher than current maximum average power, update the maximimum avg power found
          avg_power = avg_power_segment
          best_segment = start_segment # storing starting index of the best segment
        
# Trimming data to display an sample of the subject's strongest HR cycle
sample_end = hr_resample['timestamp'].iloc[best_segment + time_duration]
trimmed_data = hr_resample[hr_resample['timestamp'] <= sample_end] 

# Filtering data to make curve smoother
filter_tolerance = 0.3
fs = 1

# Handling the NaNs
nan_inds = np.where(pd.isnull(trimmed_data['value']))[0]
intertrimmed_data = trimmed_data.copy()
intertrimmed_data['value'][nan_inds] = np.nanmean(trimmed_data['value'])

# For reversing the normalising (later)
original_min = intertrimmed_data['value'].min()
original_max = intertrimmed_data['value'].max()

# Butter bandpass filter
smoothed_hr = butter_bandpass_filter(intertrimmed_data['value'],
                                        1 / ((1 + filter_tolerance) * strongest_peak),
                                        1 / ((1 - filter_tolerance) * strongest_peak),
                                        fs,
                                        order=2)

# Rescale the filtered data to the original range
filtered_min = smoothed_hr.min()
filtered_max = smoothed_hr.max()

# Reversing normalisation
if filtered_min != filtered_max:  # Just preventing division by 0
    smoothed_hr = (smoothed_hr - filtered_min) / (filtered_max - filtered_min) # Making sure it really is normalised before reversing
    smoothed_hr = smoothed_hr * (original_max - original_min) + original_min # Reversing with the orignal max and min instead of filtered max and min

# Butter bandpass filter
smoothed_all = butter_bandpass_filter(hr_interpolate['value'],
                                        1 / ((1 + filter_tolerance) * strongest_peak),
                                        1 / ((1 - filter_tolerance) * strongest_peak),
                                        fs,
                                        order=2)

# Rescale the filtered data to the original range
filtered_min = smoothed_all.min() # Finding the minimum of the smoothed_all data
filtered_max = smoothed_all.max() # Finding the maximum of the smoothed_all data

# Reversing normalisation
if filtered_min != filtered_max:  # Just preventing division by 0
    smoothed_all = (smoothed_all - filtered_min) / (filtered_max - filtered_min) # Making sure it really is normalised before reversing
    smoothed_all = smoothed_all * (original_max - original_min) + original_min # Reversing with the orignal max and min instead of filtered max and min

def 
# Butter bandpass filter
smoothed_all_hr = hr_interpolate.copy()
smoothed_all_hr['value'] = smoothed_all



def track(rhythmo_inputs, rhythmo_outputs, parameters):

    = butter_bandpass_filter_params(rhythmo_inputs.)

    rhythmo_outputs.filtered_cycle = butter_bandpass_filter()
    return rhythmo_outputs