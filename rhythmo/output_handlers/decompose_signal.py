import os
from logger.logger import get_logger

logger = get_logger(__name__)


def output_handler(inputs, outputs, _parameters) -> None:
    wavelet_data = outputs.wavelet_data
    wavelet_data.to_csv(os.path.join("results", f"wavelet_output_{inputs.id_number}.csv"), index=False)
