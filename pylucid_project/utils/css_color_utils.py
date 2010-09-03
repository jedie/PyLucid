# coding:utf-8

"""
    CSS color utilities
    ~~~~~~~~~~~~~~~~~~~
    
    
    some parts are borrowed from colorname sourcecode (GPL v2):
        http://code.foosel.org/colorname (
        by: Philippe 'demod' Neumann and Gina 'foosel' Häußge
        
    :copyleft: 2009-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import re
import math


CSS_RE = re.compile(r'#([a-f0-9]{6})[\s;]', re.IGNORECASE)
CSS_CONVERT_RE = re.compile(r'#([a-f0-9])([a-f0-9])([a-f0-9]) *;', re.IGNORECASE)


class ColorVector(tuple):
    def __sub__(self, v):
        return (self[0] - v[0], self[1] - v[1], self[2] - v[2])

COLOR_NAMES = { # CSS3 names, http://www.w3.org/TR/css3-color/
    'indigo': ColorVector((75, 0, 130)),
    'gold': ColorVector((255, 215, 0)),
    'hotpink': ColorVector((255, 105, 180)),
    'firebrick': ColorVector((178, 34, 34)),
    'indianred': ColorVector((205, 92, 92)),
    'yellow': ColorVector((255, 255, 0)),
    'mistyrose': ColorVector((255, 228, 225)),
    'darkolivegreen': ColorVector((85, 107, 47)),
    'olive': ColorVector((128, 128, 0)),
    'darkseagreen': ColorVector((143, 188, 143)),
    'pink': ColorVector((255, 192, 203)),
    'tomato': ColorVector((255, 99, 71)),
    'lightcoral': ColorVector((240, 128, 128)),
    'orangered': ColorVector((255, 69, 0)),
    'navajowhite': ColorVector((255, 222, 173)),
    'lime': ColorVector((0, 255, 0)),
    'palegreen': ColorVector((152, 251, 152)),
    'darkslategrey': ColorVector((47, 79, 79)),
    'greenyellow': ColorVector((173, 255, 47)),
    'burlywood': ColorVector((222, 184, 135)),
    'seashell': ColorVector((255, 245, 238)),
    'mediumspringgreen': ColorVector((0, 250, 154)),
    'fuchsia': ColorVector((255, 0, 255)),
    'papayawhip': ColorVector((255, 239, 213)),
    'blanchedalmond': ColorVector((255, 235, 205)),
    'chartreuse': ColorVector((127, 255, 0)),
    'dimgray': ColorVector((105, 105, 105)),
    'black': ColorVector((0, 0, 0)),
    'peachpuff': ColorVector((255, 218, 185)),
    'springgreen': ColorVector((0, 255, 127)),
    'aquamarine': ColorVector((127, 255, 212)),
    'white': ColorVector((255, 255, 255)),
    'orange': ColorVector((255, 165, 0)),
    'lightsalmon': ColorVector((255, 160, 122)),
    'darkslategray': ColorVector((47, 79, 79)),
    'brown': ColorVector((165, 42, 42)),
    'ivory': ColorVector((255, 255, 240)),
    'dodgerblue': ColorVector((30, 144, 255)),
    'peru': ColorVector((205, 133, 63)),
    'lawngreen': ColorVector((124, 252, 0)),
    'chocolate': ColorVector((210, 105, 30)),
    'crimson': ColorVector((220, 20, 60)),
    'forestgreen': ColorVector((34, 139, 34)),
    'darkgrey': ColorVector((169, 169, 169)),
    'lightseagreen': ColorVector((32, 178, 170)),
    'cyan': ColorVector((0, 255, 255)),
    'mintcream': ColorVector((245, 255, 250)),
    'silver': ColorVector((192, 192, 192)),
    'antiquewhite': ColorVector((250, 235, 215)),
    'mediumorchid': ColorVector((186, 85, 211)),
    'skyblue': ColorVector((135, 206, 235)),
    'gray': ColorVector((128, 128, 128)),
    'darkturquoise': ColorVector((0, 206, 209)),
    'goldenrod': ColorVector((218, 165, 32)),
    'darkgreen': ColorVector((0, 100, 0)),
    'floralwhite': ColorVector((255, 250, 240)),
    'darkviolet': ColorVector((148, 0, 211)),
    'darkgray': ColorVector((169, 169, 169)),
    'moccasin': ColorVector((255, 228, 181)),
    'saddlebrown': ColorVector((139, 69, 19)),
    'grey': ColorVector((128, 128, 128)),
    'darkslateblue': ColorVector((72, 61, 139)),
    'lightskyblue': ColorVector((135, 206, 250)),
    'lightpink': ColorVector((255, 182, 193)),
    'mediumvioletred': ColorVector((199, 21, 133)),
    'slategrey': ColorVector((112, 128, 144)),
    'red': ColorVector((255, 0, 0)),
    'deeppink': ColorVector((255, 20, 147)),
    'limegreen': ColorVector((50, 205, 50)),
    'darkmagenta': ColorVector((139, 0, 139)),
    'palegoldenrod': ColorVector((238, 232, 170)),
    'plum': ColorVector((221, 160, 221)),
    'turquoise': ColorVector((64, 224, 208)),
    'lightgrey': ColorVector((211, 211, 211)),
    'lightgoldenrodyellow': ColorVector((250, 250, 210)),
    'darkgoldenrod': ColorVector((184, 134, 11)),
    'lavender': ColorVector((230, 230, 250)),
    'maroon': ColorVector((128, 0, 0)),
    'yellowgreen': ColorVector((154, 205, 50)),
    'sandybrown': ColorVector((244, 164, 96)),
    'thistle': ColorVector((216, 191, 216)),
    'violet': ColorVector((238, 130, 238)),
    'navy': ColorVector((0, 0, 128)),
    'magenta': ColorVector((255, 0, 255)),
    'dimgrey': ColorVector((105, 105, 105)),
    'tan': ColorVector((210, 180, 140)),
    'rosybrown': ColorVector((188, 143, 143)),
    'olivedrab': ColorVector((107, 142, 35)),
    'blue': ColorVector((0, 0, 255)),
    'lightblue': ColorVector((173, 216, 230)),
    'ghostwhite': ColorVector((248, 248, 255)),
    'honeydew': ColorVector((240, 255, 240)),
    'cornflowerblue': ColorVector((100, 149, 237)),
    'slateblue': ColorVector((106, 90, 205)),
    'linen': ColorVector((250, 240, 230)),
    'darkblue': ColorVector((0, 0, 139)),
    'powderblue': ColorVector((176, 224, 230)),
    'seagreen': ColorVector((46, 139, 87)),
    'darkkhaki': ColorVector((189, 183, 107)),
    'snow': ColorVector((255, 250, 250)),
    'sienna': ColorVector((160, 82, 45)),
    'mediumblue': ColorVector((0, 0, 205)),
    'royalblue': ColorVector((65, 105, 225)),
    'lightcyan': ColorVector((224, 255, 255)),
    'green': ColorVector((0, 128, 0)),
    'mediumpurple': ColorVector((147, 112, 216)),
    'midnightblue': ColorVector((25, 25, 112)),
    'cornsilk': ColorVector((255, 248, 220)),
    'paleturquoise': ColorVector((175, 238, 238)),
    'bisque': ColorVector((255, 228, 196)),
    'slategray': ColorVector((112, 128, 144)),
    'darkcyan': ColorVector((0, 139, 139)),
    'khaki': ColorVector((240, 230, 140)),
    'wheat': ColorVector((245, 222, 179)),
    'teal': ColorVector((0, 128, 128)),
    'darkorchid': ColorVector((153, 50, 204)),
    'deepskyblue': ColorVector((0, 191, 255)),
    'salmon': ColorVector((250, 128, 114)),
    'darkred': ColorVector((139, 0, 0)),
    'steelblue': ColorVector((70, 130, 180)),
    'palevioletred': ColorVector((216, 112, 147)),
    'lightslategray': ColorVector((119, 136, 153)),
    'aliceblue': ColorVector((240, 248, 255)),
    'lightslategrey': ColorVector((119, 136, 153)),
    'lightgreen': ColorVector((144, 238, 144)),
    'orchid': ColorVector((218, 112, 214)),
    'gainsboro': ColorVector((220, 220, 220)),
    'mediumseagreen': ColorVector((60, 179, 113)),
    'lightgray': ColorVector((211, 211, 211)),
    'mediumturquoise': ColorVector((72, 209, 204)),
    'lemonchiffon': ColorVector((255, 250, 205)),
    'cadetblue': ColorVector((95, 158, 160)),
    'lightyellow': ColorVector((255, 255, 224)),
    'lavenderblush': ColorVector((255, 240, 245)),
    'coral': ColorVector((255, 127, 80)),
    'purple': ColorVector((128, 0, 128)),
    'aqua': ColorVector((0, 255, 255)),
    'whitesmoke': ColorVector((245, 245, 245)),
    'mediumslateblue': ColorVector((123, 104, 238)),
    'darkorange': ColorVector((255, 140, 0)),
    'mediumaquamarine': ColorVector((102, 205, 170)),
    'darksalmon': ColorVector((233, 150, 122)),
    'beige': ColorVector((245, 245, 220)),
    'blueviolet': ColorVector((138, 43, 226)),
    'azure': ColorVector((240, 255, 255)),
    'lightsteelblue': ColorVector((176, 196, 222)),
    'oldlace': ColorVector((253, 245, 230)),
}


def hypot(a, b):
    return math.sqrt(a * a + b * b)


def calc_distance(a, b):
    """
    @return: the euclidean distance between the vectors "a" and "b"
    @param a,b: ColorVector objects
    
    >>> calc_distance(ColorVector((255, 255, 255)), ColorVector((255, 255, 255)))
    0.0
    >>> calc_distance(ColorVector((255, 255, 255)), ColorVector((255, 255, 128)))
    127.0
    >>> calc_distance(ColorVector((255, 255, 255)), ColorVector((255, 0, 255)))
    255.0
    """
    return reduce(hypot, a - b)


def hex_string2colorvector(hex_string):
    r = int(hex_string[:2], 16)
    g = int(hex_string[2:4], 16)
    b = int(hex_string[4:6], 16)
    return ColorVector((r, g, b))


def hex2color_names(hex_string):
    """
    >>> sorted(hex2color_names("FF0000"))[0]
    (0.0, 'red')
    >>> sorted(hex2color_names("faebd7"))[0]
    (0.0, 'antiquewhite')
    >>> sorted(hex2color_names("faebd4"))[0]
    (3.0, 'antiquewhite')
    """
    sourcecolor = hex_string2colorvector(hex_string)
    result = []
    for color_name, colorvector in COLOR_NAMES.iteritems():
        distance = calc_distance(sourcecolor, colorvector)
        result.append((distance, color_name))
    return result


def hex2color_name(hex_string):
    """
    >>> hex2color_name("7b68ee")
    (0.0, 'mediumslateblue')
    >>> hex2color_name("f5f5f5")
    (0.0, 'whitesmoke')
    >>> hex2color_name("f5f3f5")
    (2.0, 'whitesmoke')
    """
    sourcecolor = hex_string2colorvector(hex_string)
    best_distance = 256
    best_name = "unknown"
    for color_name, colorvector in COLOR_NAMES.iteritems():
        distance = calc_distance(sourcecolor, colorvector)
        if distance < best_distance:
            best_distance = distance
            best_name = color_name
            if distance == 0.0:
                break

    return (best_distance, best_name)


#------------------------------------------------------------------------------


CSS_RE2 = re.compile(r'#([a-f0-9]{3,6}) *;', re.IGNORECASE)

def unify_spelling(content):
    """
    unify the 'spelling' of all existing css color values.
    
    >>> unify_spelling("color1: #f00; color2: #Ff0000;")
    ('color1: #ff0000; color2: #ff0000; color3: #aabbcc;', set(['ff0000']))
    
    >>> unify_spelling("color: #aAbBcC  ;")
    ('color: #aabbcc;', set(['aabbcc']))
    """
    existing_values = set()
    def callback(matchobj):
        css_value = matchobj.group(1)
        if len(css_value) == 3:
            # convert 3 length css color values to 6 length
            css_value = css_value[0] + css_value[0] + css_value[1] + css_value[1] + css_value[2] + css_value[2]
        css_value = css_value.lower()

        existing_values.add(css_value)
        return "#%s;" % css_value

    new_content = CSS_RE2.sub(callback, content)
    return new_content, existing_values




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


def unique_color_name(existing_colors, hex_string):
    """   
    >>> unique_color_name((), "ffff00")
    'yellow'
    
    >>> unique_color_name(('yellow',), "ffff00")
    'yellow_2'
    
    >>> unique_color_name((), "0000f5")
    'blue_d10'
    
    >>> unique_color_name(('blue_d10',), "0000f5")
    'blue_d10_2'
    """
    distance, color_name = hex2color_name(hex_string)
    if distance > 5.0:
        # add distance if color values are too different
        color_name += "_d%i" % round(distance)

    if color_name in existing_colors:
        # name exist -> make unique by adding a number
        for no in xrange(2, 1000):
            # get a new color name, witch not exist yet.
            test_name = "%s_%s" % (color_name, no)
            if test_name not in existing_colors:
                color_name = test_name
                break
    return color_name


def convert_3to6_colors(content):
    """
    Convert all 3 length css color values to 6 length
    
    >>> convert_3to6_colors("#f00; #aabbcc;")
    '#ff0000; #aabbcc;'
    """
    new_content = CSS_CONVERT_RE.sub("#\g<1>\g<1>\g<2>\g<2>\g<3>\g<3>;", content)
    return new_content


def findall_color_values(content, case_sensitive=True):
    """
    return all css color values
    
    >>> findall_color_values("#ff0000;")
    set(['ff0000'])
    
    >>> sorted(findall_color_values("#aabbcc; #112233;"))
    ['112233', 'aabbcc']
    
    # If case_sensitive==False: merge different large- and lowercase:
    >>> sorted(findall_color_values("#C9C573; #c9c573;"))
    ['C9C573', 'c9c573']
    >>> findall_color_values("#C9C573; #c9c573;", case_sensitive=False)
    set(['c9c573'])
    
    # Note: Didn't find 3 length color values! Use convert_3to6_colors()
    >>> findall_color_values("#abc;")
    set([])
    """
    colors = set(CSS_RE.findall(content))
    if not case_sensitive:
        colors = set([c.lower() for c in colors])
    return colors



def extract_colors(content, existing_color_dict=None):
    """   
    >>> extract_colors(".foo { color: #000000; }")
    ('.foo { color: {{ black }}; }', {'black': '000000'})
    
    it's case insensitivity:
    >>> extract_colors(".foo{color:#C9C573;} .bar{color:#c9c573;}")
    ('.foo{color:{{ darkkhaki_d20 }};} .bar{color:{{ darkkhaki_d20 }};}', {'darkkhaki_d20': 'c9c573'})
    
    Convert/merge 3 length values:
    >>> extract_colors(".foo{color:#11AAff;} .bar{color:#1af;}")
    ('.foo{color:{{ deepskyblue_d27 }};} .bar{color:{{ deepskyblue_d27 }};}', {'deepskyblue_d27': '11aaff'})
    
    You can give a existing color map:
    >>> extract_colors(".foo { color: #000000; }", existing_color_dict={"black":"000000"})
    ('.foo { color: {{ black }}; }', {'black': '000000'})
    
    Existing color names would not overwritten
    >>> extract_colors(".foo { color: #112233; }", existing_color_dict={"black":"000000"})
    ('.foo { color: {{ darkslategrey_d61 }}; }', {'black': '000000', 'darkslategrey_d61': '112233'})
    
    Existing color names would not overwritten
    >>> extract_colors(".foo { color: #010101; }", existing_color_dict={"black":"000000"})
    ('.foo { color: {{ black_2 }}; }', {'black_2': '010101', 'black': '000000'})
    
    Skip non color values:
    >>> extract_colors("to short #12345; to long #1234567; /* no # 123; color #aa11ff-value */")
    ('to short #12345; to long #1234567; /* no # 123; color #aa11ff-value */', {})
    """
    new_content = convert_3to6_colors(content)

    colors = findall_color_values(new_content)

    if existing_color_dict:
        color_dict = existing_color_dict.copy()
        exist_color = dict([(v, k) for k, v in existing_color_dict.iteritems()])
    else:
        color_dict = {}
        exist_color = {}

    for color in colors:
        color_lower = color.lower()

        if color_lower in exist_color:
            # color exist in other case
            color_name = exist_color[color_lower]
        else:# new color
            color_name = unique_color_name(color_dict, color)

            color_dict[color_name] = color_lower
            exist_color[color_lower] = color_name

        new_content = new_content.replace("#%s" % color, "{{ %s }}" % color_name)

    return new_content, color_dict


def replace_css_name(old_name, new_name, content):
    """
    >>> replace_css_name("old", "new", "color: {{ old }};")
    'color: {{ new }};'
    >>> replace_css_name("foo", "bar", "color: {{   foo   }};")
    'color: {{ bar }};'
    >>> replace_css_name("a", "b", "color: {{a}};")
    'color: {{ b }};'
    """
    return re.sub("\{\{\s*(" + old_name + ")\s*\}\}", "{{ %s }}" % new_name, content)


def get_new_css_names(existing_colors, content):
    """
    >>> get_new_css_names((), "{{ new }}")
    ['new']
    >>> get_new_css_names(("old",), "foo {{ old }} bar {{ new }}!")
    ['new']
    >>> get_new_css_names(("old",), "foo {{  old  }} bar {{  new  }}!")
    ['new']
    >>> get_new_css_names(("old",), "foo {{old}} bar {{new}}!")
    ['new']
    >>> get_new_css_names((), "foo {{ #ffddee }} bar {{new}}!")
    ['new']
    """
    # FIXME: Rexp should not match on colors!
    raw_colors = re.findall("\{\{\s*(.*?)\}\}", content)
    colors = set([color.strip() for color in raw_colors])
    new_colors = [color for color in colors if not color.startswith("#") and not color in existing_colors]
    return new_colors




if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."
