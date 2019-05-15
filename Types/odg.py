from odf.opendocument import load
from odf.text import Span
from odf import teletype
from googletrans import Translator
import odf_util
import re, language_check
from Util.Logging import get_logger
import Interpres_Globals

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)

def translate_flow_diagram(filename, destination='en'):

    doc = load(filename)
    alltext = doc.getElementsByType(Span)

    # Create translation block
    translator = Translator()
    translations = translator.translate([addSpaces(teletype.extractText(t)) for t in alltext], dest='en', src='cs')

    # grammar check
    checkedText = [language_check.correct(translation._line, language_check.LanguageTool("en-US").check(
        translation._line)) for translation in translations]
    ###### test print translation
    #print([(translation.text, translation.origin) for translation in translations])
    ######

    # Replace old text with translation
    s = len(alltext)
    styleID = {}
    for i in range(s):
        newSpan = Span()
        old_style = alltext[i].getAttribute("stylename")
        styleID.setdefault(old_style, i)
        newSpan.setAttribute("stylename", old_style)
        newSpan.addText(translations[i]._line)
        alltext[i].parentNode.insertBefore(newSpan,alltext[i])
        alltext[i].parentNode.removeChild(alltext[i])

    #print(styleID.keys())
    for id in styleID.keys():
        if odf_util.shrinkFont(doc, id, by=2) == -1:
            print("Failed to shrink font: could not find 'text-properties'")

    doc.save('Tchv10_main_program2.odg')

def addSpaces(phrase):
    m = re.search(r'\b(?:\s|(\W))+\b', phrase)
    if m is not None:
        phrase = phrase.replace(m.group(), ' ' + m.group() + ' ')
    return phrase




if __name__ == '__main__':
    filename = 'Tchv10_hlavní_program.odg'
    translate_flow_diagram(filename)
