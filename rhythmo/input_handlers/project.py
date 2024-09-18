# Projection
def get_phases(cycle):
    """
    Gets instantaneous phases for significant HR cycle with a given period using Hilbert transform
    Returns phase values of cycle
    """
    hilbert_arr = hilbert(cycle)  # hilbert transform
    phase = np.angle(hilbert_arr)  # get instantaneous phases. Returns the angle (or phase) of each complex number in hilbert_arr
    return phase


def get_phases_future(time_in_past, cycle_phase):
    """
    Forecast future phases for a given cycle using a linear model
    Phases must first be converted to cumulative phase (strictly increasing, rather than cyclical)
    in order to avoid drops from pi to -pi when phase is kept cyclical
    """
    # model cumulative phases such as 0, 2*pi, 4*pi, .... n*pi
    item_arr = [] # empty list
    n = 0 # keeps track of # phase cycles (i.e., how many times the phase has wrapped around).

    # Unwrap phases to be within (pi, inf), i.e. cumulative, rather than (-pi, pi)
    # (eg phase = 0 -> 4*pi, if 2nd cycle)
    for i, _ in enumerate(cycle_phase):
        item_arr.append(cycle_phase[i] + 2 * (n + 1) * np.pi) # For each phase value in cycle_phase, adjust it by adding 2 * (n + 1) * np.pi
                # Adjustment accounts for phase wrapping around by adding an appropriate multiple of 2 * np.pi
                # Variable n tracks how many times the phase has wrapped around (crossed from + to - values)
        if cycle_phase[i] > 0:
            if i < len(cycle_phase) - 1 and cycle_phase[i + 1] > 0: # if current phase value is positive, check whether next phase value is positive
                continue
            n += 1

    # develop a linear model for cumulative/unwrapped phases
    a = np.array(time_in_past).reshape(-1, 1) # Converts time_in_past into a NumPy array
    y = np.array(item_arr).reshape(-1, 1) # Reshapes the array to be a column vector with one column. Ensures correct shape for linear regression below
    reg1 = LinearRegression() # Facebook prophet method? people can choose projection method (linear regression, linear projection, prophet projection).. look at way she projects cycles into future
    reg1.fit(a, y) 
    """ a: feature matrix/independent variable). Reshaped version of time_in_past
        y: target matrix (dependent variable), reshaped version of item_arr.
        fit: Fits the linear regression model 
    """

    # get timestamps to project phases from
    timestamp_dif = time_in_past.iloc[-1] - time_in_past.iloc[-2] # Computes difference btw the last and second-to-last time points. Result is a time delta
    time_in_future = np.arange(time_in_past.iloc[-1], time_in_past.iloc[-1] + timestamp_dif*1000, timestamp_dif)
            # generates an array of future time points starting from the last time point in time_in_past, 
            # extending into the future by timestamp_dif * 1000, with intervals of timestamp_dif


    # project future cycle phases from linear model
    phases_in_future = [reg1.coef_[0][0] * t + reg1.intercept_[0] for t in time_in_future]
            # reg1.coef_: coefficient (slope) of linear regression model
            # reg1.coef_[0][0] extracts the coefficient for the single feature (time). When * t: The predicted phase component due to the time t
            # reg1.intercept_: intercept of linear regression model. w/ [0] it is the constant term added to the predicted phase.


    # re-wrap phases to be from -pi to pi
    round_phase = []
    for future_phase in phases_in_future: # loop through every value in phases_in_future
        phase = future_phase - (future_phase // (2 * np.pi)) * (2 * np.pi) # Computes the integer number of full 2π cycles in fut_phase. Normalizes future_phase to a value within the range of -2pi to 2pi
        round_phase.append(phase - (2 * np.pi) if phase > np.pi else phase)
            # phase - (2 * np.pi): Adjusts the phase by subtracting 2pi if it is above pi, bringing it within range of -pi to pi
            # else phase: If the phase is within the range, append it as-is.

    return time_in_future, round_phase
        # time_in_future: list of future time points corresponding to phases_in_future
        # round_phase: list of adjusted phase value


def get_future_phases(time_in_past,
                                hr_cycle):
    """
    Generates future phases of HR cycle
    """

    phases = get_phases(hr_cycle)  # get instantaneous phases of significant cycles
    time_in_future, phase_cycles_future = get_phases_future(time_in_past, phases)

    return phases, time_in_future, phase_cycles_future



# Projection figure output:
import datetime
### cycle prediction
phases, time_in_future, phase_cycles_future = get_future_phases(smoothed_all_hr['timestamp'].apply(lambda x: x.timestamp() * 1000), smoothed_all_hr['value'])

time_in_future = pd.to_datetime(time_in_future, unit='ms')
avg_amplitude = np.percentile(smoothed_all_hr['value'], 70) - np.percentile(smoothed_all_hr['value'], 30)
cycle_prediction = (avg_amplitude)*(np.cos(phase_cycles_future)) + smoothed_all_hr['value'].mean()


#def project(rhythmo_inputs, rhythmo_outputs, parameters):