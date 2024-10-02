import os
import time
from typing import List, Optional
from importlib import import_module
import pandas as pd

from logger.logger import get_logger

from rhythmo.data import Parameters, RhythmoOutput, RhythmoInput
from rhythmo.utils import check_input, read_input, read_json
from rhythmo.input_handlers.process import process
from rhythmo.input_handlers.decomp import decomp
from rhythmo.input_handlers.selection import selection
from rhythmo.input_handlers.track import track
from rhythmo.input_handlers.forecast import forecast
# from rhythmo.input_handlers.schedule import schedule

logger = get_logger(__name__)

STEPS = {"decompose_signal": 1, "track_cycle": 2, "forecast_cycle": 3, "get_schedule": 4}

class Runtime:

    def __init__(self, inputs: List[str], outputs: List[str], parameters: Optional[str]) -> None:
        """
        Creates a new runtime by reading in arguments from the namespace.
        Validates the arguments.

        Parameters
        ----------
        args: args parsed by Namespace
        """
        logger.debug(
            f"Inputs: data inputs(first 5) {inputs[:5]} outputs: {outputs} "
            f"Parameters files: {parameters}")  # log_revert

        self.inputs = inputs
        self.outputs = list(filter(None, (Runtime.get_handler(handler_name) for handler_name in outputs)))
        self.parameters = Runtime.get_parameters(parameters)
        self.step = max([STEPS[output] for output in outputs])

        # If input is a directory not a filename, get all possible data files in the directory
        if len(self.inputs) == 1:
            if os.path.isdir(self.inputs[0]): 
                self.inputs = [os.path.join(self.inputs[0], file) for file in os.listdir(
                    self.inputs[0]) if file.endswith(self.parameters.data_type)]

        logger.debug("Initialised run")  # logger_revert

    @staticmethod
    def get_handler(handler_name: str):
        """
        Attempts to import an output handler by name (outputs are in the
        outputs/ folder)

        Parameters
        ----------
        handler_name: str, the handler folder to be imported

        Returns
        -------
        An output handler function if it matches the handler_name, otherwise None
        """
        try:
            handler = import_module(f'.output_handlers.{handler_name}',
                                              'rhythmo')
            if hasattr(handler, 'output_handler'):
                return handler.output_handler

            logger.error(
                f'{handler_name} does not contain an "output_handler" '
                + 'function, this output will not be generated', exc_info=True)
            return None

        except ImportError:
            logger.error(f'{handler_name} does not exist, ' + 'this output will not be generated',
                         exc_info=True)
            return None

    @staticmethod
    def get_parameters(parameters_file: Optional[str]):
        """
        Updates the parameters based upon the specified json file. Returns default if no file given.

        Parameters
        ----------
        parameters_file: str, optional,
            json file where changes are stored.

        Returns
        -------
        Parameters class
        """

        default = Parameters.build_empty()

        if parameters_file is None:
            return default

        # Load specified json file
        try:
            new_params = read_json(parameters_file)
        except FileNotFoundError as e:
            logger.warning(f"Could not find {parameters_file}")
            raise e

        # update parameters
        updated = default
        for key in new_params:
            updated.__dict__[key] = new_params[key]

        return updated


    def run(self) -> None:
        """
        Runs Rythmo.
        """

        if not self.inputs:
            logger.error('Aborting rhythmo - no data inputs specified', exc_info=True)
            return

        # Print parameters that are being used
        logger.debug(f"Parameters: {self.parameters}")

        overall_start = time.perf_counter()

        for input_file in self.inputs:
            started = time.perf_counter()
            logger.info(f"[{input_file}] START rhythmo (S000)")

            # Open input data
            input_data = read_input(input_file)
            logger.debug(f"Opened input data from {input_file}")

            # Check input data
            if not check_input(input_data):
                logger.warning(
                    f'[{input_file}] Skipping input - Not in correct format'
                    '(E001)', exc_info=True)
                continue

            # Drop all columns except timestamp and value
            rhythmo_inputs = RhythmoInput(data = input_data.drop(
                columns = [col for col in input_data.columns if col not in ['timestamp', 'value']]),
                id_number = os.path.split(input_file)[-1].split('.')[0]) ## remove file extension and path

            try:
                rhythmo_outputs = self._run_rhythmo(rhythmo_inputs)
                logger.info(f"[{input_file}] Initiating output handlers.")
                self._run_output_handlers(rhythmo_inputs, rhythmo_outputs)

                logger.info(f"[{input_file}] FINISH Rhythmo in "
                            f"{time.perf_counter() - started:.3f}")
            except Exception as e:
                logger.error(f"[{input_file}] Failed to finish Rhythmo due to: {e}",
                             exc_info=True)

        logger.debug(f"Finished running rhythmo in {time.perf_counter() - overall_start} secs")

    def _run_rhythmo(self, rhythmo_inputs):
        """Runs rhythmo and returns the outputs"""

        rhythmo_outputs = RhythmoOutput.build_empty()
        
        rhythmo_outputs = process(rhythmo_inputs, rhythmo_outputs, self.parameters)
        rhythmo_outputs = decomp(rhythmo_inputs, rhythmo_outputs, self.parameters)
        if self.step == 1:
            return rhythmo_outputs

        rhythmo_outputs = selection(rhythmo_inputs, rhythmo_outputs, self.parameters)
        rhythmo_outputs = track(rhythmo_inputs, rhythmo_outputs, self.parameters)
        if self.step == 2:
            return rhythmo_outputs

        rhythmo_outputs = forecast(rhythmo_inputs, rhythmo_outputs, self.parameters)
        if self.step == 3:
            return rhythmo_outputs

        # rhythmo_outputs = schedule(rhythmo_inputs, rhythmo_outputs, self.parameters)

        return rhythmo_outputs

    def _run_output_handlers(self, rhythmo_inputs, rhythmo_outputs):
        """Runs output handlers for a given set of inputs/outputs and metrics"""
        for handler in self.outputs:
            handler(rhythmo_inputs, rhythmo_outputs, self.parameters)
