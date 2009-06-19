# coding:utf-8

import re

CSS_RE = re.compile(r'#([a-fA-F0-9]{3,6})')

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

def extract_colors(content, existing_color_dict={}):
    """
    >>> extract_colors(".foo { color: #000000; }")
    ('.foo { color: {{ color_0 }}; }', {'color_0': '000000'})
    
    # it's case insensitivity:
    >>> extract_colors(".foo{color:#C9C573;} .bar{color:#c9c573;}")
    ('.foo{color:{{ color_0 }};} .bar{color:{{ color_0 }};}', {'color_0': 'c9c573'})
    
    You can give a existing color map:
    >>> existing_colors = {"black":"000000"}
    >>> extract_colors(".foo { color: #000000; }", existing_colors)
    ('.foo { color: {{ black }}; }', {'black': '000000'})
    """
    colors = set(CSS_RE.findall(content))
    color_dict = existing_color_dict
    temp = dict([(v,k) for k,v in existing_color_dict.iteritems()])
    for no, color in enumerate(colors):
        color_lower = color.lower()
        
        if color_lower in temp:
            # color exist in other case
            key = temp[color_lower]
        else:
            # new color
            key = "color_%s" % no
            color_dict[key] = color_lower
            temp[color_lower] = key
                
        content = content.replace("#%s" % color, "{{ %s }}" % key)
    
    return content, color_dict 
    

if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."