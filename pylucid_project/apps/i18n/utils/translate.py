# coding: utf-8

"""
    google translation service
    
    based on:
    http://code.google.com/p/py-gtranslate/source/browse/trunk/gtrans.py
"""

import re, urllib

from django.utils import simplejson


#class UrlOpener(urllib.FancyURLopener):
#    version = "py-gtranslate/1.0"


BASE_URL = "http://ajax.googleapis.com/ajax/services/language/translate"


def translate(phrase, src="uk", to="en"):
    """
    http://groups.google.com/group/google-ajax-search-api/browse_thread/thread/c325eb966891297d/bd9f00686e9c9120?show_docid=bd9f00686e9c9120
    """
    phrase = phrase.replace("\r\n", "<br />").replace("\r", "<br />").replace("\n", "<br />")

    data = urllib.urlencode({'v': '1.0', 'langpair': '%s|%s' % (src, to), 'q': phrase.encode('utf-8')})

    url_opener = urllib.FancyURLopener()
    f = url_opener.open('%s?%s' % (BASE_URL, data))
    resp = simplejson.load(f)

    try:
        content = resp['responseData']['translatedText']
    except:
        return ""

    content = content.replace("<br />", "\n")
    return content


if __name__ == "__main__":
    print translate(phrase=u"Der Übersetzungsdienst von google...\n...ist das toll.", src="de", to="en")
