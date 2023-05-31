import logging


def get_logger() -> logging.Logger:
    """
    Get logger for the application.
    """

    logger = logging.getLogger('pyserver')
    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger
