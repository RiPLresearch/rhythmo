from logger.logger import get_logger
logger = get_logger(__name__)

def find_min_projection_period(timing_of_future_phases):

    if timing_of_future_phases == 'regular_sampling':
        d = 1 ## TODO: add in code
    elif timing_of_future_phases == 'peak_trough':
        d = 1 ## TODO: add in code
    elif timing_of_future_phases == 'peak_trough_rising_falling':
        d = 1 ## TODO: add in code
    else:
        error_message = f"Timing of future phases {timing_of_future_phases} is not valid. Please either add this functionality or select one of: regular_sampling, peak_trough, peak_trough_rising_falling."
        logger.error(error_message, exc_info=True)
        raise ValueError(error_message)

    return

def schedule(_rhythmo_inputs, rhythmo_outputs, parameters):

    timing_of_future_phases = parameters.timing_of_future_phases
    number_of_future_phases = parameters.number_of_future_phases
    projection_duration = parameters.projection_duration
    
    rhythmo_outputs.future_phases = future_phases
    return rhythmo_outputs