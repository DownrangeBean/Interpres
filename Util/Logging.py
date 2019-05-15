import logging, os, sys, Interpres_Globals

LOG_FILE = os.path.join(Interpres_Globals.ROOT_DIR, 'Util', 'Interpres.log')


def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.propagate = 0

        formatter_short = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        formatter_long = logging.Formatter(' %(asctime)s  -  %(name)s  -  %(levelname)s  -  %(message)s')

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        console.setFormatter(formatter_short)
        logger.addHandler(console)

        file = logging.FileHandler(LOG_FILE)
        file.setLevel(logging.DEBUG)
        file.setFormatter(formatter_long)
        logger.addHandler(file)

    return logger
