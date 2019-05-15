#! python3
import argparse, sys, os, logging
from Util.Logging import get_logger
import Interpres_Globals

logger = get_logger(__name__)


parser = argparse.ArgumentParser(prog='TranslationTools',
                                 description='''TranslationTools documents in place; or phrases on the CLI. 
                                 --match without -d will use the current working directory. 
                                 To use CLI translator do not specify --match or -d. ''',
                                 epilog='Supported formats: ODG, docx, .py, .asm, .c, .h')
parser.add_argument('-v', '--verbose', action="count", help='More data!', default=0)
parser.add_argument('-d', dest='directories', nargs='+',
                                        help='A document path. Or a directory to search in (see: --match).')
parser.add_argument('-t', nargs='?', dest='target', const='cs', default='en',
                                        help='target language. Default: [en] English.')
parser.add_argument('-s', dest='source', help='source language. Default: auto-detect.')
parser.add_argument('--match', dest='keywords', action='append',
                                        help='file names in directory must contain %(dest)s for them to be translated.')
parser.add_argument('--grammar', dest='grammar', help='check grammar.', action="store_true")
parser.add_argument('--mix', dest='mix', help='mix source and target languages into output document.', action="store_true")
parser.add_argument('--dynamic', dest= 'dyn', help='detects language for each line. Good for multi-lingual documents', action="store_true")

group = parser.add_mutually_exclusive_group()
group.add_argument('-a', dest='abbreviation', action="store_true", default=False,
                   help="add the target langauage abbreviation to the file's name on output.")
group.add_argument('-n', '--name', dest='translate',
                    help='translate name of file on output.', action="store_true", default=False)
parser.add_argument('-e', dest='extra', default=False, help='Extra file tag, to be attached to end of file name (after '
                                                            'any abbreviation).')
parser.add_argument('-o', dest='output', help='Output directory. Default: same directory as source file.')

args = parser.parse_args()

############################################
#   Document translation                   #
############################################

verbosity_table = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
Interpres_Globals.VERBOSITY = verbosity_table[args.verbose + 1]     # Plus 1 as we do not have CRITICAL logs yet
print('verbosity: ', Interpres_Globals.VERBOSITY)                   # need to make more tests
print(args)

from Types.DocumentFactory import DocumentFactory
from TranslationTools.Translator import Translator
from TranslationTools.Decorators import fragile

#logger.setLevel(Interpres_Globals.VERBOSITY)

if args.directories or args.keywords:
    if args.directories:
        # Separate files-paths from directory-paths and check validity
        validPaths = [p for p in args.directories if os.path.exists(p)]
        if len(validPaths) != len(args.directories):
            print("ValueError: one or more paths given does not exist:\n",
                  [item for item in args.directories if item not in validPaths])
            sys.exit()
        directories = [d for d in validPaths if os.path.isdir(d)]
        files = [f for f in validPaths if f not in directories]
    else:
        files = list()
        directories = [os.getcwd(), ]

    # unpack all paths
    print('directories: %s', directories)
    if directories is not None:
        #files.extend([(d, file.split('.')) for d in directories for file in os.listdir(d)])
        for d in directories:
            for root, dirs, file_names in os.walk(d):
                for name in file_names:
                    file = os.path.join(root, name)
                    files.append(file)
                    logger.debug(file)

    logger.info('unpacking paths..')
    if Interpres_Globals.VERBOSITY < 20:            # Debug or less
        for f in files:
            logger.debug(f)

    # remove duplicates
    files = list(set(files))
    logger.info('removing duplicates..')

    if args.output:
        if os.path.exists(args.output):
            if not os.path.isdir(args.output):
                logger.error('Output directory must be a valid directory{} '.format(args.output))
                sys.exit()
        else:
            logger.info('Creating output directory.')
            try:
                os.mkdir(args.output, 0o777)
            except PermissionError:
                logger.error('Do not have permission to create output directory here. {}'.format(args.output))

    # create translator instance
    translator = Translator(source=args.source, destination=args.target, dyn=args.dyn, mix=args.mix, extra=args.extra,
                            abbreviation=args.abbreviation, translate=args.translate)
    logger.debug('src={}, dest={}, dyn={}, mix={}'.format(args.source, args.target, args.dyn, args.mix))

    # create concrete objects
    for path in files:
        try:
            with fragile(DocumentFactory.make_dao(path)(path)) as doc:
                if args.keywords:
                    for key in args.keywords:
                        if key not in doc:
                            fragile.Break
                if args.output:
                    doc.dirpath = args.output
                logger.debug('extra={}, abbreviation={}, translate={}'.format(args.extra, args.abbreviation, args.translate))
                translator(doc)
                logger.info('Document will be saved to: {}'.format(os.path.join(doc.dirpath, doc.newbase)))
        except ValueError:
            logging.debug('Cannot support format.')
    # Done?

############################################
#   CLI translation                        #
############################################
else:
    while True:
        buf = sys.stdin.readline()
        if buf is None:
            continue
        if not buf:
            break
        if args.source is None:
            source, confidence = Translator.detectlang(buf)
        else:
            source = args.source
            confidence = 'n.a'

        print("  + {} [{}]".format(Translator.translate(buf, src=source, dest=args.target), args.target))
        if args.verbose:
            print("    - certainty: [{}]".format(confidence))
