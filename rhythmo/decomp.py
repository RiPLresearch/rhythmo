
# Mortlet Wavelet Analysis

# Variables
WAVELET = cwt.Morlet(6) # Continuous wavelet transformation, 6 (non-dimensional frequency parameter) controls the frequency of the wavelet
        # used to analyze signals, detect changes in frequency over time.
STRONGEST_PEAK = 'prominence' # measure of how much a peak stands out relative to its surrounding data. Used to filter or rank detected peaks based on their prominence.

# Wavelet analysis
dt = 1 # sampling interval of 1 (units depends on time scale of signal- days, seconds, hrs)
alpha, _, _ = cwt.ar1(y) # lag 1 autocorrelation for significance (alpha = np.corrcoef(y[:-1], y[1:])[0, 1])
            # autoregressive lag-1 coefficient (AR1) of the signal y,
            # models how much the current value of a time series depends on its previous value
            # alpha stores the coefficient, later used for significance testing

wave, scales, freqs, coi, fft, fftfreqs = cwt.cwt(signal = y, dt = dt, wavelet = WAVELET, freqs = freqs) # cwt.cwt -continuous wavelet transform (CWT)
"""         signal = y: input time series data
            dt = dt: Sampling interval (set to 1)
            wavelet = WAVELET: wavelet function being used for the transform (Morlet wavelet)
            freqs = freqs: Frequencies over which the CWT is computed
            
            OUTPUTS:
            wave: wavelet transform of signal y
            scales: wavelet scales corresponding to the wavelet transform
            freqs: frequencies associated w/ scales.
            coi: cone of influence (where edge effects distort the wavelet transform)
            fft: Fourier transform of the signal y
            fftfreqs: Fourier frequencies corresponding to fft
            
            """
power = np.abs(wave) ** 2 # wavelet power spectrum. Squared magnitude of abs value of wavelet transform. Displays how power of different freqs changes over time
fft_power = np.abs(fft) ** 2 # Fourier power spectrum. Squared magnitude of Fourier transform. Outputs overall power for each freq, independent of time
period = 1 / freqs # converting freqs to periods
glbl_power = power.mean(axis=1) # global wavelet power. Averages wavelet power over time, represents the avg power at each freq/scale.
dof = y.size - scales  # Correction for padding at edges, Degrees of freedom (DOF) 
        # calculated for wavelet power spectrum, (y.size = size of data) (scales - # of scales)
var = y.std()**2 # variance of signal y. This is used in significance testing. Variance = square of std.
glbl_signif, tmp = cwt.significance(var, dt, scales, 1, alpha, significance_level=0.95, dof=dof, wavelet=WAVELET) #  global significance of wavelet power spectrum
""" 
Inputs:
    var: Variance of signal
    dt: Sampling interval
    scales: wavelet scales
    1: background spectrum type (1 indicates an AR(1) process)
    alpha: AR1 coefficient, which models background spectrum
    significance_level=0.95: significance level (95% confidence)
    dof=dof: Degrees of freedom for wavelet power spectrum
    wavelet=WAVELET: wavelet function used (Morlet wavelet)
Outputs:
    glbl_signif: significance levels for global wavelet power spectrum
    tmp: theoretical wavelet spectrum used for significance testing (often ignored).
"""

signif, fft_theor = cwt.significance(1.0, dt, scales, 0, alpha, significance_level=0.95, wavelet=WAVELET) # pointwise significance of wavelet power spectrum
""" 
Inputs:
    1.0: Background variance is set to 1
    dt: Sampling interval
    scales: wavelet scales
    0: Indicates that background spectrum is white noise
    alpha: AR1 coefficient, which models background spectrum
    significance_level=0.95: significance level (95% confidence)
    wavelet=WAVELET: wavelet function used (Morlet wavelet)
Outputs:
    signif: significance levels for wavelet power spectrum at each scale
    fft_theor: theoretical Fourier spectrum used for significance testing

"""

#def decomp(rhythmo_inputs, rhythmo_outputs, parameters): 