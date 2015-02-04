#coding:utf-8

# IDs used in other parts of PyLucid, too
MARKUP_CREOLE = 6
MARKUP_HTML = 0
MARKUP_HTML_EDITOR = 1
MARKUP_TINYTEXTILE = 2
MARKUP_TEXTILE = 3
MARKUP_MARKDOWN = 4
MARKUP_REST = 5

MARKUP_DATA = (
    # [0] = markup ID (e.g. database integer field)
    # [1] = lowcase, ASCII-only, no spaces (e.g. for filename)
    # [2] = verbose name (used e.g. in select input form)
    (MARKUP_CREOLE, u"creole", u'Creole wiki markup'),
    (MARKUP_HTML, u"html", u'html'),
    (MARKUP_HTML_EDITOR, u"htmleditor", u'html + JS-Editor'),
    (MARKUP_TINYTEXTILE, u"tinytextile", u'tinytextile'),
    (MARKUP_TEXTILE, u"textile", u'Textile (original)'),
    (MARKUP_MARKDOWN, u"markdown", u'Markdown'),
    (MARKUP_REST, u"rest", u'ReStructuredText'),
)
# For djanfo choice form field:
MARKUP_CHOICES = tuple([(data[0], data[2]) for data in MARKUP_DATA])

# For easy "get name by id":
MARKUP_DICT = dict(MARKUP_CHOICES)

# for mapping the ID with short name
MARKUP_SHORT_DICT = dict([(data[0], data[1]) for data in MARKUP_DATA])
