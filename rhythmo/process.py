import numpy as np
import pandas as pd

# Loading and viewing the raw data


heart_rate = pd.read_csv('') 
    # Using pandas to read the csv file

heart_rate['timestamp'] = pd.to_datetime(heart_rate['seconds_since_hr_recording'], unit = 's') 
    # Converts the timestamp column in the csv into a datetime

hr_smoothed = heart_rate.rolling(window='D', on='timestamp').mean()['value']
    # Takes a moving average, with a window size of 'D' (or one day)

hr_hourly = heart_rate.resample('H', on='timestamp').mean().reset_index()['value']
    # Resamples the data to hourly intervals, calculating the resampled value as the average of the data within each interval.

heart_rate = heart_rate.drop(columns=["Unnamed: 0", "seconds_since_hr_recording"]) 
    # Removes the original timestamp column

heart_rate.head() 
    # Displays the first five rows of the dataframe by default


# Checking to see if there is sufficient amount of HR data, and looking for the best segment of data

def proportion_nans(df):
    """Get the proportion of nans in the dataset
    
        Parameters
        ------------
            df: 
                Data frame
        Returns
        ------------
            proportion_nans: numpy array of float (0 or 1)
                Proportion of NaNs in the dataset
    """
    num_of_nans = pd.isnull(df['value']).sum() 
            # Checks each element in the 'value' column of the dataset for NaN, returning a sum of true values 
    
    proportion_nans = num_of_nans / len(df)
    return proportion_nans

def check_sufficient_hr_data(heart_rate_df):
    '''
    Checks for sufficient HR data:
    At least one month HR data overall, with at least one timestamp in the
    past two months, and at least 70% non nan

    Parameters
    ------------
        heart_rate_df: 
            Data frame
    '''

    if heart_rate_df.empty:
        return False, heart_rate_df
    else:
        num_of_nans = proportion_nans(heart_rate_df) 
            # If the dataframe is not empty, finds the proportion of NaNs

        if num_of_nans <= 0.3: 
            # If proportion of NaNs is less than 30% in the dataframe
            return True, heart_rate_df
        
        # Finding the longest segment of data with less than 30% NaN
        max_duration = pd.Timedelta(0)
        longest_start_ind = 0
        longest_end_ind = 0
        min_window_size = pd.Timedelta(days=90)
        sliding_window_size = pd.Timedelta(days=30)

        starting_inds = []
        k = 1
        while (next_date:=heart_rate_df.iloc[0]['timestamp'] + k*sliding_window_size) < heart_rate_df['timestamp'].max():
            """
            Loop creates an array of indices of approximately 1 per month (e.g., Month 1, Month 2, Month 3), starting 
            from the beginning of the dataframe. Loop increases by increments of k (window size of 30 days) until it 
            hits a date that is greater than or equal to the maximum timestamp in the dataframe.
            """
            
            # Finding the closest/nearest time stamp to 'next-date' and appending its index to the starting_inds list (start of the 30 days)
            closest = nearest(heart_rate_df['timestamp'], next_date)
            starting_inds.append(heart_rate_df[heart_rate_df['timestamp'] == closest].index[0])
            k += 1
        
        for i, start_ind in enumerate(starting_inds):
            """Iterate through the data of each month to find the longest segment with less than 30% NaN
                Parameters
                ------------
                i: 
                    indices of start_ind
                start_ind:
                    original monthly indices for heart_rate_df, found in while loop above
            """

            # Ending indices of approximately 1 per month starting from the starting index (e.g., Month 2, Month 3, Month 4)
            ending_inds = starting_inds[i + 1:]

            for end_ind in ending_inds:
                """ Iterating through all possible ending indices until the end of the recording is reached"""

                if heart_rate_df.iloc[end_ind]['timestamp'] - heart_rate_df.iloc[start_ind]['timestamp'] <= min_window_size:
                    # Checks if the segment of data is longer than 90 days
                    continue

                # Finding the number of NaNs in the segment of interest
                segment = heart_rate_df.iloc[start_ind:end_ind+1]
                num_of_nans = proportion_nans(segment)

                # Checking if the segment has <30% NaNs and is longer than the current longest segment
                if num_of_nans <= 0.3 and (segment['timestamp'].max() - segment['timestamp'].min()) > max_duration:
                    max_duration = segment['timestamp'].max() - segment['timestamp'].min()
                    longest_start_ind = start_ind
                    longest_end_ind = end_ind

        longest_segment = heart_rate_df.iloc[longest_start_ind:longest_end_ind+1]
        if len(longest_segment) == 1:
            # If a segment >3 months with <30% nans is found, return False
            return False, longest_segment.reset_index(drop=True)

        return True, longest_segment.reset_index(drop=True)
    


# Re-sampling and Interpolation

hr_resample = heart_rate.resample('1D', on='timestamp').apply(resting_hr).reset_index() 
""" Re-sampling the heart rate data, getting resting heart-rate per day """
print(hr_resample)

# Checking if there is enough data to work with
hr_check, hr_new = check_sufficient_hr_data(hr_resample)
if hr_check:
    hr_resample = hr_new
else:
    ## reject data message
    print("Not enough data to work with")
    exit()

# Interpolating for any missing data (blanks in the CSV)
hr_interpolate = pd.DataFrame() # Creates an empty DF
hr_interpolate['timestamp'] = hr_resample['timestamp']
hr_interpolate['value'] = hr_resample['value']
hr_interpolate['value'] = (hr_interpolate['value'] - hr_interpolate['value'].mean())/hr_interpolate['value'].std() 
"""Standardization: standardizing the 'value' column. Resulting values will have a mean of 0 and stdev of 1. Useful for normalizing data."""

hr_interpolate['value'][pd.isnull(hr_interpolate['value'])] = hr_interpolate['value'].mean() 
"""For any NaN values, the corresponding entry in 'value' is replaced by the mean of the column."""

n = (hr_interpolate['timestamp'].iloc[-1] - hr_interpolate['timestamp'].iloc[0]).total_seconds()/(60 * 60 * 24)/3 
"""Calculates the total duration in days between the first and last timestamps in hr_interpolate and divides by 3"""

periods = np.arange(2, int(n), 0.5) 
"""Generates values from 2 to up until 'int(n)' calculated above, with a step size of 0.5"""
freqs = (1/periods)

y = hr_interpolate.value.to_numpy() 
"""Accesses 'value' column in hr_interpolate DF, and converts pandas series into NumPy arrays (easier to manipulate)"""



#def process(rhythmo_inputs, rhythmo_outputs, parameters):