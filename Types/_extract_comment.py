def comment(self):
    if self._comment:
        return self._comment

    text = self._line
    if self.l_token:
        l = self._contains(self.l_token, text)
        if l:
            text = self._l(text, l)

            self._openltoken = True  # Flag open left token

    if self.r_token:
        r = self._contains(self.r_token, text)
        if r:
            text = self._r(text, r)
            logger.debug('_comment after R: %s', text)
            self._openltoken = False  # Turn of flag for open left token

    if self.token and not self._openltoken:
        t = self._contains(self.token, text)
        if t and not (l or r):
            text = self._l(text, t)
            logger.debug('_comment after T: %s', text)

    self._comment = text
    if self._line == text and not self._openltoken:
        self._comment = ''
    return self._comment