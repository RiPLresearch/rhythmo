import json
import os

import numpy as np
import pandas as pd


def read_json(file_path: str):
    """De-serializes file to Python object."""
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(data, file_path: str):
    """Serializes and writes Python object to file."""
    # ensure dir exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=True)
    return data

def read_csv(file_path: str):
    """Reads a csv file and returns a pandas dataframe."""
    return pd.read_csv(file_path)

def write_csv(data: pd.DataFrame, file_path: str):
    """Writes a pandas dataframe to a csv file."""
    data.to_csv(file_path, index=False)
    return data

def read_parquet(file_path: str):
    """Reads a parquet file and returns a pandas dataframe."""
    return pd.read_parquet(file_path)

def read_input(input_file: str) -> pd.DataFrame:

    """Reads an input file and returns a pandas dataframe."""
    if input_file.endswith('.csv'):
        return read_csv(input_file)

    elif input_file.endswith('.parquet'):
        return read_parquet(input_file)

    elif input_file.endswith('.json'):
        return read_json(input_file)
    else:
        raise ValueError(f"Unsupported file type: {input_file}")

def check_input(input_data_frame: pd.DataFrame) -> bool:

    """Checks that the input contains columns 'timestamp' and 'value'"""
    if all(expected_column in input_data_frame.columns for expected_column in ['timestamp', 'value']):
        return True
    raise ValueError(f"Input data frame does not contain one or more of the expected columns: timestamp, value")

# Get the bottom 10% of the data and return the mean
def resting_hr(array_like):
    # print(type(array_like[0]))
    # print(type(array_like))
    if array_like.empty:
        return np.nan # represents "NaN" or "Not a Number"
    # if not isinstance(array_like[0], np.float64):
    #     return np.nan
        
    return array_like[array_like <= np.percentile(array_like, 10)].mean()
            # np.percentile: calculates the 10th percentile (value below which 10% of data falls)of the array
            # array_like <= np.percentile : any elements greater than 10th percentile value, marked as False
            # overall, this selects the elements that are less than or equal to 10th percentile value, and creates a new array with these values. 
            # The average of the elements in the filtered array are taken of the filtered array

# Gets the nearest value in a list of items to the pivot point. Retuns the closest value.
def nearest(items, pivot):
    # Inputs: list of items and pivot point.
    # Ouputs: closest value in list to pivot point.
    return min(items, key=lambda x: abs(x - pivot)) # takes minimum value. Lambda function calcuates absolute difference between each item x in items and the pivot value
