from __future__ import absolute_import

import os
import logging

# logger singleton
global logger
logger = None


def get_logger(path):
    """
    Returns a logger object that writes a log file to disk ( provided path )
    and to the stderr output.

    :param str path:
    :return: Logger
    :rtype: logging.RootLogger
    """

    # get logger
    global logger
    logger = logging.getLogger()

    # create logging file
    if path:
        logging_path = os.path.join(path, "log.log")
        logging.basicConfig(
            filename=logging_path,
            level=logging.DEBUG,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y/%m/%d/ %I:%M:%S",
        )
    
    # create logging to stderr
    stderr_logger = logging.StreamHandler()
    stderr_logger.setLevel(logging.INFO)
    stderr_logger.setFormatter(
        logging.Formatter("%(levelname)s | %(message)s")
    )

    logger.addHandler(stderr_logger)

    return logger


def get_maya_logger(path):
    """
    Returns a logger object that writes a log file to disk ( provided path )
    and to the stderr output.

    :param str path:
    :return: Logger
    :rtype: logging.RootLogger
    """
    # get logger
    global logger
    logger = logging.getLogger()

    # remove existing handlers
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # create logging file
    if path:
        logging_path = os.path.join(path, "log.log")
        file_logger = logging.FileHandler(logging_path)
        file_logger.setLevel(logging.DEBUG)
        file_logger.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                "%Y/%m/%d/ %I:%M:%S"
            )
        )

        logger.addHandler(file_logger)

    # create logging to stderr
    stderr_logger = logging.StreamHandler()
    stderr_logger.setLevel(logging.INFO)
    stderr_logger.setFormatter(
        logging.Formatter("%(levelname)s | %(message)s")
    )

    logger.addHandler(stderr_logger)

    return logger
