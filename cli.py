import click
from logger.logger import get_logger
from main import Run

logger = get_logger(__name__)


@click.group()
def cli() -> None:
    pass


@cli.command(
    help=
    "For a given input or folder of inputs, rythmo processes the data and identifies cycles, returning the required ouput.")
@click.option(
    "-i", "--inputs", required=True,
    help="Comma separated list of data inputs, or a folder location containing data inputs.")
@click.option("-o", "--outputs", default="predict_future_phases",
              help="Comma separated list of outputs.")
@click.option("-p", "--parameters", default=None,
              help="Location of parameters file name in json format (e.g., ), allowing default paramters to be overwritten.")
def run(inputs, outputs, parameters) -> None:
    logger.debug("=== Running command ===")
    runtime = Run(
        inputs.split(',') if inputs else None,
        outputs.split(',') if outputs else ["predict_future_phases"],
        parameters if parameters else None)
    logger.debug("Runtime initialised, starting runtime.run()")
    try:
        runtime.run()
    except MemoryError as mem_error:
        logger.error(f"Task failed due to memory error: {mem_error}")
        raise mem_error
    except Exception as e:
        logger.error(f"Task failed due to: {e}", exc_info=True)
        raise e
