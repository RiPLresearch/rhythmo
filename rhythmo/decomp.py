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
        WAVELET = cwt.Mortlet(6)
    elif wavelet_waveform == "gaussian":
        WAVELET = cwt.DOG(m=2)
    elif wavelet_waveform == "mexican_hat":
        WAVELET = cwt.MexicanHat()
    # elif wavelet_waveform = "":
    #     WAVELET = cwt.
    else:
        WAVELET = cwt.Mortlet(6)

    return WAVELET

def  compute_alpha(resampled_data):
    """ Calculates alpha, the autoregressive coefficient."""

    # Convert panda series ('value' column in the data) into NumPy arrays
    resampled_data_array = resampled_data.value.to_numpy()
    alpha, _, _ = cwt.ar1(resampled_data_array) 
    return alpha, resampled_data_array

def get_cwt_frequencies(resampled_data, min_cycles, min_cycle_period, max_cycle_period, cycle_step_size):
    """Calculates the frequencies (in 1/day) over which the CWT is computed."""

    # Calculates the total duration in days between the first and last timestamps in the resampled data and divides by the minimum number of cycles
    data_duration = (resampled_data['timestamp'].iloc[-1] - resampled_data['timestamp'].iloc[0]).total_seconds() / SECONDS_IN_A_DAY 
    max_period = int(data_duration / min_cycles)
    
    if max_cycle_period:
        max_period = min(max_cycle_period, max_period)

    # Generates values from 2 to up until 'int(n)' calculated above, with a step size of 0.5
    periods = np.arange(min_cycle_period, max_period, cycle_step_size)

    frequencies_cwt = (1/periods)
    return frequencies_cwt # in days

def cont_wavelet_transform(resampled_data_array, sampling_interval, WAVELET, frequencies_cwt):
    """ Continuous wavelet transform (CWT)
    
        Parameters
        ------------
        signal = resampled_data_array: 
            input time series data
        dt = sampling_interval: 
            Sampling interval (set to 1)
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
    #transformed_wavelet, scales, frequencies_scales, coi, fft, fftfreqs = cwt.cwt(signal = resampled_data_array, dt = sampling_interval, wavelet = WAVELET, freqs = frequencies_cwt) 
    transformed_wavelet, scales, frequencies_scales, _, _, _ = cwt.cwt(signal = resampled_data_array, dt = sampling_interval, wavelet = WAVELET, freqs = frequencies_cwt) 

    return transformed_wavelet, scales, frequencies_scales


def get_global_significance(var, sampling_interval, scales, alpha, DOF, WAVELET):
    """ Global significance of wavelet power spectrum.
        Parameters
        ------------
            var: 
                Variance of signal
            sampling_interval: 
                Sampling interval
            scales: 
                wavelet scales
            1: 
                background spectrum type (1 indicates an AR(1) process)
            alpha: 
                AR1 coefficient, which models background spectrum
            significance_level=0.95: 
                significance level (95% confidence)
            dof=DOF: 
                Degrees of freedom for wavelet power spectrum
            wavelet=WAVELET: 
                wavelet function used (Morlet wavelet)
        Returns
        ------------
            global_significance: 
                significance levels for global wavelet power spectrum
            wavespec_theor: 
                theoretical wavelet spectrum used for significance testing (often ignored).
    """
    global_significance, wavespec_theor = cwt.significance(var, sampling_interval, scales, 1, alpha, significance_level=0.95, dof=DOF, wavelet=WAVELET)
    
    return global_significance, wavespec_theor

def get_signifance_levels(sampling_interval, scales, alpha, WAVELET): # for fourier transform don't use this
    """ Pointwise significance of wavelet power spectrum.

        Parameters
        ------------
            1.0: 
                Background variance is set to 1
            sampling_interval: 
                Sampling interval
            scales: 
                wavelet scales
            0: 
                Indicates that background spectrum is white noise
            alpha: 
                AR1 coefficient, which models background spectrum
            significance_level=0.95: 
                significance level (95% confidence)
            wavelet=WAVELET: 
                wavelet function used (Morlet wavelet)
        Returns
        ------------
            significance_levels: 
                significance levels for wavelet power spectrum at each scale
            fft_theor: 
                theoretical Fourier spectrum used for significance testing
    """
    significance_levels, fft_theor = cwt.significance(1.0, sampling_interval, scales, 0, alpha, significance_level=0.95, wavelet=WAVELET) 
    return significance_levels, fft_theor

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

    waveform = create_wavelet(parameters.wavelet_waveform)

    alpha, resampled_data_array = compute_alpha(rhythmo_outputs.resampled_data)

    sampling_rate = get_sampling_rate(parameters.data_resampling_rate) # samples per day

    frequencies_cwt = get_cwt_frequencies(rhythmo_outputs.resampled_data,
                                          min_cycles = parameters.min_cycles,
                                          min_cycle_period = parameters.min_cycle_period,
                                          max_cycle_period = parameters.max_cycle_period,
                                          cycle_step_size = parameters.cycle_step_size)

    transformed_wavelet, scales, frequencies_scales = cont_wavelet_transform(resampled_data_array, sampling_rate, waveform, frequencies_cwt)

    # Degrees of freedom (DOF) 
    dof = resampled_data_array.size - scales  
    # Variance of resampled data:
    var = resampled_data_array.std()**2 

    glbl_power = power.mean(axis=1) # global wavelet power... global power* variance..
    period = 1 / frequencies_scales # goes into dataframe, first column
    power = glbl_power*var # second column
    ind_peaks = find_peaks(var * glbl_power)[0] # detects peaks in the data, indices stored in ind_peaks 
    peaks = [1 if i in ind_peaks else 0 for i in range(len(period))] # 4th column

    global_significance, wavespec_theor = get_global_significance(var, sampling_rate, scales, alpha, dof, waveform) # 3rd column

    #significance_levels, fft_theor = get_signifance_levels(sampling_interval, scales, alpha, waveform)

    dataframe = pd.DataFrame({"period": period, "power": power, "significance": global_significance, "peaks": peaks})

    rhythmo_outputs.wavelet_data = dataframe ## some dataframe, 1 column is period, power output from wavelet, significance value at each period, add peak too (output to user)

    return rhythmo_outputs