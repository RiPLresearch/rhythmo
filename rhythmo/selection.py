# Peak analysis
xpeaks = []; power_relative = []
ind_peaks = scipy.signal.find_peaks(var * glbl_power)[0]
peak_prominence = scipy.signal.peak_prominences(var * glbl_power, ind_peaks)[0]

for i in ind_peaks:
    xpeaks.append(period[i])
    power_relative.append([var * glbl_power - glbl_signif][0][i])

if STRONGEST_PEAK == 'prominence':
    strongest_peak = xpeaks[np.argmax(peak_prominence)]
elif STRONGEST_PEAK == 'relative_power':
    strongest_peak = xpeaks[np.argmax(power_relative)]

loc_peak = np.where(period == strongest_peak)[0][0]
power_peak = power[loc_peak]
cycle_repeats = 3
time_duration = int(strongest_peak*cycle_repeats)
avg_power = 0
best_segment = 0
for start_segment in range(len(power_peak) - time_duration):
    end_segment = start_segment + time_duration
    test_segment = power_peak[start_segment:end_segment]
    avg_power_segment = np.mean(test_segment)
    if avg_power_segment > avg_power:
          avg_power = avg_power_segment
          best_segment = start_segment
        

xpeaks = [strongest_peak]
print(f"Strongest peak: {strongest_peak}")


# Trimming data to display an sample of the subject's strongest HR cycle
sample_start = hr_resample['timestamp'].iloc[best_segment] 
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
sample_data = trimmed_data.copy()
sample_data['value'] = smoothed_hr
sample_data['value'][nan_inds] = np.NaN # Putting the NaNs back in for accuracy


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

# Butter bandpass filter
smoothed_all_hr = hr_interpolate.copy()
smoothed_all_hr['value'] = smoothed_all
# smoothed_all_hr['value'][nan_inds] = np.NaN # Putting the NaNs back in for accuracy


#def selection(rhythmo_inputs, rhythmo_outputs, parameters):