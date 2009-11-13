# coding:utf-8

import re

CSS_RE = re.compile(r'#([a-f0-9]{6}) *;', re.IGNORECASE)
CSS_CONVERT_RE = re.compile(r'#([a-f0-9])([a-f0-9])([a-f0-9]) *;', re.IGNORECASE)


def filter_content(content):
    """
    Skip all lines, start with .pygments - Used in update routine.
    Note: result is not valid CSS!
    """
    result = []
    for line in content.splitlines():
        line = line.strip()
        if line and not line.startswith(".pygments"):
            result.append(line)
    return "\n".join(result)

def extract_colors(content, existing_color_dict=None):
    """
    # TODO: Preprocess: Change all 3 length values to 6 length values for merging it.
    
    >>> extract_colors(".foo { color: #000000; }")
    ('.foo { color: {{ color_0 }}; }', {'color_0': '000000'})
    
    it's case insensitivity:
    >>> extract_colors(".foo{color:#C9C573;} .bar{color:#c9c573;}")
    ('.foo{color:{{ color_0 }};} .bar{color:{{ color_0 }};}', {'color_0': 'c9c573'})
    
    Convert/merge 3 length values:
    >>> extract_colors(".foo{color:#11AAff;} .bar{color:#1af;}")
    ('.foo{color:{{ color_0 }};} .bar{color:{{ color_0 }};}', {'color_0': '11aaff'})
    
    You can give a existing color map:
    >>> extract_colors(".foo { color: #000000; }", existing_color_dict={"black":"000000"})
    ('.foo { color: {{ black }}; }', {'black': '000000'})
    
    Skip non color values:
    >>> extract_colors("to short #12345; to long #1234567; /* no # 123; color #aa11ff-value */")
    ('to short #12345; to long #1234567; /* no # 123; color #aa11ff-value */', {})
    """
    # Convert all 3 length values to 6 length
    new_content = CSS_CONVERT_RE.sub("#\g<1>\g<1>\g<2>\g<2>\g<3>\g<3>;", content)

    colors = set(CSS_RE.findall(new_content))

    if existing_color_dict:
        color_dict = existing_color_dict
        exist_color = dict([(v, k) for k, v in existing_color_dict.iteritems()])
    else:
        color_dict = {}
        exist_color = {}

    for no, color in enumerate(colors):
        color_lower = color.lower()

        if color_lower in exist_color:
            # color exist in other case
            key = exist_color[color_lower]
        else:
            # new color
            key = "color_%s" % no
            color_dict[key] = color_lower
            exist_color[color_lower] = key

        new_content = new_content.replace("#%s" % color, "{{ %s }}" % key)

    return new_content, color_dict


if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
