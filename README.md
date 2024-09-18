Rythmo analyses physiological rhythms by identifying ultradian, circadian and circadian cycles and predicting future phases of cycles. This allows researchers to better understand the timing of biological processes and optimise study designs, making it ideal for scheduling interventions, measurements, or data collection during key phases of the cycle.

This repository is best suited for Python version 3.11.8

To install all dependencies, run:
```bash
pip install -r requirements.txt
```

Rythmo can be run using:

```bash
python -m rhythmo run --inputs {path/to/data.csv} --outputs predict_future_phases
```

### Inputs
Standard inputs are csv files with two columns: timestamp and value
Timestamp refers to the number of milliseconds since epoch (UNIX time)
Value refers to the physiological value (e.g., Heart rate beats per minute)

### Running with non-default parameters

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
python -m rhythmo run --inputs {path/to/data.csv} --outputs predict_future_phases --parameters change_parameters.json
```