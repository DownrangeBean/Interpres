#! python3
import argparse, sys, os, logging
from Util.Logging import get_logger
import Interpres_Globals


logger = get_logger(__name__)

########################################################################################################################
#  Argument parser
########################################################################################################################

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

########################################################################################################################
#   Setup logging                                                                                                      #
########################################################################################################################

with open(Interpres_Globals.LOG_FILE, 'w') as f:
    pass                                            # Truncate log file

verbosity_table = [logging.CRITICAL, logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
Interpres_Globals.VERBOSITY = verbosity_table[args.verbose + 1]     # Plus 1 as we do not have CRITICAL logs yet
logger.setLevel(Interpres_Globals.VERBOSITY)                        # need to make more tests
logger.debug('verbosity: %s', Interpres_Globals.VERBOSITY)
logger.debug(args)

from Types.DocumentFactory import DocumentFactory
from TranslationTools.Translator import Translator
from TranslationTools.Decorators import fragile

############################################
#   Document translation                   #
############################################

def handle_google(func, docu):
    try:
        func(docu)
    except ValueError as e:
        logger.info(e, 'Google may have blocked your current IP.')
        print('If possible please use/change your VPN and then continue.')
        while 1:
            choice = input('[C]ontinue, or [E]xit')
            if choice == 'C' or choice == 'E':
                if choice == 'C':
                    handle_google(func, docu)
                else:
                    sys.exit()


def prepare_output(out_dir, current_dir):
    output_ = ''
    if out_dir:
        out_dir = out_dir.replace("'", '').replace('"', '')
        if os.path.isdir(out_dir):
            output_ = out_dir
        elif os.path.exists(os.path.join(current_dir, out_dir)):
            output_ = os.path.join(current_dir, out_dir)
        elif os.path.splitdrive(out_dir)[0] == '':
            output_ = os.path.join(current_dir, out_dir)
        elif os.path.splitdrive(out_dir)[0].lower().isalpha():
            output_ = out_dir
        else:
            logger.error('Not a valid path.')
            sys.exit()
        if not os.path.exists(output_):
            try:
                os.mkdir(output_, 0o777)
                logger.info('Created output directory %s', output_)
            except PermissionError:
                logger.error('Do not have permission to create output directory here. %s', output_)
                sys.exit()
        logger.info('Using output directory %s', output_)
    return output_


if args.directories or args.keywords:
    if args.directories:
        # Separate files-paths from directory-paths and check validity
        validPaths = [p for p in args.directories if os.path.exists(p)]
        if len(validPaths) != len(args.directories):
            logger.error("\n\nValueError: one or more paths given with '-d' argument does not exist: %s\n",
                         str([item for item in args.directories if item not in validPaths]))
            sys.exit()
        directories = [d for d in validPaths if os.path.isdir(d)]
        files = [f for f in validPaths if f not in directories]
    else:
        files = list()
        directories = [os.getcwd(), ]

    # unpack all paths
    logger.debug('directories: %s', directories)
    if directories is not None:
        for d in directories:
            logger.info("currently searching in directory %s", d)
            for root, dirs, file_names in os.walk(d):
                if args.output and root == prepare_output(args.output, os.path.dirname(root)):
                    continue
                for name in file_names:
                    file = os.path.join(root, name)
                    files.append(file)
                    logger.debug(file)

    logger.info('unpacking paths..')
    if Interpres_Globals.VERBOSITY < 20:  # Debug or less
        for f in files:
            logger.debug(f)

    # remove duplicates
    files = list(set(files))
    logger.info('removing duplicates..')

    # create translator instance
    logger.info("Creating translator.")
    translator = Translator(source=args.source, destination=args.target, dyn=args.dyn, mix=args.mix,
                            extra=args.extra,
                            abbreviation=args.abbreviation, translate=args.translate)
    logger.debug('src=%s, dest=%s, dyn=%s, mix=%s', args.source, args.target, args.dyn, args.mix)

    extension_counter = {}
    # create concrete objects
    for path in files:
        try:
            with fragile(DocumentFactory.make_dao(path)(path)) as doc:
                if args.keywords:
                    if not [True for key in args.keywords if key in doc]:
                        doc.close()             # safely close document handle
                        fragile.Break
                if args.output:
                    doc.dirpath = prepare_output(args.output, os.path.dirname(path))
                logger.debug('extra=%s, abbreviation=%s, translate=%s', args.extra, args.abbreviation,
                             args.translate)

                # Test if document already exists so we can skip it.
                old_name = doc.newbase
                translator._translate_name(doc)
                new_name = doc.newbase
                doc.newbase = old_name
                path = os.path.join(doc.dirpath, new_name + os.path.extsep + doc.ext)
                logger.debug("testing existence with constructed path %s", path)

                if os.path.exists(path):
                    logger.info("Skipping file %s as it already exists.", path)
                    doc.close()                 # safely close document handle
                    fragile.Break               # skip if the file already exists.
                                                # this is to reduce the load going to google and the chance that google
                                                # will block the ip address

                handle_google(translator, doc)  # Handle google blocking by waiting for user to change vpn
                extension_counter[doc.ext] = extension_counter.setdefault(doc.ext, 0) + 1
                logger.info('Document will be saved to: %s', os.path.join(doc.dirpath, doc.newbase))
        except ValueError:
            logger.warning('Cannot support format. %s', os.path.split(os.path.basename(path))[1])
        except AssertionError:
            logger.warning('This file is empty: %s', path)
    print("Data types parsed: ", str(extension_counter))
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
