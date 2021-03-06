import unittest, logging, os, sys
from Util.Logging import get_logger
from Types.Code import Comments
from TranslationTools.Translator import Translator
from Tests.WarningDecorators import ignore_warnings
import Interpres_Globals

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)


'''
Note. This test implicitly tests the function of the deprecated method 'setname' for docx instance. This may be removed
later along with the method. But the fault thrown that implicitly indicates an error in the naming of the document is:
    
docx.opc.exceptions.PackageNotFoundError: Package not found at 'EXPECTED-PATH-TO-OUTPUT-FILE'
'''

TEST_OUT_DIR = os.path.join(Interpres_Globals.TEST_OUT_DIR, __name__.replace('.', '_'))


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


class TestNaming(unittest.TestCase):
    @classmethod
    @ignore_warnings
    def setUpClass(cls):
        cls.test_directory = TEST_OUT_DIR

        cls.filename = 'Hello_world'
        cls.sep = '_'
        cls.id = 'code'
        cls.ext = '.py'
        localtest = os.path.join(cls.test_directory, cls.filename + cls.sep + cls.id + cls.ext)

        # Create test document
        doc = open(localtest, 'w+')
        doc.write('Hello world  # say "Hello" to the world.')

        cls.test_file_path = localtest

    @ignore_warnings
    def setUp(self):
        self.document = Comments(TestNaming().test_file_path)

    @ignore_warnings
    def test_source_provided_translation(self):
        '''Test1 fast translation with no language detect features used.'''
        name = 'T1'
        tx = Translator(source='en', destination='cs', mix=True)
        self.document.setname(extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. Testing not possible.')

        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + TestNaming().sep + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_eng_2_eng(self):
        '''Test2 English to English translation.'''
        name = 'T2'
        tx = Translator(source='en', mix=True)
        self.document.setname(extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n')
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + TestNaming().sep + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # say "Hello" to the world.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_quick_detect(self):
        '''Test3 quick language detection.'''
        name = 'T3'
        tx = Translator(destination='cs', quick=True, mix=True, extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n')
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + TestNaming().sep + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_dynamic_detect(self):
        '''Test4  dynamic language detection.'''
        name = 'T4'
        tx = Translator(destination='cs', dyn=True, mix=True)
        self.document.setname(extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n')
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + TestNaming().sep + name + TestNaming().ext)
        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_best_certainty(self):
        '''Test5  best certainty language detection.'''

        name = 'T5'
        tx = Translator(destination='cs', mix=True)
        self.document.setname(extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n%s\n*******', e)
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + TestNaming().sep + name + TestNaming().ext)
        print(local_filepath)
        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
            self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.')

    @ignore_warnings
    def test_destination_abbreviation_naming(self):
        '''Test6 add destination abbreviation.'''
        name = 'T6'
        tx = Translator(source='en', destination='cs', mix=True, abbreviation=True, extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n%s', e)
        try:
            self.document.save()
        except PermissionError:
            print('PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, TestNaming().filename + TestNaming().sep + TestNaming().id \
                         + '_cs_' + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_translated_name(self):
        '''Test7 name should be translated'''
        name = 'T7'
        tx = Translator(source='en', destination='cs', mix=True)
        self.document.setname(translate=True, extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n')
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, 'Ahoj_svět_kód_' \
                         + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # říci "Ahoj" světu.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

    @ignore_warnings
    def test_translated_and_dest_abbreviation_naming(self):
        '''Test8 name is translated and destination abbreviation added.'''
        name = 'T8'
        tx = Translator(source='en', destination='fr', mix=True, abbreviation=True, translate=True, extra=name)
        try:
            tx(self.document)
        except ValueError as e:
            logger.error('Google has blocked your current IP. We suggest you use a VPN if possible '
                          'or switch the VPN server you are using.\n*******\n')
        try:
            self.document.save()
        except PermissionError:
            print(
                'PermissionError: Close any instances of the files generated by this test unit and load the unit again.')

        local_filepath = os.path.join(TestNaming().test_directory, 'Bonjour_monde_code' \
                         + '_fr_' + name + TestNaming().ext)

        # Test translation:
        self.assertTrue(os.path.exists(local_filepath), 'This file has not been named correctly')
        with open(local_filepath, 'r+') as doc:
            line = doc.read()
        self.assertEqual(line, 'Hello world  # dites "bonjour" au monde.\n say "Hello" to the world.'
                         , 'Text is not as expected.')

if __name__ == '__main__':
    unittest.main()
