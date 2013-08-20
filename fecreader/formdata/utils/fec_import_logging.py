import logging

# should go in some non-django file; we'd then have to
LOG_DIRECTORY="/projects/realtimefec/log/"
LOG_NAME="fec_import"

""" Set up a logger with settings from the settings file. Will log info and anything higher.

from utils.fec_logging import fec_logger

my_logger=fec_logger()
my_logger.info('my_logger.info')
my_logger.warn('my_logger.warn')
my_logger.error('my_logger.error')
my_logger.critical('my_logger.critical')

-

2012-04-17 13:24:46,745 INFO my_logger.info
2012-04-17 13:24:46,745 WARNING my_logger.warn
2012-04-17 13:24:46,745 ERROR my_logger.error
2012-04-17 13:24:46,745 CRITICAL my_logger.critical

"""
def fec_logger():
    logger = logging.getLogger(LOG_NAME)
    hdlr = logging.FileHandler(LOG_DIRECTORY + LOG_NAME + '.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.ERROR)
    return logger
