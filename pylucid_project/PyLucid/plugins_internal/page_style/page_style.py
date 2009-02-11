# -*- coding: utf-8 -*-

"""
    PyLucid stylesheets
    ~~~~~~~~~~~~~~~~~~~

    - Put the css html tag into the cms page.
    - Send the current stylesheet directly to the client.

    Note:
    1. The page_style plugin insert the temporary ADD_DATA_TAG *before* the
        global Stylesheet inserted. So the global Stylesheet can override CSS
        properties from every internal page.
        The ADD_DATA_TAG would be replaced with the collected CSS/JS contents
        in PyLucid.index *after* the page rendered with the django template
        engine.
    2. In CGI environment you should use print_current_style() instead of
        lucidTag! Because the lucidTag insert only the link to the stylesheet.
        Every page request causes a stylesheet request, in addition!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


__version__= "$Rev$"


import sys, os, datetime

from django import forms
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.translation import ugettext as _

from PyLucid.models import Style, Template
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.tools.content_processors import render_string_template


class SwitchForm(forms.Form):
    """
    Select style/template for overwriting.
    """
    style = forms.ModelChoiceField(queryset=Style.objects.all())
    template = forms.ModelChoiceField(queryset=Template.objects.all())



#------------------------------------------------------------------------------
# ToDo: move the "get style/template" stuff out from here...


def tolerant_delete(obj, key):
    """
    Usefull for e.g.:
    tolerant_delete(request.session, "style")
    tolerant_delete(request.session, "template")
    """
    try:
        del obj[key]
    except KeyError:
        pass





class StyleTemplate(object):
    """
    Generic class for getting template/style instance.
    
    1. Use the information in request.session["style" / "template"] and
        get the instance from database.
    2. Get style/template from the current page object
    """
    def __init__(self, request, Model, key):
        self.request = request
        self.Model = Model # PyLucid.models.Style or PyLucid.models.Template
        self.key = key # "style" or "template"

    def get_from_session(self):
        """
        Get style/template instance from database, if the name of it are stored
        in the session.
        """
        item_name = self.request.session.get(self.key, None)
        if not item_name:
            # No override saved in the session data
            return
        
        # Try to get the item from the database
        try:
            instance = self.Model.objects.get(name=item_name)
        except:
            # ToDo: self.Model.DoesNotExist should work here, isn't it?
            tolerant_delete(self.request.session, self.key)
            return
        else:
#            self.request.page_msg(
#                "Info: Use %r as %s" % (instance.name, self.Model.__name__)
#            )
            return instance

    def get(self):
        """
        return the instance
        """
        instance = self.get_from_session()
        if instance:
            return instance
        
        # Get style/template from the current page object
        context = self.request.CONTEXT 
        current_page = context["PAGE"]
        instance = getattr(current_page, self.key)
        return instance


def get_template(request):
    return StyleTemplate(request, Template, "template").get()

def get_style(request):
    return StyleTemplate(request, Style, "style").get()



#------------------------------------------------------------------------------



class page_style(PyLucidBasePlugin):

    def lucidTag(self):
        """
        -Put a link to sendStyle into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet link
        """
        self.response.write(settings.ADD_DATA_TAG)

        current_style = get_style(self.request)

        style_filepath = current_style.get_filepath()
        if os.path.isfile(style_filepath):
            # The stylesheet was stored into a static file
            url = current_style.get_absolute_url()
        else:
            # _command fake-file request
#            self.page_msg("file '%s' not found." % style_filepath)

            style_name = current_style.name
            style_filename = "%s.css" % style_name

            url = self.URLs.methodLink("sendStyle")
            url = url + style_filename

        cssTag = '<link rel="stylesheet" type="text/css" href="%s" />\n' % url
        self.response.write(cssTag)


    def print_current_style(self):
        """
        -Write the stylesheet directly into the page.
        -Insert ADD_DATA_TAG *before* the global Stylesheet content.

        Used with the tag: {% lucidTag page_style.print_current_style %}
        """
        self.response.write(settings.ADD_DATA_TAG)
        
        current_style = get_style(self.request)

        context = {
            "content": current_style.content,
        }
        self._render_template("write_styles", context)#, debug=True)


    def sendStyle(self, css_filename=None):
        """
        send the stylesheet as a file to the client.
        It's the request started with the link tag from self.lucidTag() ;)
        TODO: Should insert some Headers for the browser cache.
        """
        if not css_filename:
            raise Http404(_("Wrong stylesheet url!"))

        css_name = css_filename.rsplit(".",1)[0]

        try:
            style = Style.objects.get(name=css_name)
        except Style.DoesNotExist:
            raise Http404(_("Stylesheet '%s' unknown!") % css_filename)

        content = style.content

        response = HttpResponse()
        response['Content-Type'] = 'text/css; charset=utf-8'
        response.write(content)

        return response


    def switch(self, url_args=None):
        """
        Switch the associated page template/stylesheet and save these info
        into the session data.
        """
        if url_args:
            tolerant_delete(self.request.session, "style")
            tolerant_delete(self.request.session, "template")
            self.page_msg("Delete saved style/template.")
                    
        if self.request.method == 'POST':
            form = SwitchForm(self.request.POST)
            if form.is_valid():
                selected_style = form.cleaned_data['style']
                selected_template = form.cleaned_data['template']
                self.request.session['style'] = selected_style.name
                self.request.session['template'] = selected_template.name
                self.page_msg("Style/Template, saved.")
        else:
            form = SwitchForm({
                "style": self.current_page.style.pk,
                "template": self.current_page.template.pk,
            })
        
        context = {
            "current_page": self.current_page,
            "reset_url": self.URLs.methodLink("switch", "reset"),
            "form": form,
        }
        self._render_template("switch", context)



from PyLucid.system.internal_page import get_internal_page, InternalPageNotFound
def replace_add_data(context, content):
    """
    Replace the temporary inserted "add data" tag, with all collected CSS/JS
    contents, e.g. from the internal pages.
    Note: The tag added in PyLucid.plugins_internal.page_style
    """
    internal_page_content = get_internal_page(context, "page_style", "add_data")

    context = {
        "js_data": context["js_data"],
        "css_data": context["css_data"],
    }
    html = render_string_template(
        internal_page_content, context, autoescape=False
    )

    content = content.replace(settings.ADD_DATA_TAG, html)
    return content