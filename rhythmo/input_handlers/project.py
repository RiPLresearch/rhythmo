import pandas as pd
import numpy as np
import datetime
from statistics import LinearRegression
from scipy.fftpack import hilbert
from prophet import Prophet
from logger.logger import get_logger
logger = get_logger(__name__)

def get_phases(cycle_data):
    """
    Finds the instantaneous phases values for the significant cycle  
    within a given period using the Hilbert transform.

    Parameters
    ------------
    cycle_data: array of float
        significant cycle

    Returns
    -------
    cycle_phase: array of float
        instaneous phase (or angle) of cycle
    """
    hilbert_arr = hilbert(cycle_data)
    cycle_phase = np.angle(hilbert_arr)
    return cycle_phase

def get_phase_arr(cycle_phase):
    """
    Phases are converted from cyclical phases (i.e. (-π, π)) to 
    cumulative phases (strictly increasing, i.e. 0, 2*π, 4*π, .... n*π)
    in order to avoid drops from π to -π when phase is kept cyclical.
    Returns an array containing these cumulative phases.

    Parameters
    ------------
    cycle_phase: array of float
        instaneous phase (or angle) of cycle

    Returns
    -------
    cumulative_phase: array of float
        array of cumulative phases
    """
    n = 0 
    cumulative_phase = [phase + 2 * (n+1) * np.pi
                for i, phase in enumerate(cycle_phase)
                if (phase > 0 and (i == len(cycle_phase) - 1 or cycle_phase[i+1] <= 0)) or (n := n+1)]
    return cumulative_phase

def get_phases_future(cycle_projection_method, time_in_past, cumulative_phase):
    """
    Based on the selected cycle projection method (i.e., linear regression or Facebook Prophet),
    develops a model for the cumulative/unwrapped phases. Then forecasts future phases for a given 
    cycle using the selected cycle projection model.

    Parameters
    ------------
    cycle_projection_method: str
        selected cycle projection method
    time_in_past: array of float
        timestamps of the cycle data
    cumulative_phase: array of float
        array of cumulative phases

    Returns
    -------
    projection_model:
        projection model (linear or prophet)
    time_in_future: array of float
        list of future time points corresponding to phases_in_future
    circular_phase: array of float
        list of adjusted phase value
    """

    # Finds timestamps to project phases from:
    timestamp_dif = time_in_past.iloc[-1] - time_in_past.iloc[-2]
    time_in_future = np.arange(time_in_past.iloc[-1], time_in_past.iloc[-1] + timestamp_dif*1000, timestamp_dif)
    
    if cycle_projection_method == 'linear':
        # Fitting the linear regression model:
        a = np.array(time_in_past).reshape(-1, 1)
        y = np.array(cumulative_phase).reshape(-1, 1)
        projection_model = LinearRegression()
        projection_model.fit(a, y)

        # Projecting future cycle phases from linear model:
        phases_in_future = [projection_model.coef_[0][0] * t + projection_model.intercept_[0] for t in time_in_future]

    elif cycle_projection_method == 'prophet':
        # Fitting the facebook prophet model:
        ds = np.array(time_in_past).reshape(-1, 1)
        y = np.array(cumulative_phase).reshape(-1, 1)
        projection_model = Prophet(uncertainty_samples=0)
        projection_model.fit(ds, y)

        # Projecting future cycle phases from prophet model:
        phases_in_future = 1# insert projection code

    else:
        error_message = f"Cycle projection method {cycle_projection_method} is not valid. Please either add this functionality or select one of: linear, prophet."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    # Converts cumulative phases into circular phases by re-wrapping phases to be from -π to π
    circular_phase = [phase - (2 * np.pi) if phase > np.pi else phase
                      for future_phase in phases_in_future
                      for phase in [future_phase - (future_phase // (2 * np.pi)) * (2 * np.pi)]]
    
    return time_in_future, circular_phase


def project(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Projects the cycle into the future based on the selected cycle projection method (i.e., linear regression or Facebook Prophet).
    If the user inputs a cycle projection method, then the method is used to output a forecast of future phases of the cycle.
    If the user has not provided a cycle projection method, go through with linear regression.
    """
    cycle_projection_method = parameters.projection_method
    standardized_data = rhythmo_outputs.standardized_data
    cycle_data = standardized_data['value']

    time_in_past = standardized_data['timestamp'].apply(lambda x: x.timestamp() * 1000)

    cycle_phase = get_phases(cycle_data)
    cumulative_phase = get_phase_arr(cycle_phase)
    time_in_future, phase_cycles_future = get_phases_future(cycle_projection_method, time_in_past, cumulative_phase)

    time_in_future = pd.to_datetime(time_in_future, unit='ms')
    avg_amplitude = np.percentile(cycle_data, 70) - np.percentile(cycle_data, 30)
    projected_cycle = (avg_amplitude)*(np.cos(phase_cycles_future)) + cycle_data.mean()

    rhythmo_outputs.projected_cycle = projected_cycle
    return rhythmo_outputs