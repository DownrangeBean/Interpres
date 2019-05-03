import re, nltk, logging
import Definitions
from Util.Logging import get_logger
from googletrans import Translator as googleTranslator
from Types.TranslatableDocument import TranslatableDocument
from Types import Code


logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)


class Translator(object):

    def __init__(self, source=None, destination='en', dyn=False, quick=False, mix=False, abbreviation=False, translate=False, extra=''):
        self.destination = destination
        self.dyn = dyn
        self.quick = quick
        self.mix = mix
        self.abbreviation = abbreviation
        self.translate_name = translate
        self.extra = extra
        self._text = list()
        self.source = source

    def get_source_from_user(self):
        if self.source:
            return self.source
        else:
            raise AttributeError('No source language has been provided')

    def __call__(self, document: TranslatableDocument):
        logger.info('Translating: {}'.format(type(document).__name__))
# FIXME: hasattribute does not function for test:
#       C:\Users\Ttron\OneDrive\Workspaces\PyCharm_Workspace\Interpres\Tests\Tests_out\Code\File_naming\Hello_world_code_T5.py
        logger.debug('__call__ - len(document.source_text): %s', str(len(document.source_text)))
        logger.debug('__call__ - isinstance(document.source_text[0], Line): %s',
                     str(isinstance(document.source_text[0], Code.Line)))
        logger.debug('__call__ - hasattr(document.source_text[0], "text": %s', str(hasattr(document.source_text[0], 'text')))
        logger.debug('__call__ - isinstance(document.source_text[0], str): %s', str(isinstance(document.source_text[0], str)))
        if isinstance(document.source_text[0], str):
            self._text = list(document.source_text)
        elif hasattr(document.source_text[0], 'text'):
            for obj in document.source_text:
                logger.debug('%s - adding text from object to self._text: %s', self._detect_source.__name__, obj.text)
                self._text.append(obj.text)

        logger.debug('source: {}'.format(document.source_text))
        new_text = list()
        source = ''
        logger.info('Performing language detection for the document: ')
        # Source is given
        if self.source:
            logger.info('Source has been provided by caller.')

        # Source becomes the first detected language
        elif self.quick:
            logger.info('[quick mode]')
            self.source = self._quick_detect()  # may raise exception ValueError

        # source language is detected for every line. Reverts to previous or first(detectable)
        # language if block cannot be detected
        elif self.dyn:
            logger.info('[dynamic mode]')

            for i in range(len(self._text)):
                source = ''
                source = Translator().detectlang(self._text[i])[0]
                if not source:
                    if not previous_source:
                        source = self._quick_detect(self._text[i+1])
                    else:
                        source = previous_source
                new_text.append((Translator.translate(self._text[i], src=source, dest=self.destination)
                                 + (self.mix and '\n' + self._text[i] or '')))
                logger.debug('source: {}, destination: {}'.format(self._text[i], document.source_text[i]))
                previous_source = source

        # Source is given the language with highest certainty for the document.
        else:
            logger.info('[Certainty mode]')
            self.source = self._detect_source()  # may raise exception ValueError

        if not new_text:
            logger.info('Source  language: {}'.format(self.source))
            for i in range(len(self._text)):
                new_text.append(Translator.translate(self._text[i], src=self.source, dest=self.destination)
                                + (self.mix and '\n' + self._text[i] or ''))
                logger.debug('translated text: "%s"', new_text[-1])

        if isinstance(document.source_text[0], str):
            logger.debug('Copying strings to document.destination_text')
            document.destination_text = new_text
        elif hasattr(document.source_text[0], 'text'):
            logger.debug('Copying source objects and adding translated text to text property.')
            i = 0
            for i in range(len(document.source_text)):
                logger.debug('Adding line[%d] to destination_text', i)
                obj = document.source_text[i]
                obj.text = new_text[i]
                document.destination_text.append(obj)

        self._translate_name(document)

    def _translate_name(self, document):
        # translate filename
        logger.info('Translating document name.')
        if document.setname_override:
            obj = document
        else:
            obj = self
        if obj.translate_name:
            s = document.base.replace('_', ' ').replace('-', ' ')
            tokens = nltk.word_tokenize(s)
            document.newbase = ''
            for t in tokens:
                document.newbase += googleTranslator().translate(t, src=self.source, dest=self.destination).text + '_'
        if obj.abbreviation:
            logging.info('Adding destination language abbreviation: {} to end of file.'.format(self.destination))
            document.newbase += obj.destination # for adding abbreviation to filename
        if obj.extra:
            logging.info('Adding callers provided text ({}) to end of filename.'.format(obj.extra))
            if obj.abbreviation:
                obj.extra = '_' + obj.extra
            document.newbase += obj.extra

    @staticmethod
    def translate(block, src, dest):
        # Capture non-alphanumeric characters as google will strip these and they will need to be replaced
        start = ''
        end = ''
        non_alphanumeric = {' ', '\t', '\n', }
        if block[0] in non_alphanumeric:
            start = block[0]
        if block[-1] in non_alphanumeric:
            end = block[-1]

        BLOCK = googleTranslator().translate(block, src=src, dest=dest).text

        if start:
            BLOCK = start + BLOCK
        if end:
            BLOCK += end
        return BLOCK

    def _quick_detect(self, text=None):
        if text is None:
            text = self._text
        logger.debug('Looking for first block of text with at least 1 words on which to apply the detection function.')
        for block in text:
            m = re.search(r'(\w+?\b\W*?){1,}', block)
            if m:
                try:
                    return Translator().detectlang(block)[0]
                except TypeError as e:
                    logger.error('Block: {}, type: {}, len: {}'.format(block, type(block), len(block)))
                    raise e
        raise (ValueError('Could not determine language from source text.'))

    @staticmethod
    def detectlang(b):
        logger.debug('..Asking google to detect language.')
        try:
            d = googleTranslator().detect(b)
        except ValueError as e:
            logger.debug('%s - error detected: %s', Translator.detectlang.__name__, e)
        lang = d.lang
        if len(lang) > 2:
            lang = lang[:2]
        logger.debug('Language: {}, certainty: {}'.format(lang, d.confidence))
        return lang, d.confidence

    def _detect_source(self, text=None):
        if text is None:
            local_text = self._text
        new_text = []
        for i in local_text:
            if isinstance(i, str):
                new_text.append(i)
            elif hasattr(i, 'text'):
                new_text.append(i.text)
        local_text = new_text
        detected = {}
        logger.debug('Detecting language for all blocks of text in document.')
        print(local_text)
        for block in local_text:
            logger.debug('%s - block: %s', self._detect_source.__name__, block)
            lang, cert = Translator().detectlang(block)
            detected.setdefault(cert, lang)
        logger.debug('%s - Returning detected language: %s', self._detect_source.__name__, detected[max(detected)])
        logger.debug('%s - len(detected): %s', self._detect_source.__name__, len(detected))
        return detected[max(detected)]
