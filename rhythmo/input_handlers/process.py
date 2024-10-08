import numpy as np
import pandas as pd
import copy
from rhythmo.utils import nearest, find_percentile

from logger.logger import get_logger
logger = get_logger(__name__)

def timestamps_to_dates(rhythmo_inputs):
    """
    Converts a dataframe of UNIX timestamps (milliseconds since epoch) to datetime dates.

    Parameters
    ------------
    rhythmo_inputs: 
        data frame

    Returns
    ------------
    data_datetime:
        data frame with datetime dates
    """
    data_datetime = copy.copy(rhythmo_inputs)
    data_datetime['timestamp'] = pd.to_datetime(data_datetime['timestamp'], unit = 'ms')

    return data_datetime

def resample_data(data, data_resampling_rate):
    """ 
    Resamples the data to intervals as specified by the user 
    (i.e., default is hourly, but can be '1Min', '5Min', '1D'), calculating 
    the resampled value as the average of the data within each interval.

    Parameters
    ------------
    data: 
        data frame

    data_resampling_rate:
        data resampling rate
    
    Returns
    ------------
    resample_data:
        resampled data 
    """
    #resampled_data = data.resample(data_resampling_rate, on='timestamp').mean().reset_index()
    resampled_data = data.resample(data_resampling_rate, on='timestamp').apply(find_percentile).reset_index()
    return resampled_data

def get_proportion_nans(df):
    """
    Finds the proportion of nans in the dataset.
    
    Parameters
    ------------
    df: 
        data frame
    
    Returns
    ------------
    proportion_nans: numpy array of float (0 or 1)
        Proportion of NaNs in the dataset
    """
    num_of_nans = pd.isnull(df['value']).sum() # Checks each element in the 'value' column of the dataset for NaN, returning a sum of true values 
    proportion_nans = num_of_nans / len(df)
    return proportion_nans

def check_sufficient_data(df):
    '''
    Checks for sufficient data:
    At least one month data overall, with at least one timestamp in the
    past two months, and at least 70% non-NaN

    Parameters
    ------------
    df: 
        Data frame

     Returns
    ------------
   
    '''

    if df.empty:
        return False, df
    else:
        # If the dataframe is not empty, finds the proportion of NaNs
        num_of_nans = get_proportion_nans(df) 
        
        # If proportion of NaNs is less than 30% in the dataframe
        if num_of_nans <= 0.3: 
            return True, df
        
        # Finding the longest segment of data with less than 30% NaN
        max_duration = pd.Timedelta(0)
        longest_start_ind = 0
        longest_end_ind = 0
        min_window_size = pd.Timedelta(days=90)
        sliding_window_size = pd.Timedelta(days=30)

        starting_inds = []
        k = 1
        while (next_date:=df.iloc[0]['timestamp'] + k*sliding_window_size) < df['timestamp'].max():
            """
            Loop creates an array of indices of approximately 1 per month (e.g., Month 1, Month 2, Month 3), starting 
            from the beginning of the dataframe. Loop increases by increments of k (window size of 30 days) until it 
            hits a date that is greater than or equal to the maximum timestamp in the dataframe.
            """
            
            # Finding the closest/nearest time stamp to 'next-date' and appending its index to the starting_inds list (start of the 30 days)
            closest = nearest(df['timestamp'], next_date)
            starting_inds.append(df[df['timestamp'] == closest].index[0])
            k += 1
        
        for i, start_ind in enumerate(starting_inds):
            """
            Iterate through the data of each month to find the longest segment with less than 30% NaN
                Parameters
                ------------
                i: 
                    indices of start_ind
                start_ind:
                    original monthly indices for df, found in while loop above
            """

            # Ending indices of approximately 1 per month starting from the starting index (e.g., Month 2, Month 3, Month 4)
            ending_inds = starting_inds[i + 1:]

            for end_ind in ending_inds:
                """
                Iterating through all possible ending indices until the end of the recording is reached.
                """

                # Checks if the segment of data is longer than 90 days
                if df.iloc[end_ind]['timestamp'] - df.iloc[start_ind]['timestamp'] <= min_window_size:
                    continue

                # Finding the number of NaNs in the segment of interest
                segment = df.iloc[start_ind:end_ind+1]
                num_of_nans = get_proportion_nans(segment)

                # Checking if the segment has <30% NaNs and is longer than the current longest segment
                if num_of_nans <= 0.3 and (segment['timestamp'].max() - segment['timestamp'].min()) > max_duration:
                    max_duration = segment['timestamp'].max() - segment['timestamp'].min()
                    longest_start_ind = start_ind
                    longest_end_ind = end_ind

        # If a segment >3 months with <30% nans is found, return False
        longest_segment = df.iloc[longest_start_ind:longest_end_ind+1]
        if len(longest_segment) == 1:
            return False, longest_segment.reset_index(drop=True)
        return True, longest_segment.reset_index(drop=True)
    
    return data_check, best_segment


def data_standardize(df):
    """
    Standardizing the 'value' column of the dataframe. Resulting values 
    will have a mean of 0 and stdev of 1. Useful for normalizing data.

    Parameters
    ------------
    df: 
        data frame

    Returns
    ------------
    df:
        data frame
    """
    
    df['value'] = (df['value'] - df['value'].mean())/df['value'].std() 
    return df

def interpolate_data(df):
    """
    For any NaN values, the corresponding entry in 'value' is replaced by 
    the mean of the column.
    
    Parameters
    ------------
    df: 
        data frame

    Returns
    ------------
    df:
        data frame
    """ 

    df.loc[pd.isnull(df['value']), 'value'] = df['value'].mean() 
    return df


def process(rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Takes the raw data input from the user and processes the data 
    (i.e., converting dates to datetime format, interpolating missing data). 
    Returns dataframes of both the resampled data and the standardized data.
    """
    # convert timestamps to dates
    data_datetime = timestamps_to_dates(rhythmo_inputs.data)

    # Resampling the data
    data_resampling_rate = parameters.data_resampling_rate
    resampled_data = resample_data(data_datetime, data_resampling_rate)

    data_check, best_segment = check_sufficient_data(resampled_data)
    if data_check:
        rhythmo_outputs.best_segment = best_segment ## TODO: add this so wavelet uses best_segment
    else:
        logger.error("Insufficient data for Rhythmo.",
                     exc_info=True)
        return
    
    # Standardize and interpolate the data
    data_interpolated = interpolate_data(resampled_data)
    data_interpolated_copy = data_interpolated.copy()
    data_standardized = data_standardize(data_interpolated_copy)
    
    rhythmo_outputs.resampled_data = data_interpolated
    rhythmo_outputs.standardized_data = data_standardized
    return rhythmo_outputs