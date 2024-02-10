import logging
import logging.handlers
'''
   Setting up and return logger
'''


def setup_logger(module_name, log_file=None, level=logging.INFO):
    logger = logging.getLogger(module_name)
    logger.setLevel(level)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # create file handler
    if log_file is not None:
        fh = logging.handlers.TimedRotatingFileHandler(log_file, "D", 1)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
