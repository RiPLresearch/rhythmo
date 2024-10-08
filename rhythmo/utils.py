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

def resting_hr(array_like):
    """
    Calculates the 10th percentile (value below which 10% of the data falls) of 
    the data array Finds the bottom 10% of the data and returns the mean. 

    Parameters
    ------------
    array_like: 
        array of values

    Returns
    ------------
    data_datetime:
    """
    if array_like.empty:
        return np.nan  
    return array_like[array_like <= np.percentile(array_like, 10)].mean()

def nearest(items, pivot):
    """
    Finds and returns the nearest value in a list of items to the pivot point. 

    Parameters
    ------------
    items: 
        list of items
    
    pivot:
        pivot point

    Returns
    ------------
    data_datetime:
        closest value in 'items' to the pivot point
    """
    nearest_value = min(items, key=lambda x: abs(x - pivot))
    return nearest_value