import logging, os, sys, Interpres_Globals


def get_logger(name):
    logger = logging.getLogger(name)
    if not os.path.exists(Interpres_Globals.LOG_FILE):
        with open(Interpres_Globals.LOG_FILE, 'w') as f:
            pass                                            # Create and truncate the file.

    if not logger.handlers:
        logger.propagate = 0

        formatter_short = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        formatter_long = logging.Formatter(' %(asctime)s  -  %(name)s  -  %(levelname)s  -  %(message)s')

        console = logging.StreamHandler()
        console.setLevel(Interpres_Globals.VERBOSITY)
        console.setFormatter(formatter_short)
        logger.addHandler(console)

        file = logging.FileHandler(Interpres_Globals.LOG_FILE)
        file.setLevel(logging.DEBUG)
        file.setFormatter(formatter_long)
        logger.addHandler(file)

    return logger
