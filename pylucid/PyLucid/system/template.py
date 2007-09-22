
from PyLucid.models import Page, Template

def get_template_obj(response, current_page):
    assert isinstance(current_page, Page)
    template_id = current_page.template
    return Template.objects.get(id__exact=template_id)

def get_template_content(response, current_page):
    assert isinstance(current_page, Page)
    template = get_template_obj(response, current_page)
    return template.content