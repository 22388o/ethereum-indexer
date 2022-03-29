#!/usr/bin/env python
import logging
import sys
from multiprocessing import Process

from config import Config
from extract.main import Extract
from transform.main import Transform


def extract_and_load(address: str) -> None:
    """
    Initiate and start extractor process.

    Args:
        address (str): Target wallet address for extractor
    """

    extract = Extract(address)
    extract()


def transform_and_load(to_transform: str) -> None:
    """
    Initiate and start transformer process.

    Args:
        to_transform (str): Transformer sub-directory name to be instantiated
    """

    transform = Transform(to_transform)
    transform()


def main():
    """Starts the whole ETL pipeline. Creates two separate processes.
    One for extraction, and one for transforming.
    """

    config = Config.azrael()

    logging.basicConfig(
        filename=config.get_log_filename(),
        level=logging.INFO,
        format="%(relativeCreated)6d %(process)d %(message)s",
    )

    # todo: graceful keyboard interrupt
    extractor = Process(target=extract_and_load, args=[config])
    transformer = Process(target=transform_and_load, args=[config])

    extractor.start()
    logging.info("Extractor started.")

    transformer.start()
    logging.info("Transformer started.")

    extractor.join()  # wait to finish
    transformer.join()  # wait to finish


if __name__ == "__main__":
    sys.exit(main())
