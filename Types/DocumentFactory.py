import os, logging
from Types.WordDocx import WordDocx
from Types.Code import Comments

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.ERROR)
handler = logging.StreamHandler()
formatter = logging.Formatter(' %(asctime)s  -  %(name)s  -  %(levelname)s  -  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class DocumentFactory(object):
    @staticmethod
    def make_dao(filepath):
        logger.debug('%s', filepath)

        dirpath, basename = os.path.split(filepath)
        base, ext = basename.split('.')

        logger.debug('ext: {}'.format(ext))

        switcher = {'docx': WordDocx,
                    'doc': WordDocx,
                    'py': Comments,
                    'c': Comments,
                    'h': Comments,
                    'cpp': Comments,
                    'asm': Comments}
        logger.debug('%s', switcher[ext])
        return switcher[ext]
