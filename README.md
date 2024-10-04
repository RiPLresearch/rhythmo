# Rhythmo
Rhythmo analyses physiological rhythms by identifying ultradian, circadian and circadian cycles and predicting future phases of cycles. This allows researchers to better understand the timing of biological processes and optimise study designs, making it ideal for scheduling interventions, measurements, or data collection during key phases of the cycle.

This repository is best suited for Python version 3.11.8

To install all dependencies, run:
```bash
pip install -r requirements.txt
```

Rhythmo can be run using:

```bash
python -m rhythmo run --inputs {path/to/data.csv} --outputs get_schedule
```

### Inputs
Standard inputs are csv files with two columns: timestamp and value
Timestamp refers to the number of milliseconds since epoch (UNIX time)
Value refers to the physiological value (e.g., Heart rate beats per minute)

### Arguments
Add description of what user needs to do w/ inputs & outputs here -- specify all the options (inputs are location of file), tell the user about the outputs they can type in.. brief explanation of what each does. Optional parameters file can be called by using the --parameters argument (see section 'Running with non-default parameters' below for details).

### Parameters
List all parameters and what they do (use format in file Rachel sent). Add more explanation below, and talk about what it actually does

- **data_type**: str = "csv" # default is csv file, but can be "json" or "parquet"
- **data_resampling_rate**: str = '1H'  # default is hourly, but can be '1Min', '5Min', '1D', etc.
- **wavelet_waveform**: str = "morlet" # default is morlet, but can be "gaussian", "mexican_hat", etc.. # TODO: add support for other waveforms
- **min_cycles**: int = 3 # default is 3, but can be any integer value. This determines the minimum number of cycles to observe for the wavelet transform.
- **min_cycle_period**: Number = 2 # in days
- **max_cycle_period**: Optional[Number] = None # in days, default is set to data duration divided by "min_cycles"
- **cycle_step_size**: Number = 0.5 # in days, default is 0.5, but can be any float value. This determines the step size for the cycle periods to be used in the wavelet.
- **cycle_selection_method**: str = 'prominence' # default is 'prominence', but can be 'power' or 'relative power'
- **cycle_period**: Optional[Number] = None # default is None (automatically selects strongest), but can be any float value (in days). This determines the cycle period to filter the signal at and project the cycle at etc.
- **bandpass_cutoff_percentage**: Number = 33 # default is +/- 33%, but can be any float value (as a percentage). This determines the bandpass filter cutoff percentages either side of the cycle period.
- **projection_method**: str = "linear"  # default is linear projection, but can be "prophet" for Facebook Prophet method #TODO: add support for this and ohter projection methods
- **projection_duration**: Optional[int] = None # if None, it will automatically select 4 * period of cycle. Otherwise this can be any integer value (in days).
- **timing_of_future_phases**: str = "regular_sampling" # default is regular_sampling to capture all phases of the cycle, but can be "peak_trough" or "peak_trough_rising_falling"
- **number_of_future_phases**: int = 8 # by default, rhythmo will predict 8 future phase times. Must be at least 1


#### Running with non-default parameters

See parameters.py for list of parameters used in Rythmo.

Non-default parameters can be set by creating a json file (example given in change_parameters.json), containing only changes required comapred to the default.

For example, if the user wants the next 4 peak/trough times (i.e., 2 peaks, 2 troughs), the json would be:

```json
{
    "timing_of_future_phases": "peak_trough",
    "number_of_future_phases": 4
}
```

All other parameters will use default values.

Once the json file is created, use the -p flag to point to the json file location:

```bash
python -m rhythmo run --inputs {path/to/data.csv} --outputs get_schedule --parameters change_parameters.json
```
