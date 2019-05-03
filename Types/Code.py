import re
import os
import logging
from Util.Logging import get_logger
import sys
from Types.TranslatableDocument import TranslatableDocument
from TranslationTools.Translator import Translator

logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)


class Comments (TranslatableDocument):

    def __init__(self, filepath):
        super(Comments, self).__init__(filepath)
        self.token = None

    def _openDoc(self):
        self.document = open(os.path.join(self.dirpath, '.'.join((self.base, self.ext))), 'r+')

    def save(self, name=None):
        self.document.close()
        pathname = self._checkdir(name)
        with open(pathname, 'w') as f:
            i = 0
            for line in self.destination_text:
                if isinstance(line, Line):
                    logger.debug('Saving line[%d] to document: %s', i, line.translate)
                    f.write(line.translate)
                    logger.debug('line written to file: %s', line.translate)
                else:
                    logger.debug(line)
                    f.write(line)
                i += 1

    def set_token(self, token):
        self.token = token

    def _extract_text(self):
        # get token(s)
        ltoken = rtoken = token = None

        if self.ext == 'asm':
            token = ';'
            ltoken = '/*'
            rtoken = '*/'

        elif self.ext == 'c' or self.ext == 'h' or self.ext == 'cpp':
            token = '//'
            ltoken = '/*'
            rtoken = '*/'

        elif self.ext == 'py':
            token = '#'
            ltoken = "'''"
            rtoken = "'''"

        elif self.token:
            token = self.token

        i = 0
        previous_line = False
        for l in self.document:
            logger.debug('_extract_text - Adding line[%d] to source_text', i)
            line = Line(l, token, ltoken, rtoken, plo=previous_line)
            previous_line = line
            self.source_text.append(line)


class Line:
    def __init__(self, line, token=None, ltoken=None, rtoken=None, plo=False):
        '''

        :param line: string of text to instantiate object
        :param token: major one line comment indication token
        :param ltoken: start-of multi line comment indication token
        :param rtoken: end-of multi line comment indication token
        :param plo: [previous-line-object] this will allow for the capture of multi line comments where the token is the same
        '''
        self._line = line
        self._comment = ''
        self._code_text = ''
        self._reforged = ''
        self._translated_comment = ''
        self.token = token
        self.l_token = ltoken
        self._openltoken = ''
        self._open_quotes = False # temp
        self._double_open = False # temp
        self._single_open = False # temp


        if isinstance(plo, self.__class__):
            self._plo_open = plo._open_quotes
            self._openltoken = plo.has_open_comment
            self._double_open = plo._double_open  # temp
            self._single_open = plo._single_open  # temp
        elif isinstance(plo, bool):
            self._plo_open = plo
            self._openltoken = plo
            self._double_open = plo  # temp
            self._single_open = plo  # temp
        else:
            self._openltoken = False


        if rtoken:
            self.r_token = rtoken
        else:
            self.r_token = ltoken
        if self._openltoken:
            self.l_token = None

    def _contains(self, item, text=None):
        if text is None:
            text = self._line
        logger.debug('_contains input-text: %s, token: %s', text, item)
        m = self.find_tokens_one(text, item)
        logger.debug('_contains.match@ %s', m)
        if m:
            return m
        return False

    def find_tokens_one(self, string, token):
        def sort_span(m):
            return m.span()[0]
        if self._openltoken:                                # In this state all text from the left is a comment and
            self._double_open = self._single_open = False   # we are only looking for the closing token self.rtoken
            return re.search(token, string).span()
        tokens = re.findall(re.escape(token), string)
        DOUBLE = '"'
        SINGLE = "'"
        d = re.findall(DOUBLE, string)
        s = re.findall(SINGLE, string)
        all = list(tokens)
        all.extend(d)
        all.extend(s)
        if token != "'''":
            TRIPLE = "'''"
            t = re.findall(TRIPLE, string)
            all.extend(t)
            new_all = []
            if t:
                for i in all:
                    if not t[0] <= i.span()[0] <= t[1]:
                        new_all.append(i)
            all = new_all
        all.sort(key=sort_span)
        double = int(self._double_open)
        single = int(self._single_open)
        logger.debug('%s - tokens and quotes: %s', self.find_tokens_one.__name__, all)
        ret = ''
        for item in all:
            if ret:
                if ret[0] <= item.span()[0] <= ret[1]:
                    logger.debug('%s - Skipping incorrect detection of quote inside of token', self.find_tokens_one.__name__)
                    continue
            logger.debug('%s - item: %s', self.find_tokens_one.__name__, item.group())
            logger.debug('%s - single mod 2 == 0: %s', self.find_tokens_one.__name__, str(single % 2 == 0))
            logger.debug('%s - double mod 2 == 0: %s', self.find_tokens_one.__name__, str(double % 2 == 0))
            if item.group() == DOUBLE and single % 2 == 0:
                double += 1
                continue
            if item.group() == SINGLE and double % 2 == 0:
                single += 1
                continue
            if item.group() == token:
                if double % 2 == 0 and single % 2 == 0:
                    logger.debug('%s - returning %s', self.find_tokens_one.__name__, item.span())
                    ret = item.span()

        if double % 2 == 1:
            self._double_open = True
        if single % 2 == 1:
            self._single_open = True
        if ret:
            return ret
        return None

    def _l(self, text, m, offs=0): return text[m[1] - offs:]

    def _r(self, text, m, offs=0): return text[:m[0] + offs]

    @property
    def text(self):
        return self.comment

    @text.setter
    def text(self, text_input):
        self.translate = text_input

    @property
    def has_open_comment(self):
        text = self._line
        ret = False
        if self.l_token:
            l = self._contains(self.l_token, text)
            if l:
                text = text[l[1]:]
                ret = True
        if self.r_token:
            if self._contains(self.r_token, text):
                ret = False
        return ret

    @property
    def comment(self):
        if self._comment:
            return self._comment

        text = self._line
        if self.l_token:
            l = self._contains(self.l_token, text)
            if l:
                text = self._l(text, l)
                logger.debug('_comment after L: %s', text)

        if self.r_token:
            r = self._contains(self.r_token, text)
            if r:
                text = self._r(text, r)
                logger.debug('_comment after R: %s', text)

        if self.token:
            t = self._contains(self.token, text)
            if t and not (l or r):
                text = self._l(text, t)
                logger.debug('_comment after T: %s', text)

        self._comment = text
        if self._line == text and not self._openltoken:
            self._comment = ''
        return self._comment

    @comment.setter
    def comment(self, text):
        self._comment = text

    @comment.deleter
    def comment(self):
        del self._comment

    @property
    def code(self):
        if self._code_text:
            return self._code_text

        text = self._line
        ret = []
        self._code_text = ['', '']

        if self.l_token:                                # if left token was given
            l = self._contains(self.l_token, text)      # find it
            if l:                                       # if found
                logger.debug('code.getter: code: L')
                if not l[0] == 0:                       # token is at the beginning of the text?
                    ret.append(self._r(text, l))        # add all text left of the symbol
                text = text[l[1]:]                      # there is no code and so just cut the text for the next search

        if self.r_token:
            r = self._contains(self.r_token, text)
            if r:
                logger.debug('code.getter: code: R')
                logger.debug('code.getter: r[1] >= len(self._line) %s', r[1] >= len(self._line))
                if len(ret) < 1:
                    ret.append('')
                if not r[1] >= len(text):
                    ret.append(self._l(text, r))
        logger.debug('code.getter: if self.token: %s', bool(self.token))
        if self.token:                                  # token was given
            t = self._contains(self.token, text)        # find token in text
            logger.debug('code.getter: text: %s', text)
            logger.debug('code.getter: t and not (l or r): %s', t and not (l or r))
            if t and not (l or r):                      # if token is found but no the other tokens
                logger.debug('code.getter: T')
                if not t[0] == 0:                       # token starts at the beginning of the text?
                    logger.debug('code.getter - code_text: %s', self._r(text, t))
                    ret.append(self._r(text, t))        # add the code text to the return list as first element
                    ret.append('')
        if ret:
            self._code_text = ret
            logger.debug('code.getter: comments detected: %s, %s', ret[0], ret[1])
        elif not self._openltoken:
            self._code_text[0] = self._line
            logger.debug('code.getter: no comments detected. Code.code will return entire string: %s', self._code_text)
        return self._code_text

    @code.setter
    def code(self, text):
        self._code_text = text

    @code.deleter
    def code(self):
        del self._code_text

# FIXME: make it possible to use Transaltor's call function and to pass the Translator in as an object (probably dont need to do this)
    @property
    def translate(self):
        if self._reforged:
            return self._reforged
        raise AttributeError('Property has not been set. This property has no initial value')

    @translate.setter
    def translate(self, translation):
        if not self._code_text:
            self.code
        if not self._comment:
            self.comment

        text = self._line
        self._reforged = ''
        self._translated_comment = translation
        if self.l_token:
            l = self._contains(self.l_token, text)
            if l:
                logger.debug('reforging for left token.')
                self._reforged = self._code_text[0] + self.l_token
                text = text[l[1]:]
        logger.debug('_reforged after L: %s', self._reforged)

        self._reforged += self._translated_comment
        logger.debug('_reforged after adding the translated text: %s', self._reforged)

        if self.r_token:
            r = self._contains(self.r_token, text)
            if r:
                logger.debug('reforging for right token.')
                test = (len(self._code_text) > 1)
                self._reforged = self._reforged + self.r_token + (test and self._code_text[1] or '')

        logger.debug('_reforged after R: %s', self._reforged)

        if self.token:
            if self._contains(self.token) and not (l or r):
                self._reforged = self._code_text[0] + self.token + self._translated_comment
                logger.debug('reforging for single token: %s + %s + %s'
                             , self._code_text[0]
                             , self.token
                             , self._translated_comment)
        logger.debug('reforged after T: %s', self._reforged)
        if not self._reforged:
            logger.debug('translate.getter: self._line does not _contain any tokens. '
                         '\nSetting self._reforged to self._line')
            self._reforged = self._line


def token_b4_txt(token, text):
    m = re.search(token, text)
    if m:
        return text[m.span()[1]:]
    return False


def txt_b4_token(token, text):
    m = re.search(token, text)
    if m:
        return text[:m.span()[0]]
    return False

def txt_in_tokens(text, ltoken, rtoken=None, mem=''):
    if rtoken is None:
        rtoken = ltoken
    if not mem:
        lh = token_b4_txt(ltoken, text)
        if not lh:
            return {'ltoken': ltoken, 'rtoken': rtoken, 'mem': mem}
        text = lh
    rh = txt_b4_token(rtoken, text)
    if rh:
        return mem + rh
    mem = mem + text
    return {'ltoken': ltoken, 'rtoken': rtoken, 'mem': mem}

# FIXME: use re.compile.scanner
#  'https://www.programcreek.com/python/example/53972/re.Scanner'



