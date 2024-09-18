import pycwt as cwt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

from logger.logger import get_logger
logger = get_logger(__name__)

SECONDS_IN_A_DAY = 60 * 60 * 24

def create_wavelet(wavelet_waveform):
    """Based on the chosen waveform, creates the relevant wavelet."""
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
    """ Calculates alpha, the autoregressive coefficient."""

    # Convert panda series ('value' column in the data) into NumPy arrays
    data_array = data['value'].to_numpy()
    try:
        alpha, _, _ = cwt.ar1(data_array)
    except:
        alpha = pd.Series(data_array[:-1]).corr(pd.Series(
            data_array[1:]))  # alpha autocorr value for significance test

    return alpha, data_array

def get_cwt_frequencies(data, min_cycles, min_cycle_period, max_cycle_period, cycle_step_size):
    """Calculates the frequencies (in 1/day) over which the CWT is computed."""

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
    """ Continuous wavelet transform (CWT)
    
        Parameters
        ------------
        signal = data_array: 
            input time series data
        dt = sampling_rate: 
            Sampling rate (in days)
        wavelet = WAVELET: 
            wavelet function being used for the transform (Morlet wavelet)
        freqs = frequencies_cwt: 
            Frequencies over which the CWT is computed
            
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
    transformed_wavelet, scales, frequencies_scales, _, _, _ = cwt.cwt(signal = data_array, dt = sampling_rate, wavelet = wavelet, freqs = frequencies_cwt) 

    return transformed_wavelet, scales, frequencies_scales


def get_global_significance(var, sampling_rate, scales, alpha, dof, wavelet, significance_level = 0.95):
    """ Global significance of wavelet power spectrum.
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
    global_significance, _ = cwt.significance(var, sampling_rate, scales, 1, alpha=alpha, significance_level=significance_level, dof=dof, wavelet=wavelet)
    
    return global_significance


def get_sampling_rate(data_resampling_rate):
    """Convert string sampling rate to integer sampling rate (per day)"""
    if data_resampling_rate == '1H':
        return 24
    elif data_resampling_rate == '1D':
        return 1
    elif data_resampling_rate == '1Min':
        return 24 * 60
    elif data_resampling_rate == '5Min':
        return 24 * 60 / 5
    else:
        # TODO: add more options in
        # return error
        logger.error(f"Sampling rate of {data_resampling_rate} unknown. Either add this functionality or select one of: 1H, 1D, 1Min, 5Min", exc_info=True)
        raise ValueError(f"Sampling rate of {data_resampling_rate} unknown. Either add this functionality or select one of: 1H, 1D, 1Min, 5Min")


def decomp(_rhythmo_inputs, rhythmo_outputs, parameters): 

    wavelet = create_wavelet(parameters.wavelet_waveform)

    alpha, data_array = compute_alpha(rhythmo_outputs.standardized_data)

    sampling_rate = get_sampling_rate(parameters.data_resampling_rate) # samples per day

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

    power = np.abs(transformed_wavelet)**2 # wavelet power spectrum
    glbl_power = power.mean(axis=1) # global wavelet power... global power* variance..
    period = 1 / frequencies_scales # goes into dataframe, first column
    power = glbl_power*var # second column
    ind_peaks = find_peaks(var * glbl_power)[0] # detects peaks in the data, indices stored in ind_peaks 
    peaks = [1 if i in ind_peaks else 0 for i in range(len(period))]

    global_significance = get_global_significance(var, sampling_rate, scales, alpha, dof, wavelet)

    rhythmo_outputs.wavelet_data = pd.DataFrame({"period": period, "power": power, "significance": global_significance, "peaks": peaks})

    return rhythmo_outputs