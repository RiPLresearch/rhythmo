import pycwt as cwt
import pandas as pd
import numpy as np
import scipy
from rhythmo.data import WaveletOutputs, SECONDS_IN_A_DAY

from logger.logger import get_logger
logger = get_logger(__name__)

def create_wavelet(wavelet_waveform):
    """
    Based on the chosen waveform, creates the relevant wavelet.

    Parameters
    ------------
    wavelet_waveform: str
        waveform type

    Returns
    ------------
    wavelet: 
        waveform wavelet
    """
    if wavelet_waveform == "mortlet":
        wavelet = cwt.Morlet(6)
    elif wavelet_waveform == "gaussian":
        wavelet = cwt.DOG(m=2)
    elif wavelet_waveform == "mexican_hat":
        wavelet = cwt.MexicanHat()
    # elif wavelet_waveform = "":
    #     wavelet = cwt.
    else:
        wavelet = cwt.Morlet(6)

    return wavelet

def  compute_alpha(data):
    """
    Calculates alpha, the autoregressive coefficient.

    Parameters
    ------------
    data:
        panda series of the data

    Returns
    ------------
    alpa: 
        alpha autocorr value for significance test
    data_array: arr
        NumPy array of the data
    """
    data_array = data['value'].to_numpy()

    try:
        alpha, _, _ = cwt.ar1(data_array)
    except:
        alpha = pd.Series(data_array[:-1]).corr(pd.Series(
            data_array[1:]))

    return alpha, data_array

def get_sampling_rate(data_resampling_rate):
    """
    Convert string sampling rate to integer sampling rate (per day).

    Parameters
    ------------
    data_resampling_rate: str
        data resampling rate

    Returns
    ------------
    sampling_rate: 
        integer sampling rate (samples per day)
    """
    if data_resampling_rate == '1H':
        sampling_rate = 24
    elif data_resampling_rate == '1D':
        sampling_rate = 1
    elif data_resampling_rate == '1Min':
        sampling_rate = 24 * 60
    elif data_resampling_rate == '5Min':
        sampling_rate = 24 * 60 / 5
    else:
        # TODO: add more options in
        # return error
        logger.error(f"Sampling rate of {data_resampling_rate} unknown. Either add this functionality or select one of: 1H, 1D, 1Min, 5Min", exc_info=True)
        raise ValueError(f"Sampling rate of {data_resampling_rate} unknown. Either add this functionality or select one of: 1H, 1D, 1Min, 5Min")
    
    return sampling_rate

def get_cwt_frequencies(data, min_cycles, min_cycle_period, max_cycle_period, cycle_step_size):
    """
    Calculates the frequencies (in 1/day) over which the CWT is computed.

    Parameters
    ------------
    data:
        dataframe
    min_cycles:
        minimum number of cycles to observe
    min_cycle_period:
        minimum cycle period (in days)
    max_cycle_period:
        maximum cycle period (in days)
    cycle_step_size:
        step size for the cycle periods

    Returns
    ------------
    frequencies_cwt: 
        frequencies over which the CWT is computed
    """

    # Calculates the total duration in days between the first and last timestamps in the resampled data and divides by the minimum number of cycles
    data_duration = (data['timestamp'].iloc[-1] - data['timestamp'].iloc[0]).total_seconds() / SECONDS_IN_A_DAY 
    max_period = int(data_duration / min_cycles)
    
    if max_cycle_period:
        max_period = min(max_cycle_period, max_period)

    # Generates values from 2 to up until 'int(n)' calculated above, with a step size of 0.5
    periods = np.arange(min_cycle_period, max_period, cycle_step_size)

    frequencies_cwt = (1/periods)
    return frequencies_cwt # in days

def cont_wavelet_transform(data_array, sampling_rate, wavelet, frequencies_cwt):
    """ 
    Continuous wavelet transform (CWT)

    Parameters
    ------------
    signal = data_array: 
        input time series data
    dt = sampling_rate: 
        sampling rate (in days)
    wavelet = WAVELET: 
        wavelet function being used for the transform (Morlet wavelet)
    freqs = frequencies_cwt: 
        frequencies over which the CWT is computed
        
    Returns
    ------------
    wave: 
        wavelet transform of the resampled data
    scales: 
        wavelet scales corresponding to the wavelet transform
    frequencies_scales: 
        frequencies associated w/ scales.
    coi: 
        cone of influence (where edge effects distort the wavelet transform)
    fft: 
        Fourier transform of the signal resampled data
    fftfreqs: 
        Fourier frequencies corresponding to fft
    """
    transformed_wavelet, scales, frequencies_scales, _, _, _ = cwt.cwt(signal = data_array, dt = 1 / sampling_rate, wavelet = wavelet, freqs = frequencies_cwt) 

    return transformed_wavelet, scales, frequencies_scales


def get_global_significance(var, sampling_rate, scales, alpha, dof, wavelet, significance_level = 0.95):
    """ 
    Global significance of wavelet power spectrum.

    Parameters
    ------------
    var: 
        Variance of signal
    sampling_rate: 
        Sampling rate (in days)
    scales: 
        wavelet scales
    alpha: 
        AR1 coefficient, which models background spectrum
    dof: 
        Degrees of freedom for wavelet power spectrum
    wavelet: 
        wavelet function used (Morlet wavelet)
    significance_level (default=0.95):
        significance level (95% confidence)

    Returns
    ------------
    global_significance: 
        significance levels for global wavelet power spectrum
    wavespec_theor: 
        theoretical wavelet spectrum used for significance testing (often ignored).
    """
    global_significance, _ = cwt.significance(var, 1 / sampling_rate, scales, 1, alpha = alpha, significance_level = significance_level, dof = dof, wavelet = wavelet)
    
    return global_significance

def decomp(_rhythmo_inputs, rhythmo_outputs, parameters): 
    """
    Utilizes the users chosen wavelet waveform, desired sampling rate, and cycling period.
    Returns the relevant wavelet data (i.e., period, power, significance, and peaks) from the data.
    """

    wavelet = create_wavelet(parameters.wavelet_waveform)

    alpha, data_array = compute_alpha(rhythmo_outputs.standardized_data)

    sampling_rate = get_sampling_rate(parameters.data_resampling_rate)

    frequencies_cwt = get_cwt_frequencies(rhythmo_outputs.standardized_data,
                                          min_cycles = parameters.min_cycles,
                                          min_cycle_period = parameters.min_cycle_period,
                                          max_cycle_period = parameters.max_cycle_period,
                                          cycle_step_size = parameters.cycle_step_size)

    transformed_wavelet, scales, frequencies_scales = cont_wavelet_transform(data_array, sampling_rate, wavelet, frequencies_cwt)

    # Degrees of freedom (DOF) 
    dof = data_array.size - scales  
    # Variance of resampled data:
    var = data_array.std()**2 

    power = np.abs(transformed_wavelet) ** 2 # wavelet power spectrum
    glbl_power = power.mean(axis=1) # global wavelet power
    period = 1 / frequencies_scales # goes into dataframe, first column
    power = glbl_power * var # second column
    ind_peaks = scipy.signal.find_peaks(var * glbl_power)[0] # detects peaks in the data, indices stored in ind_peaks 
    peaks = [1 if i in ind_peaks else 0 for i in range(len(period))]

    global_significance = get_global_significance(var, sampling_rate, scales, alpha, dof, wavelet)

    wavelet_outputs = WaveletOutputs(period = period, power = power, significance = global_significance, peaks = peaks, wavelet = wavelet, scales = scales, SAMPLES_PER_DAY = sampling_rate)
    rhythmo_outputs.wavelet_outputs = wavelet_outputs

    return rhythmo_outputs