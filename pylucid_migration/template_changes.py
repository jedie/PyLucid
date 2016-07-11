
"""
    migrate Templates
    ~~~~~~~~~~~~~~~~~

    http://docs.django-cms.org/en/latest/reference/templatetags.html

    :copyleft: 2015 by the PyLucid team, see AUTHORS for more details.
    :created: 2015 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import re

from reversion_compare.helpers import unified_diff

def diff(old, new):
    old = old.splitlines()
    new = new.splitlines()
    diff = unified_diff(old, new, n=1)
    return "\n".join(diff)


REPLACES = (
    ("{{ page_language }}", "{{ LANGUAGE_CODE }}"),
    ("{{ page_description }}",'{% page_attribute "meta_description" %}'),
    ("{{ page_keywords }}",'{% page_attribute "meta_keywords" %}'),
    ("{{ page_permalink }}","{% page_url request.current_page %}"),
    (
        '"{{ page_lastupdatetime|date:_("DATETIME_FORMAT") }}"',
        '{% page_attribute "changed_date" as changed_date %}{{ changed_date|date:_("DATETIME_FORMAT") }}'
    ),
    # inserts:
    ("<head>", "<head>{% block meta_tags %}"),
)
RE_REPLACES = (
    (r"{{ (page_createtime.*?)}}","{# decativate: \g<1> #}"),
    (
        r'href="/static/(.*?)"',
        'href="{% static "\g<1>" %}"'
    ),
    (
        r'href="{{ STATIC_URL }}(.*?)"',
        'href="{% static "\g<1>" %}"'
    ),

    # TODO:
    (r"{{ (page_robots) }}","{# decativate: \g<1> #}"),
)

def migrate_template(content):
    old_content = content

    for before, after in REPLACES:
        content = content.replace(before, after)

    for re_before, re_after in RE_REPLACES:
        content = re.sub(re_before, re_after, content)

    print(diff(old_content, content))

    return content


