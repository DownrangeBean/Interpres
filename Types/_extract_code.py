def _dissect_line(self):
    if self._code_text:
        return self._code_text

    code_text = comment_text = self._line
    self._code_text = ['', '']

    if self.l_token:  # if left token was given
        l = self._contains(self.l_token, code_text)  # find it
        if l:  # if found
            logger.debug('_dissect_line: L')
            if not l[0] == 0:  # token is at the beginning of the text?
                self._code_text[0](self._r(code_text, l))   # add all text left of the symbol

            self._comment = self._l(comment_text, l)            # extract the comment as well
            code_text = code_text[l[1]:]                        # cut the texts for the next token search
            logger.debug('_comment after L: %s', self._comment)
            logger.debug('_code_text after L: %s', self._code_text)
            comment_text = self._comment

            self._openltoken = True                             # and flag the open left token

    if self.r_token:
        r_code = self._contains(self.r_token, code_text)
        r_comment = self.
        if r:
            self._openltoken = False  # Turn off open left token flag
            logger.debug('code.getter: code: R')
            logger.debug('code.getter: r[1] >= len(self._line) %s', r[1] >= len(self._line))
            if len(ret) < 1:
                ret.append('')
            if not r[1] >= len(code_text):
                ret.append(self._l(code_text, r))
    logger.debug('code.getter: if self.token: %s', bool(self.token))
    if self.token and not self._openltoken:  # token was given
        t = self._contains(self.token, code_text)  # find token in text
        logger.debug('code.getter: text: %s', code_text)
        logger.debug('code.getter: t and not (l or r): %s', t and not (l or r))
        if t and not (l or r):  # if token is found but no the other tokens
            logger.debug('code.getter: T')
            if not t[0] == 0:  # token starts at the beginning of the text?
                logger.debug('code.getter - code_text: %s', self._r(code_text, t))
                ret.append(self._r(code_text, t))  # add the code text to the return list as first element
                ret.append('')
    if ret:
        self._code_text = ret
        logger.debug('code.getter: comments detected: %s', str(ret))
    elif not self._openltoken:
        self._code_text[0] = self._line
        logger.debug('code.getter: no comments detected. Code.code will return entire string: %s', self._code_text)
    return self._code_text
