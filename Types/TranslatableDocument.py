import nltk, os, sys, abc
import logging
from TranslationTools.Decorators import fragile


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter(' %(asctime)s  -  %(name)s  -  %(levelname)s  -  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class TranslatableDocument:

    def __init__(self, filepath):
        self.dirpath, basename = os.path.split(filepath)
        self.base, self.ext = basename.split('.')
        self.newbase = self.base + '_'
        self.document = None
        self.source_text = []
        self.destination = ''
        self.translate_name = ''
        self.abbreviation = ''
        self.extra = ''
        self.destination_text = []
        self.setname_override = False

        self._openDoc()
        self._extract_text()

    def __contains__(self, kw):
        logging.info('Searching document filename for keywords.')
        s = self.base.replace('_', ' ').replace('-', ' ')
        tokens = set(nltk.word_tokenize(s))
        if kw is str:
            return kw in tokens
        elif kw is list:
            for k in kw:
                if k in tokens:
                    return True
        else:
            raise TypeError('Types supported are list(str)|str.')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type == fragile.Break:
            return False
        try:
            self.save()
        except PermissionError:
            i = 0
            while i < 100:
                self.newbase = self.newbase.split('.')[0] + str(i) + self.newbase.split('.')[1]
                if os.path.exists(os.path.join(self.dirpath, self.newbase)):
                    continue
                break
            logger.warning('A document with the same name is still open. So the new document has been saved to {}.'.format(os.path.join(self.dirpath, self.newbase)))
        return False

    @staticmethod
    def translate(doc, tx , abbreviation=False, translate=False, extra=None):
        tx(doc)

    @abc.abstractmethod
    def _openDoc(self):
        '''
        Open document handle
        '''
        logging.debug('Opening document')

    def _checkdir(self, name):
        '''
        Used by the save function to create directories and add extensions
        :param name:
        :return:
        '''
        if name is None:
                logging.debug('Using generated filename: {}.'.format(self.newbase))
                pathname = os.path.join(self.dirpath, '.'.join([self.newbase, self.ext]))

        else:
            if len(os.path.basename(name).split('.')) > 1:
                logging.debug('Creating pathname with given name.')
                pathname = os.path.join(self.dirpath, name)

            else:
                logging.debug('No extension detected in given name. Using original extension.')
                pathname = os.path.join(self.dirpath, '.'.join([name, self.ext]))

        if not os.path.exists(os.path.dirname(pathname)):
            logging.debug('Creating new directory for new filename.')
            os.mkdir(pathname, 0o777)

        logging.info('new file path: {}'.format(pathname))
        return pathname

    def setname(self, abbreviation=False, translate=False, extra=''):
        '''
        Apply changes to self.basename
        :param abbreviation:[bool] tack destination language abbreviation onto the end of self.basename
        :param translate:[bool] translate self.basename
        :param extra: user defined text to add to end of name
        :return:
        '''
        self.setname_override = True
        if translate:
            self.translate_name = True
        if abbreviation:
            self.abbreviation = True
        if extra:
            self.extra = extra


    @abc.abstractmethod
    def _extract_text(self):
        """
        Retrieves the next that is/can be translated and returns it as a list. Each element of the list will be
        translated separately. So sentences should not span multiple elements.
            :param mix=True: if True, will have original language and target language into the same doc.
        """
        logging.debug('Extracting text which is to be translated.')

    @abc.abstractmethod
    def save(self, name=None):
        '''
        saves file with (new?)name
        :param name: optional override any name formed by settings
        '''
        logging.debug('Saving document.')

