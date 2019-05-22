import os
from Types.WordDocx import WordDocx
from Types.Code import Comments
from Util.Logging import get_logger
import Interpres_Globals

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)


class DocumentFactory(object):
    @staticmethod
    def make_dao(filepath):
        logger.debug('%s', filepath)

        dirpath, basename = os.path.split(filepath)
        base, ext = basename.split('.')

        logger.debug('ext: %s', ext)

        switcher = {'docx': WordDocx,
                    #'doc': WordDocx, - it seems that python -docx does not support opening these older files types
                    'py': Comments,
                    'c': Comments,
                    'h': Comments,
                    'cpp': Comments,
                    'asm': Comments}
        if ext in switcher.keys():
            logger.debug('%s', switcher[ext])
            return switcher[ext]
        else:
            logger.error("Cannot support this file extension.")
            raise ValueError
