import os
from logger.logger import get_logger

logger = get_logger(__name__)


def output_handler(rhythmo_inputs, rhythmo_outputs, _parameters) -> None:
    """
    This output handler outputs a plot of the wavelet data and the corresponding csv file.
    """
    wavelet_data = rhythmo_outputs.wavelet_outputs
    wavelet = wavelet_data.wavelet
    wavelet.to_csv(os.path.join("results", f"wavelet_output_{rhythmo_inputs.id_number}.csv"), index=False)
