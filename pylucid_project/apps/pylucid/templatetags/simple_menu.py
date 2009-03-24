
from django import template

from pylucid_project.apps.pylucid.models import Page08

register = template.Library()

@register.inclusion_tag('pylucid/simple_menu.html')
def simple_menu():
    pages = Page08.objects.all()
    context = {
        "pages": pages,
    }
    return context

#from django.template import add_to_builtins
#add_to_builtins('PyLucid.template_addons')