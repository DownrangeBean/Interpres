import logging


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
handler = logging.StreamHandler()
#formatter = logging.Formatter(' %(asctime)s  -  %(name)s  -  %(levelname)s  -  %(message)s')
formatter = logging.Formatter(' %(name)s  -  %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Paragraph(object):

    def __init__(self, para):
        self._para = para
        self._runs = []
        self._text = ''

    @property
    def text(self):
        if not self._text:
            if len(self.runs) > 1:
                self._text = ''.join([run._line for run in self.runs])
            elif len(self.runs) > 0:
                self._text = self.runs[0]._line
            else:
                self._text = ''
        logger.debug('text getter: ' + self._text)
        return self._text

    @text.setter
    def text(self, text):
        self._text = text

    @text.deleter
    def text(self):
        self._text = ''

    @property
    def runs(self):
        if self._runs:
            return self._runs

        page = None
        for j in range(len(self._para.runs)):
            cond = False
            if page:
                cond = page.text[-1] == ' ' or page.text[-1] == '\t' or page.text[-1] == '\n'
                logger.debug('using page condition')
            else:
                logger.debug('using run condition')
                if self._para.runs[j]._line:
                    cond = self._para.runs[j]._line[-1] == ' ' or self._para.runs[j]._line[-1] == '\t' or \
                           self._para.runs[j]._line[-1] == '\n'
            if cond:
                if page:
                    logger.debug('page: ' + str(page.__dict__))
                    self._runs.append(page)
                run = RunMessenger(text=self._para.runs[j]._line
                                                , bold=self._para.runs[j].bold
                                                , italic=self._para.runs[j].italic
                                                , underline=self._para.runs[j].underline
                                                , style=self._para.runs[j].style)
                self._runs.append(run)
                logger.debug('run: ' + str(run.__dict__))
                page = None

            elif page is None:
                page = RunMessenger(text=self._para.runs[j]._line
                               , bold=self._para.runs[j].bold
                               , italic=self._para.runs[j].italic
                               , underline=self._para.runs[j].underline
                               , style=self._para.runs[j].style)
            else:
                page.text += self._para.runs[j]._line

        if page:
            logger.debug('page: ' + str(page.__dict__))
            self._runs.append(page)
        return self._runs

    @runs.setter
    def runs(self, value):
        self._runs = value


class RunMessenger:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs




