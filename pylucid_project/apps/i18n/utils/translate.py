# coding: utf-8

"""
    google translation service
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    
    Note:
        Google Translate API v1 will be shut off completely on (December 1, 2011)
"""

import re, urllib

from django.utils import simplejson
from pylucid_project import VERSION_STRING


class UrlOpener(urllib.FancyURLopener):
    version = "pylucid/%s" % VERSION_STRING


BASE_URL = "http://ajax.googleapis.com/ajax/services/language/translate"


def translate(phrase, src="uk", to="en", debug=False):
    """
    https://code.google.com/apis/language/translate/overview.html
    
    based on:
    http://code.google.com/p/py-gtranslate/source/browse/trunk/gtrans.py
    """
    phrase = phrase.replace("\r\n", "<br />").replace("\r", "<br />").replace("\n", "<br />")

    data = urllib.urlencode({'v': '1.0', 'langpair': '%s|%s' % (src, to), 'q': phrase.encode('utf-8')})

    url_opener = UrlOpener()
    url = '%s?%s' % (BASE_URL, data)
    if debug:
        print "Request %r" % url
    f = url_opener.open(url)
    resp = simplejson.load(f)

    if debug:
        print "Response: %s" % repr(resp)

    content = ""
    error = None

    if resp["responseStatus"] != 200:
        error = resp["responseDetails"]
    else:
        try:
            content = resp['responseData']['translatedText']
        except KeyError, err:
            error = str(err)
        else:
            content = content.replace("<br />", "\n")

    return content, error


def prefill(source_form, dest_form, source_language, dest_language, only_fields=None, exclude_fields=None, debug=False):
    if exclude_fields is None:
        exclude_fields = ()

    filled_fields = []
    errors = []
    for field_name, source_value in source_form.cleaned_data.items():
        if only_fields is not None and field_name not in only_fields:
            continue
        if field_name in exclude_fields:
            continue

        if not isinstance(source_value, basestring):
            errors.append(
                "Can't translate '%(field_name)s', it's not a string. (value: %(value)s)" % {
                    "field_name":field_name, "value":repr(source_value)
                }
            )
            continue

        if not source_value:
            # Skip empty fields
            continue

        dest_key = dest_form.add_prefix(field_name)
        dest_value = dest_form.data[dest_key]
        if dest_value:
            # Don't overwrite content from the user.
            continue

        try:
            dest_value, error = translate(
                source_value, src=source_language.code, to=dest_language.code, debug=debug
            )
        except ValueError, err:
            errors.append(
                "Can't translate %(field_name)s with google: %(err)s" % {
                    "field_name":field_name, "err":err
                }
            )
        else:
            if error is not None:
                errors.append(error)
            if debug:
                print "%r translated to %r" % (source_value, dest_value)
            filled_fields.append(field_name)
            dest_form.data._mutable = True
            dest_form.data[dest_key] = dest_value
            dest_form.data._mutable = False
            dest_form.initial[field_name] = dest_value
            dest_form.fields[field_name].widget.attrs['class'] = 'auto_translated'

    return dest_form, filled_fields, errors


if __name__ == "__main__":
    print translate(phrase=u"Der Übersetzungsdienst von google...\n...ist das toll.", src="de", to="en")
