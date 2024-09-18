from dataclasses import asdict, dataclass, field
from typing import Optional, Sequence

import pandas as pd
from logger.logger import get_logger

logger = get_logger(__name__)

@dataclass
class Parameters:
    """
    Parameters for rhythmo.
    Default values must be provided.
    """
    data_type: str = "csv" # default is csv file, but can be "json" or "parquet"
    data_resampling_rate: str = '1H'  # default is hourly, but can be '1Min', '5Min', '1D', etc.
    wavelet_waveform: str = "morlet" # default is morlet, but can be "gaussian", "mexican_hat", etc.. # TODO: add support for other waveforms
    min_cycles: int = 3 # default is 3, but can be any integer value. This determines the minimum number of cycles to observe for the wavelet transform.
    min_cycle_period: int = 2 # in days
    max_cycle_period: Optional[int] = None # in days, default is set to data duration divided by "min_cycles"
    cycle_step_size = 0.5 # in days, default is 0.5, but can be any float value. This determines the step size for the cycle periods to be used in the wavelet.
    cycle_selection_method: str = 'prominence' # default is 'prominence', but can be 'power' or 'relative power'
    cycle_period: Optional[float] = None # default is None (automatically selects strongest), but can be any float value (in days). This determines the cycle period to filter the signal at and project the cycle at etc.
    bandpass_cutoff_percentage: float = 33 # default is +/- 33%, but can be any float value (as a percentage). This determines the bandpass filter cutoff percentages either side of the cycle period.
    projection_method: str = "linear"  # default is linear projection, but can be "prophet" for Facebook Prophet method #TODO: add support for this and ohter projection methods
    projection_duration: Optional[int] = None # if None, it will automatically select 4 * period of cycle. Otherwise this can be any integer value (in days).
    timing_of_future_phases: str = "regular_sampling" # default is regular_sampling to capture all phases of the cycle, but can be "peak_trough" or "peak_trough_rising_falling"
    number_of_future_phases: int = 8 # by default, rhythmo will predict 8 future phase times. Must be at least 1

    def sanity_check(self) -> bool:
        '''
        Raises a warning and returns False if parameters are outside expected bounds.
        '''
        raise_warning = False
        params = []
        if self.cycle_period and self.cycle_period <= 0:
            raise_warning = True
            params.append('cycle_period')
        if self.bandpass_cutoff_percentage <= 0:
            raise_warning = True
            params.append('bandpass_cutoff_percentage')
        if self.projection_duration and self.projection_duration <= 0:
            raise_warning = True
            params.append('projection_duration')
        if self.number_of_future_phases <= 0:
            raise_warning = True
            params.append('number_of_future_phases')

        if raise_warning:
            logger.warning(
                f'Warning: {", ".join(params)} hyperparameter(s) outside the expected bounds.')
            return False
        return True

    def to_dict(self):
        """Returns object of dataclass instance."""
        return asdict(self)

# pylint: disable=too-many-instance-attributes
# It doesn't make sense to split / merge any of these variables
@dataclass
class RhythmoOutput:
    """
    Output data from Rhythmo
    """
    resampled_data: Optional[pd.DataFrame] = None # dataframe with columns: timestamp and value
    best_segment: Optional[pd.DataFrame] = None # dataframe with columns: timestamp and value
    wavelet_data: Optional[pd.DataFrame] = None # dataframe with columns: period, power, significance, peak (1 or 0)
    cycle_period: Optional[float] = None # float value (in days)
    filtered_cycle: Optional[pd.DataFrame] = None # dataframe with columns: timestamp and value

    projected_cycle: Optional[pd.DataFrame] = None # dataframe with columns: timestamp and value
    future_phases: Optional[pd.DataFrame] = None # dataframe with columns: timestamp and phase

    # str, comments about the cycle
    notes: str = ''

    @staticmethod
    def build_empty():
        return RhythmoOutput()

    def to_dict(self):
        """Returns object of dataclass instance."""
        return asdict(self)
