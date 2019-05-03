import unittest


class TestTranslator(unittest.TestCase):
    def test_anti_stripping(self):
        from TranslationTools.Translator import Translator
        a = 'Hello '
        b = ' world'
        c = 'Hello\t'
        d = '\tworld'
        e = 'Hello\n'
        f = '\nworld'
        A = Translator().translate(a, 'en', 'en')
        B = Translator().translate(b, 'en', 'en')
        C = Translator().translate(c, 'en', 'en')
        D = Translator().translate(d, 'en', 'en')
        E = Translator().translate(e, 'en', 'en')
        F = Translator().translate(f, 'en', 'en')

        self.assertEqual(a + b, A + B)
        self.assertEqual(c + d, C + D)
        self.assertEqual(e + f, E + F)


if __name__ == '__main__':
    unittest.main()
