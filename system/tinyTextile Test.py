import re

txt = """
Text !/MeinBild.jpg! Text
"""

print txt
print "="*80

print re.sub(
    r'\!(.+?)\!(?uis)',
    r'<img src="\1">',
    txt
    )
print "-"*80
#~ txt = " "+txt # Hiermit geht's...
#~ print re.sub(
    #~ r"""
        #~ ([^:])
        #~ (http|ftp)://(\S+)
        #~ (?uimx)""",
    #~ r'\1<a href="\2://\3">\2://\3</a>',
    #~ txt
    #~ )