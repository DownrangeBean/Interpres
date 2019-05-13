import unittest, logging, os, sys, Definitions
from unittest.mock import patch, Mock
from Util.Logging import get_logger
from Types.Code import Line
from Types.Code import Comments


logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)

TEST_OUT_DIR = Definitions.TEST_OUT_DIR


def setUpModule():
    if os.path.exists(TEST_OUT_DIR):
        logger.info('Deleting previous directory.')
        try:
            os.rmdir(TEST_OUT_DIR)
        except OSError:
            logger.error('Could not delete the entire tree.')
    else:
        os.makedirs(TEST_OUT_DIR, 0o777)
    logger.info('Created new test directory at: %s', TEST_OUT_DIR)


class TestLineClass(unittest.TestCase):
    def run_Line_tests(self, line, txin, txout, code, com, previous_line=None):
        try:
            with self.assertRaises(AttributeError):
                test = line.translate
            self.assertEqual(line.code, code)
            self.assertEqual(line.comment, com)
            line.text = txin
            self.assertEqual(line.translate, txout)
        except AssertionError:
            raise
        return line

    @staticmethod
    def create_multiline_test_data(ltoken, rtoken=None):
        if rtoken is None:
            rtoken = ltoken
        test_data = {}
        test_data.setdefault('input_strings', [ltoken + " A test to see how well we do", "with comments over two lines" + rtoken
                         , "Hello " + ltoken + " A pleasant greeting" + rtoken, ltoken + "Some random code" + rtoken + " say.helloworld()"])
        test_data.setdefault('code', [['', ''], ['', ''], ['Hello '], ['', ' say.helloworld()']])
        test_data.setdefault('comment', [' A test to see how well we do', 'with comments over two lines', ' A pleasant greeting'
                   , 'Some random code'])
        test_data.setdefault('output_string', [ltoken + "Test, jak dobře to děláme", " s komentáři na dvou řádcích" + rtoken
                         , "Hello " + ltoken + "Příjemný pozdrav" + rtoken, ltoken + "Nějaký náhodný kód" + rtoken + " say.helloworld()"])
        test_data.setdefault('translation_input', ["Test, jak dobře to děláme", " s komentáři na dvou řádcích"
                             , "Příjemný pozdrav", "Nějaký náhodný kód"])
        return test_data

    @staticmethod
    def create_singleline_test_data(token):
        test_data = {}
        test_data.setdefault('input', 'Hello world ' + token + ' say "Hello" to the world')
        test_data.setdefault('txin', ' říci "Ahoj" světu')
        test_data.setdefault('txout', 'Hello world ' + token + ' říci "Ahoj" světu')
        test_data.setdefault('code', ['Hello world '])
        test_data.setdefault('com', ' say "Hello" to the world')
        return test_data

    def test_py_token(self):
        ''' tests the properties of a Line object with python token'''
        data = TestLineClass.create_singleline_test_data('#')
        self.run_Line_tests(Line(data['input'], token="#", ltoken="'''")
                            , data['txin']           # Input translation
                            , data['txout']          # Output string
                            , data['code']           # Extracted code
                            , data['com'])           # Extracted comment

    def test_py_multiline_tokens(self):
        ''' tests the properties of a Line object with python l and r tokens'''
        data = TestLineClass.create_multiline_test_data("'''")
        previous_line = False
        for i in range(len(data['input_strings'])):
            previous_line = self.run_Line_tests(Line(data['input_strings'][i], ltoken="'''", plo=previous_line)
            , data['translation_input'][i]                  # Input translation
            , data['output_string'][i]                      # Output string
            , data['code'][i]                               # Extracted code
            , data['comment'][i]                            # Extracted comment
            , previous_line)

    def test_assembler_token(self):
        ''' tests the properties of a Line object with assembler token'''
        token = ';'
        ltoken = '/*'
        rtoken = '*/'
        data = TestLineClass.create_singleline_test_data(token)
        self.run_Line_tests(Line(data['input'], token=token, ltoken=ltoken, rtoken=rtoken)
                            , data['txin']  # Input translation
                            , data['txout']  # Output string
                            , data['code']  # Extracted code
                            , data['com'])  # Extracted comment

    def test_assembler_multiline_tokens(self):
        ''' tests the properties of a Line object with assembler l and r tokens'''
        ltoken = '/*'
        rtoken = '*/'
        data = TestLineClass.create_multiline_test_data(ltoken, rtoken)
        previous_line = False
        for i in range(len(data['input_strings'])):
            with self.subTest(input_string=data['input_strings'][i]):
                previous_line = self.run_Line_tests(Line(data['input_strings'][i], ltoken=ltoken, rtoken=rtoken
                                                         , plo=previous_line)
                                                    , data['translation_input'][i]  # Input translation
                                                    , data['output_string'][i]  # Output string
                                                    , data['code'][i]  # Extracted code
                                                    , data['comment'][i]  # Extracted comment
                                                    , previous_line)

    def test_cpp_token(self):
        ''' tests the properties of a Line object with cpp token'''
        token = '//'
        ltoken = '/*'
        rtoken = '*/'
        data = TestLineClass.create_singleline_test_data(token)
        self.run_Line_tests(Line(data['input'], token=token, ltoken=ltoken, rtoken=rtoken)
                            , data['txin']  # Input translation
                            , data['txout']  # Output string
                            , data['code']  # Extracted code
                            , data['com'])  # Extracted comment

    def test_cpp_multiline_tokens(self):
        ''' tests the properties of a Line object with cpp l and r tokens'''
        ltoken = '/*'
        rtoken = '*/'
        data = TestLineClass.create_multiline_test_data(ltoken, rtoken)
        previous_line = False
        for i in range(len(data['input_strings'])):
            previous_line = self.run_Line_tests(Line(data['input_strings'][i], ltoken=ltoken, rtoken=rtoken, plo=previous_line)
                                                , data['translation_input'][i]  # Input translation
                                                , data['output_string'][i]  # Output string
                                                , data['code'][i]  # Extracted code
                                                , data['comment'][i]  # Extracted comment
                                                , previous_line)


@patch('Types.Code.Line')
class TestCodeClass(unittest.TestCase):
    @staticmethod
    def create_test_file(lang_abb) -> str:
        dir = os.path.join(TEST_OUT_DIR, 'line_call_test.' + lang_abb)
        with open(dir, 'w+') as f:
            f.write('Hello world')
        return dir

    def test_py(self, mock_line):
        ''' tests the extraction method uses the correct tokens by mocking calls to the Line class'''
        file = TestCodeClass.create_test_file('py')
        with Comments(file) as doc:
            mock_line.assert_called_with('Hello world', '#', "'''", "'''", plo=False)

    def test_assembler(self, mock_line):
        ''' tests the extraction method uses the correct tokens by mocking calls to the Line class'''
        file = TestCodeClass.create_test_file('asm')
        with Comments(file) as doc:
            mock_line.assert_called_with('Hello world', ';', "/*", "*/", plo=False)

    def test_cpp(self, mock_line):
        ''' tests the extraction method uses the correct tokens by mocking calls to the Line class'''
        file = TestCodeClass.create_test_file('cpp')
        with Comments(file) as doc:
            mock_line.assert_called_with('Hello world', '//', "/*", "*/", plo=False)

    def test_c(self, mock_line):
        ''' tests the extraction method uses the correct tokens by mocking calls to the Line class'''
        file = TestCodeClass.create_test_file('c')
        with Comments(file) as doc:
            mock_line.assert_called_with('Hello world', '//', "/*", "*/", plo=False)

    def test_h(self, mock_line):
        ''' tests the extraction method uses the correct tokens by mocking calls to the Line class'''
        file = TestCodeClass.create_test_file('h')
        with Comments(file) as doc:
            mock_line.assert_called_with('Hello world', '//', "/*", "*/", plo=False)


class TestCodeBreakage(unittest.TestCase):
    ''' Use to add and fix new failures '''
    file_types = [['#', "'''", "'''"], [';', '/*', '*/'], ['//', '/*', '*/']]

    def test_reject_tokens_in_str(self):
        ''' tests the ability to reject comment tokens embedded in strings'''
        # TODO:
        for tokens in TestCodeBreakage.file_types:
            tok, ltok, rtok = tokens
            lines = ["'string with embedded " + tok + " tokens'"
                     , '"string with embedded ' + ltok + ' tokens"'
                     , '"string with embedded ' + rtok + ' tokens"'
                     , '"closed double with \' in it and a ' + tok + ' a quoted comment"']
            for i in range(len(lines)):
                line = Line(lines[i], tok, ltok, rtok)
                logger.debug('test_reject_tokens: lines[i]: %s', lines[i])
                self.assertEqual(lines[i], line.code[0])

    def test_reject_tokens_in_regex(self):
        ''' tests the ability to reject comment tokens embedded in regex'''
        # TODO:
        for tokens in TestCodeBreakage.file_types:
            tok, ltok, rtok = tokens
            lines = ["re.compile('(pattern using).+ (" + tok + "tokens){2,4}')"
                     , "re.compile('(pattern using).+ (" + ltok + "tokens){2,4}')"
                     , "re.compile('(pattern using).+ (" + rtok + "tokens){2,4}')"]
            for i in range(len(lines)):
                line = Line(lines[i], tok, ltok, rtok)
                self.assertEqual(lines[i], line.code[0])
