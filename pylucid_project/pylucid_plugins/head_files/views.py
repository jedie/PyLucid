# coding: utf-8

"""
    TODO: Should be better make this in a middleware???
        So plugins can add own files, like the SHA1auth plugin and his SHA1.js file??? 
"""

from django.http import HttpResponse

def lucidTag(request):
    """
    Generate all html head file links 
    """
    pagetree = request.PYLUCID.pagetree
    design = pagetree.design
    
    headfiles = design.headfiles.all()
    
    head_links = []
    for headfile in headfiles:
        head_link = headfile.get_head_link()
        head_links.append(head_link)
    
    result = "\n".join(head_links)
    return HttpResponse(result)