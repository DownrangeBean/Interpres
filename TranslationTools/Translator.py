import re, nltk, logging
from googletrans import Translator as googleTranslator
from Types.TranslatableDocument import TranslatableDocument
from Types.Code import Line
from Util.Logging import get_logger
import Interpres_Globals

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)


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
        logger.info('Translating: %s, %s', type(document).__name__, document.dirpath)
        if not len(document.source_text) > 0:
            logger.info("Nothing to translate.")
            return

        test_type = document.source_text[0]
        logger.debug('__call__ - len(document.source_text): %s', str(len(document.source_text)))
        logger.debug('__call__ - hasattr(test_type, "text"): %s'
                     , str(hasattr(test_type, 'text')))
        logger.debug('__call__ - isinstance(document.source_text[0], Line): %s'
                     , str(isinstance(document.source_text[0], Line)))
        logger.debug('__call__ - isinstance(document.source_text[0], str): %s'
                     , str(isinstance(document.source_text[0], str)))

        if isinstance(document.source_text[0], str):
            self._text = list(document.source_text)
        elif hasattr(document.source_text[0], 'text'):
            for obj in document.source_text:
                logger.debug('%s - adding text from object to self._text: %s', self._detect_source.__name__, obj.text)
                self._text.append(obj.text)

        logger.debug('source: %s', self._text)
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
                logger.debug('source: %s, destination: %s', self._text[i], document.source_text[i])
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
            logging.info('Adding destination language abbreviation: %s to end of file.', self.destination)
            document.newbase += obj.destination # for adding abbreviation to filename
        if obj.extra:
            logging.info('Adding callers provided text (%s) to end of filename.', obj.extra)
            if obj.abbreviation:
                obj.extra = '_' + obj.extra
            document.newbase += obj.extra

    @staticmethod
    def translate(text, src, dest):
        if not text:
            return text
        # Capture non-alphanumeric characters as google will strip these and they will need to be replaced
        start = ''
        end = ''
        non_alphanumeric = {' ', '\t', '\n', }
        if text[0] in non_alphanumeric:
            start = text[0]
        if text[-1] in non_alphanumeric:
            end = text[-1]

        new_text = googleTranslator().translate(text, src=src, dest=dest).text

        if start:
            new_text = start + new_text
        if end:
            new_text += end
        return new_text

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
                    logger.error('Block: %s, type: %s, len: %s', block, str(type(block)), str(len(block)))
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
        logger.debug('Language: %s, certainty: %s', lang, d.confidence)
        return lang, d.confidence

    def _detect_source(self, text=None):
        if text is None:
            local_text = self._text
        if text == '':
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
        logger.debug("_detect_source: local_text: %s", local_text)
        for block in local_text:
            logger.debug('%s - block: %s', self._detect_source.__name__, block)
            lang, cert = Translator().detectlang(block)
            detected.setdefault(cert, lang)
        logger.debug('%s - Returning detected language: %s', self._detect_source.__name__, detected[max(detected)])
        logger.debug('%s - len(detected): %s', self._detect_source.__name__, len(detected))
        return detected[max(detected)]
