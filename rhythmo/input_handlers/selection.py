import numpy as np
import scipy
from scipy.signal import butter, sosfiltfilt, hilbert

power = np.abs(rhythmo_outputs.transformed_wavelet) ** 2 # wavelet power spectrum. Squared magnitude of abs value of wavelet transform. Displays how power of different freqs changes over time
glbl_power = power.mean(axis=1) # global wavelet power. Averages wavelet power over time, represents the avg power at each freq/scale.
period = 1 / freqs # converting freqs to periods
var = data_array.std()**2 # variance of the resampled data. This is used in significance testing. Variance = square of std.


fft_power = np.abs(fft) ** 2 # Fourier power spectrum. Squared magnitude of Fourier transform. Outputs overall power for each freq, independent of time


xpeaks = []; power_relative = [] # Initializes two empty lists
ind_peaks = scipy.signal.find_peaks(var * glbl_power)[0] # detects peaks in the data, indices stored in ind_peaks 
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


def selection(rhythmo_inputs, rhythmo_outputs, parameters):

    
    rhythmo_outputs =  ## some dataframe
    return rhythmo_outputs