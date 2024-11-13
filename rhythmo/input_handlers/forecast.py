import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from scipy.signal import hilbert
from prophet import Prophet
from rhythmo.data import Cycle, MILLISECONDS_IN_A_DAY
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
    # cumulative_phase = [
    #     phase + 2 * (n + 1) * np.pi if not (phase > 0 and (i < len(cycle_phase) - 1 and cycle_phase[i + 1] <= 0)) else (n := n + 1) * 0 + phase + 2 * (n + 1) * np.pi
    #     for i, phase in enumerate(cycle_phase)
    # ]
    return cumulative_phase

def get_phases_future(cycle_projection_method, time_in_past, time_in_future, cumulative_phase, strongest_peak):
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
        ds = np.array(time_in_past).reshape(-1)
        y = np.array(cumulative_phase).reshape(-1)
        data = pd.DataFrame({'ds': ds, 'y': y})
        projection_model = Prophet(uncertainty_samples=0)
        projection_model.fit(data)

        # Projecting future cycle phases from prophet model:
        future = projection_model.make_future_dataframe(freq='D', periods=int(4*strongest_peak), include_history=False) # Do I need to use data_resampling_rate from track.py?
        projected_future_phases = projection_model.predict(future)
        phases_in_future = projected_future_phases['ds'].astype('int64') // 10**9
        #phases_in_future_1 = projected_future_phases['yhat']
        #phases_in_future = get_phases(phases_in_future_1)
 
    else:
        error_message = f"Cycle projection method {cycle_projection_method} is not valid. Please either add this functionality or select one of: linear, prophet."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    # Converts cumulative phases into circular phases by re-wrapping phases to be from -π to π
    # circular_phase = [(phase - (2 * np.pi) if phase > np.pi else phase)
                    #   for future_phase in phases_in_future
                    #   for phase in [future_phase - (future_phase // (2 * np.pi)) * (2 * np.pi)]]
    circular_phase = [future_phase - (future_phase // (2 * np.pi)) * (2 * np.pi) for future_phase in phases_in_future]
    return circular_phase

def get_projection_times(time_in_past, strongest_peak):
    """Gets the future projection times as an array"""

    end_timestamp = time_in_past[-1]
    timestamp_dif = end_timestamp - time_in_past[-2]
    start_projection = end_timestamp + timestamp_dif

    projection_duration = 4 * strongest_peak
    projection_duration_ms = projection_duration * MILLISECONDS_IN_A_DAY # convert to UNIX timestamp (miliseconds in a day)
    end_projection = start_projection + projection_duration_ms

    future_timestamps = np.arange(start_projection, end_projection, timestamp_dif)

    return future_timestamps

def forecast(_rhythmo_inputs, rhythmo_outputs, parameters):
    """
    Projects the cycle into the future based on the selected cycle projection method (i.e., linear regression or Facebook Prophet).
    If the user inputs a cycle projection method, then the method is used to output a forecast of future phases of the cycle.
    If the user has not provided a cycle projection method, go through with linear regression.
    """

    ## historic phase information
    cycle_values = rhythmo_outputs.historic_cycle.value
    time_in_past = rhythmo_outputs.historic_cycle.timestamps

    ## get historic phase data
    cycle_phase = get_phases(cycle_values) ## CHECK WHY THIS IS NOT GOING FROM 0 TO 2PI OR -pi to pi
    rhythmo_outputs.historic_cycle.phases = cycle_phase
    cumulative_phase = get_phase_arr(cycle_phase)

    ## get future phase data
    time_in_future = get_projection_times(time_in_past=time_in_past, strongest_peak=rhythmo_outputs.cycle_period)
    phase_cycles_future = get_phases_future(parameters.projection_method, time_in_past, time_in_future, cumulative_phase, strongest_peak=rhythmo_outputs.cycle_period)

    avg_amplitude = np.percentile(cycle_values, 70) - np.percentile(cycle_values, 30)
    projected_cycle = (avg_amplitude)*(np.cos(phase_cycles_future)) + cycle_values.mean()

    rhythmo_outputs.future_cycle = Cycle(timestamps = time_in_future, value = projected_cycle, phases = phase_cycles_future)

    return rhythmo_outputs