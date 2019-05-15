from odf.style import TextProperties
from Util.Logging import get_logger
import Interpres_Globals

logger = get_logger(__name__)
logger.setLevel(Interpres_Globals.VERBOSITY)


def _buildAttributesFromSource(src):
    attributes = {}
    for (n,k), v in src.attributes.items():
        attributes.setdefault(k.replace('-',''), v)
    return attributes


def shrinkFont(doc, stylename, by=2):
    return _modifyFont(doc, stylename, addto=(-by))
    # It is a safe bet that most translations from CZ to EN will grow in word count so it is good idea to drop 2 pt


def expandFont(doc, stylename, by=2):
    return _modifyFont(doc, stylename, addto=by)


def _modifyFont(doc, stylename, changeto=None, addto=0):
    '''

    :param doc: document handle
    :param stylename: style name which needs fontsize changing
    :param change: amount to change fontsize by; Ex. +2/-2
    :return: -1 if fail to find text-properties child node
    '''

    node = doc.getStyleByName(stylename)
    tp = TextProperties()
    for child in node.childNodes:
        if child.qname[1] == 'text-properties':
            tp = child
            break
    if tp is None:
        return -1
    attr = _buildAttributesFromSource(tp)
    if changeto:
        attr["fontsize"] = changeto
    else:
        attr["fontsize"] = str(int(attr["fontsize"].replace('pt',''))+addto) + 'pt'
    newTP = TextProperties(attributes=attr)
    node.insertBefore(newTP, tp)
    node.removeChild(tp)
