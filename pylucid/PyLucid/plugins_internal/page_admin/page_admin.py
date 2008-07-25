# -*- coding: utf-8 -*-

"""
    PyLucid plugin
    ~~~~~~~~~

    CMS page administration (edit, delete, make a new page etc.)

    TODO: With django autoescape we need no longer a escape hack here.
    But the row should be increased here.
    Idea: Create a normal newforms class for the page edit.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate:2007-06-18 16:07:16 +0200 (Mo, 18 Jun 2007) $
    $Rev:1070 $
    $Author:JensDiemer $

    :copyleft: 2007 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:1070 $"

import posixpath
import inspect

from PyLucid.tools.utils import escape, escape_django_tags

from django import forms
from django.forms import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from django.conf import settings
from PyLucid.models import Page, Plugin, MARKUPS
from PyLucid.db.page import flat_tree_list, get_sitemap_tree
from PyLucid.db.page_archiv import archive_page
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.plugin_import import get_plugin_module
from PyLucid.tools.content_processors import apply_markup, \
                                                        render_string_template
from PyLucid.plugins_internal.page_style.page_style import replace_add_data

from PyLucid.db.page import PageChoiceField, get_page_choices, flat_tree_list




# Keys must be correspond with PyLucid.models.MARKUPS
HELP_INFO = {
    2: u'markup_help_tinyTextile',
    6: u'markup_help_creole',
}


class EditPageForm(forms.Form):
    """
    Form for editing a cms page.
    """
    edit_comment = forms.CharField(
        max_length=255, required=False,
        help_text=_("The reason for editing."),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )

    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': '15'}),
    )

    parent = PageChoiceField(
        help_text="the higher-ranking father page",
    )

    name = forms.CharField(
        max_length=255, help_text=_("A short page name"),
    )
    title = forms.CharField(
        max_length=255, required=False, help_text=_("A long page title"),
    )
    markup = forms.IntegerField(
        widget=forms.Select(choices=MARKUPS),
        help_text=_("the used markup language for this page"),
    )

    keywords = forms.CharField(
        max_length=255, required=False,
        help_text=_("Keywords for the html header. (separated by commas)"),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )
    description = forms.CharField(
        max_length=255, required=False,
        help_text=_("Short description of the contents. (for the html header)"),
        widget=forms.TextInput(attrs={'class':'bigger'}),
    )

    preview_escape = forms.BooleanField(
        required=False,
        help_text=_("Escape django template tags in preview?"),
    )
    def __init__(self, *args, **kwargs):
        super(EditPageForm, self).__init__(*args, **kwargs)
        # FIXME: How to set invalid_choice here?
        self.fields["parent"].widget=forms.Select(choices=get_page_choices())


#______________________________________________________________________________

class SelectEditPageForm(forms.Form):
    page_id = forms.IntegerField()

#______________________________________________________________________________

class page_admin(PyLucidBasePlugin):

    def _get_edit_page(self, edit_page_id, new_page_instance):
        """
        returned the right id and instance for the edit form.
        """
        if new_page_instance != None:
            # Edit a new page, the skeleton is given from self.new_page()
            edit_page_id = self.current_page.id
            page_instance = new_page_instance

        elif edit_page_id != None:
            # Edit the page with the given ID. ("select page to edit" function)
            try:
                edit_page_id = int(edit_page_id.strip("/"))
                #edit_page_id = 9999 # Test a wrong ID from the POST data
                page_instance = Page.objects.get(id=edit_page_id)
            except Page.DoesNotExist, msg:
                raise Page.DoesNotExist(_("Wrong page ID! (%s)") % msg)

        else:
            # No ID or instance given
            # The "edit page" link was used -> Edit the current cms page
            edit_page_id  = self.current_page.id
            page_instance = self.current_page

        page_instance.lastupdateby = self.request.user

        return edit_page_id, page_instance

    def _refresh_curent_page(self, page_instance):
        """
        If a new page created, PyLucid should display this new page
        and e.g. the URLs should used the new current page id. So here we
        update the global current page object.
        """
        self.current_page.id = page_instance.id
        self.current_page = page_instance
        self.context["PAGE"] = page_instance

    def _save_edited_page(self, page_instance, html_form):
        """
        Save a edited page into the database.

        if a old page was edited:
            -Archive the old page data
        if a new page was created:
            -return the new page content for rendering
        """
        if page_instance.id == self.current_page.id:
            # A existing page was edited
            edit_comment = html_form.cleaned_data.pop("edit_comment")
            # achive the old page data:
            archive_page(self.current_page, edit_comment)
            self.page_msg(_("Old page data archived."))

        # Assign parent page
        parent_page_id = html_form.cleaned_data.pop("parent")
        if parent_page_id != None:
            parent = Page.objects.get(id=parent_page_id)
            page_instance.parent = parent
        else:
            page_instance.parent = None

        # Transfer the form values into the page instance
        for key, value in html_form.cleaned_data.iteritems():
            setattr(page_instance, key, value)

        try:
            page_instance.save()
        except Exception, msg:
            if self.request.debug:
                raise
            self.page_msg("Can't save the page data:", msg)
            return

        if page_instance.id == self.current_page.id:
            # Normal page edit
            self.page_msg(_("Page data updated."))
        else:
            self.page_msg(_("The new page created."))

            # refresh the current page data:
            self._refresh_curent_page(page_instance)


    def edit_page(self, edit_page_id=None, new_page_instance=None):
        """
        Edit a cms page.
            - Display the html form for inline editing.
            - Save the new page data, sent by POST.

        Used for:
            - The admin menu "edit page" link.
            - The "select page to edit" function. (self.select_edit_page)
            - The admin menu "new page" link. (self.new_page)
        """
        try:
            edit_page_id, page_instance = self._get_edit_page(
                edit_page_id, new_page_instance
            )
        except Page.DoesNotExist, msg:
            # The page ID from the "select page to edit" POST data is wrong.
            self.page_msg.red(msg)
            return

        context = {
            "url_taglist": self.URLs.methodLink("tag_list"),
            "url_pagelinklist": self.URLs.methodLink("page_link_list"),
            "page_instance": page_instance,
        }

        # The markup is a little dynamicly. It should always be used the current
        # markup editor (html with or without TinyMCE) e.g. The user change the
        # markup and used the "preview" fuction.
        current_markup = page_instance.markup

        if self.request.method != 'POST':
            parent = getattr(page_instance.parent, "id", 0) # Root is None

            html_form = EditPageForm({
                "content": page_instance.content,
                "parent": parent,
                "name": page_instance.name,
                "title": page_instance.title,
                "markup": current_markup,
                "keywords": page_instance.keywords,
                "description": page_instance.description,
                "preview_escape": True,
            })
        else: # POST
            #self.page_msg(dict(self.request.POST))
            html_form = EditPageForm(self.request.POST)
            if html_form.is_valid():
                if "preview" in self.request.POST:
                    cleaned_data = html_form.cleaned_data
                    content = apply_markup(
                        cleaned_data["content"], self.context,
                        cleaned_data["markup"]
                    )

                    preview_escape = cleaned_data["preview_escape"]
                    if preview_escape == True:
                        # escape django template tags for preview
                        content = escape_django_tags(content)

                    content = render_string_template(content, self.context)
                    context["preview_content"] = content

                    # Use the current selected markup
                    current_markup = html_form.cleaned_data["markup"]

                elif "save" in self.request.POST:
                    # Save the new page data. returns a new page instance
                    return self._save_edited_page(page_instance, html_form)
                else:
                    self.page_msg.red("Form error!")

        context["edit_page_form"] = html_form

        # Edit in the django admin panel:#
        if new_page_instance != None:
            # If the page is new:
            url_django_edit = self.URLs.adminLink("PyLucid/page/add/")
        else:
            url_django_edit = self.URLs.adminLink(
                "PyLucid/page/%s/" % edit_page_id
            )
        context["url_django_edit"] = url_django_edit

        # On abort -> goto the current displayed page:
        url_abort = self.current_page.get_absolute_url()
        context["url_abort"] = url_abort

        if current_markup in HELP_INFO:
            context["help_link"] = self.URLs.methodLink(
                "markup_help", current_markup
            )
            # TODO: make help link working
            #self.page_msg("help_link:", context["help_link"])

        if current_markup == 1:
            # markup with id=1 is html + TinyMCE JS Editor
            context["use_tinymce"] = True

            # url to e.g. /media/PyLucid/tiny_mce/tiny_mce.js
            tiny_mce_url = posixpath.join(
                self.URLs["PyLucid_media_url"], "tiny_mce", "tiny_mce.js"
            )
            # url to e.g. .../internal_page/page_admin/edit_page_tinymce.js
            use_tiny_mce_url = self.internal_page.get_url(
                "edit_page_tinymce", slug="js"
            )
            # Add external media files
            for url in (tiny_mce_url, use_tiny_mce_url):
                # Add tiny_mce.js to
                self.context["js_data"].append({
                    "plugin_name": self.plugin_name,
                    "url": url,
                })

        self._render_template("edit_page", context)#, debug=True)

    def select_edit_page(self):
        """
        A html select box for editing a cms page.
        If the form was sended, return a redirect to the edit_page method.
        """
        if self.request.method == 'POST':
            form = SelectEditPageForm(self.request.POST)
            if form.is_valid():
                form_data = form.cleaned_data
                page_id = form_data["page_id"]
                new_url = self.URLs.commandLink(
                    "page_admin", "edit_page", page_id
                )
#                self.page_msg(new_url)
                return HttpResponseRedirect(new_url)

        page_list = flat_tree_list()

        context = {
            "page_list": page_list,
        }
        self._render_template("select_edit_page", context)

    #___________________________________________________________________________

    def new_page(self):
        """
        make a new CMS page.
        Create a new page instance skeleton.
        Inherit some things from the current page.
        """
        parent = self.current_page
        # make a new page skeleton object:
        new_page = Page(
            name             = "New page",
            shortcut         = "NewPage",
            content          = "New page.",
            template         = parent.template,
            style            = parent.style,
            markup           = parent.markup,
            createby         = self.request.user,
            lastupdateby     = self.request.user,
            showlinks        = parent.showlinks,
            permitViewPublic = parent.permitViewPublic,
            permitViewGroup  = parent.permitViewGroup,
            permitEditGroup  = parent.permitEditGroup,
            parent           = parent,
        )
        # Display the normal edit page dialog for the new cms page.
        # After the html form sended via POST, the new page created in the
        # database and PyLucid should render this new page and not the old
        # current page. So here we retuned the new page content
        return self.edit_page(new_page_instance=new_page)

    #___________________________________________________________________________

    def _delete_page(self, id):
        """
        Delete one page with the given >id<.
        Error, if...
        ...this is the default page.
        ...this page has sub pages.
        """
        skip_data = self.get_delete_skip_data()
        # The skip_data contains the default- and the current page.
        if id in skip_data:
            msg = _(
                    "Can't delete the page with ID:%(id)s,"
                    " because %(reason)s!"
            ) % {"id":id, "reason":skip_data[id]}
            raise DeletePageError(msg)

        # Check if the page has subpages
        sub_pages_count = Page.objects.filter(parent=id).count()
        if sub_pages_count != 0:
            msg = _(
                    "Can't delete the page with ID:%s,"
                    " because it has %s sub pages!"
            ) % (id, sub_pages_count)
            raise DeletePageError(msg)

        # Delete the page:
        try:
            page = Page.objects.get(id=id)
            page.delete()
        except Exception, msg:
            msg = _("Can't delete the page with ID:%s: %s") % (
                id, escape(str(msg))
            )
            raise DeletePageError(msg)
        else:
            self.page_msg(_("Page with id: %s delete successful.") % id)


    def _process_delete_pages(self):
        """
        process a sended "delete pages" dialog.
        """
        if self.request.method != 'POST':
            # No form sended via POST
            return

        # create a list of the sended page IDs:
        id_list = self.request.POST.getlist("pages")
        try:
            # Convert the string list to a interger list
            id_list = [int(i) for i in id_list]
        except ValueError, msg:
            self.page_msg.red(_("Wrong data: %s") % escape(str(msg)))
            return

        # delete the pages, one by one:
        for id in id_list:
            try:
                self._delete_page(id)
            except DeletePageError, msg:
                self.page_msg.red(msg)


    def _get_html(self, sitemap_tree, skip_data):
        """
        generate from the sitemap_tree a "checkbox-list" for the delete
        page html form dialog.
        The default page and pages with sub pages would get no checkbox.
        """
        result = ["<ul>\n"]
        for entry in sitemap_tree:
            result.append('<li>')

            if entry["id"] in skip_data:
                html = (
                    '<span title="Can not delete this pages,'
                    ' because: %s">%%(name)s</span>'
                ) % skip_data[entry["id"]]
            elif "subitems" in entry:
                html = (
                    '<span title="Can not delete this pages,'
                    ' because it has sub pages.">%(name)s</span>'
                )
            else:
                html = (
                    '<input name="pages" value="%(id)s"'
                    ' id="del_page_%(id)s" type="checkbox"'
                    ' title="delete page: %(name)s" />'
                    ' <label for="del_page_%(id)s">%(name)s</label>'
                )

            result.append(html % entry)
#            result.append(' <small>(id: %s)</small>' % entry["id"])

            if "subitems" in entry:
                result.append(
                    self._get_html(entry["subitems"], skip_data)
                )

            result.append('</li>\n')

        result.append("</ul>\n")
        return "".join(result)


    def get_delete_skip_data(self):
        """
        returns a dict with default- and the current page id and why they can't
        delete.
        """
        skip_data = {}
        skip_data[self.current_page.id] = _(
            "It's the current page."
            " Please goto a other page and start deleting again"
        )

        # The default page can't delete, so we need the ID of the default page:
        default_page = Page.objects.default_page
        skip_data["default_page.id"] = _("It's the default page.")

        return skip_data


    def delete_pages(self):
        """
        Render the delete page html form dialog.
        A sended html form would be
        TODO: We should only display one page level (like sequencing do).
        """
        # Process a sended POST formular:
        self._process_delete_pages()

        # Get the needed data for build the html form:
        page_tree = get_sitemap_tree(self.request)

        # The skip_data contains the default- and the current page.
        skip_data = self.get_delete_skip_data()

        # Generate the HTML form code:
        html = self._get_html(page_tree, skip_data)
        html = mark_safe(html) # turn djngo auto-escaping off

        # Render the Template:
        context = {
            "html_data": html,
        }
        self._render_template("delete_pages", context)

    #___________________________________________________________________________

    def markup_help(self, url_args):
        """
        Render help page for the markup
        Render the tinyTextile Help page.
        """
        try:
            markup_id = int(url_args.strip("/"))
            internal_page_name = HELP_INFO[markup_id]
        except Exception, e:
            if self.request.debug:
                raise
            else:
                self.page_msg("URL error.")
                return

        context = {
            "add_data_tag": mark_safe(settings.ADD_DATA_TAG)
        }

        if markup_id == 6: # Creole wiki markup
            sheet_url = self.internal_page.get_url(
                internal_page_name = "creole_cheat_sheet",
                slug = "png"
            )
            if not sheet_url:
                self.page_msg.red("creole_cheat_sheet.png not found!")
            context["sheet_url"] = sheet_url

        #self.page_msg(markup_id, internal_page_name, context)

        content = self._get_rendered_template(internal_page_name, context)

        if markup_id == 2: # textile
            # Use tinyTextile markup
            content = apply_markup(content, self.context, markup_id)

        # insert CSS data from the internal page into the rendered page:
        content = replace_add_data(self.context, content)
        return HttpResponse(content)

    #___________________________________________________________________________

    def tag_list(self):
        """
        Render a help page with a list of all available django template tags
        and all available lucidTag's (List of all available plugins which
        provide lucidTag method).
        """
        def _get_method_syntax(method):
            """
            returns the argument string for the given method.
            e.g.: url="" debug="None"
            """
            (args, varargs, varkw, defaults) = inspect.getargspec(method)
            argmap = dict.fromkeys(args[1:],None)
            if defaults:
                argmap.update(zip(args[-len(defaults):], map(repr,defaults)))
            stx = []
            for arg in args[1:]:
                if argmap[arg]:
                    stx.append('%s="%s"' % (arg,argmap[arg]))
                else:
                    stx.append('%s=""' % arg)
            return " ".join(stx)

        def get_plugin_list():
            """
            Generate a list of all Plugins which are active.
            """
            plugins = Plugin.objects.filter(active=True).all()

            plugin_list = []
            for plugin in plugins:
                try:
                    plugin_methods = plugin.get_all_methods()
                except Exception, err:
                    self.page_msg.red(
                        "Error getting plugin class %s.%s: %s" % (
                            plugin.package_name, plugin.plugin_name, err
                        )
                    )
                    continue

                for method in plugin_methods:
                    if method[0] == "lucidTag":
                        plugin_list.append({
                            'plugin_name': plugin.plugin_name,
                            'arguments': _get_method_syntax(method[1]),
                            'description': plugin.description
                        })

            return plugin_list

        def get_page_fields():
            """
            Generate a list of all PyLucid.models.Page fields.
            """
            page_fields = []
            opts = self.current_page._meta
            for field in opts.fields:
                page_fields.append({
                    "name": field.name,
                    "help_text": field.help_text
                })
            return page_fields

        # TODO: insert the extra context fields
        # e.g. from PyLucid.system.context_processors

        context = {
            "plugin_list": get_plugin_list(),
            "page_fields": get_page_fields(),
            "add_data_tag": mark_safe(settings.ADD_DATA_TAG)
        }
        content = self._get_rendered_template("tag_list", context)
        # insert CSS data from the internal page into the rendered page:
        content = replace_add_data(self.context, content)
        return HttpResponse(content)

    #___________________________________________________________________________

    def page_link_list(self):

        page_list = flat_tree_list()

        context = {
            "page_list": page_list,
            "prefix": settings.PERMALINK_URL_PREFIX,
            "add_data_tag": mark_safe(settings.ADD_DATA_TAG)
        }
        content = self._get_rendered_template("page_link_list", context)
        # insert CSS data from the internal page into the rendered page:
        content = replace_add_data(self.context, content)
        return HttpResponse(content)

    #___________________________________________________________________________

    def _save_sequencing(self, page_data):
        """
        Save the new position weight for every pages, if changed.
        """
        no_changes = True
        for page in page_data:
            try:
                page_id = str(page.id)
                #page_id = "Not exists test"
                weight = self.request.POST[page_id]
                #weight = "Not a number test"
                weight = int(weight)
            except (KeyError, ValueError), msg:
                self.page_msg.red(_("Error: Wrong POST data!"))
                if self.request.debug:
                    self.page_msg.red("Debug: %s" % msg)
                # abort!
                return

            if page.position == weight:
                # No change needed for this page
                continue

            # Set new position weight and save:
            page.position = weight
            page.save()

            no_changes = False
            self.page_msg.green(
                _("Set position weight %s for page '%s', ok.") % (
                    weight, page.name
                )
            )

        if no_changes:
            # Give feedback for the user, if nothing to do...
            self.page_msg.green(_("Nothing to change ;)"))


    def _get_sequence_data(self, url_args):
        """
        returned the pages and the "use"-mode.
        Based on the url, the pages are from the "parent", "current", "child"
        level.
        """
        # Start with "current" level. Only if the url starts with "parent" or
        # "child" change the level.
        use = "current"
        if url_args != None:
            if url_args.startswith("parent"):
                use = "parent"
                parent_page = Page.objects.get(
                    id=self.current_page.parent.id
                )
                parent_filter = parent_page.parent
            elif url_args.startswith("child"):
                use = "child"
                parent_filter = self.current_page.id

        if use == "current":
            # "url_args == None" or the url is not well-formed: It doesn't
            # starts with "parent" or "child"
            parent_filter = self.current_page.parent

        # Change a "parent__exact=None" query to "parent__isnull=True"
        # see: http://www.djangoproject.com/documentation/db-api/#isnull
        if parent_filter == None:
            filter_kwargs = {"parent__isnull": True}
        else:
            filter_kwargs = {"parent": parent_filter}

        page_data = Page.objects.filter(**filter_kwargs)

        return use, page_data


    def sequencing(self, url_args=None):
        """
        Set the position weight of the cms page to change the correct order.
        TODO: Save the weight range in the preferences
        """
        use, page_data = self._get_sequence_data(url_args)

        if self.request.method == 'POST':
            # Save new position weight
            self._save_sequencing(page_data)

        # Order the pages *after* a sended POST data processed.
        page_data = page_data.order_by("position")

        childs = Page.objects.filter(parent=self.current_page.id).count()
        has_childs = childs != 0

        parents = Page.objects.filter(parent=self.current_page.parent).count()
        has_parents = parents != 0

#        self.page_msg("url_args:", url_args)
#        self.page_msg("use:", use)
#        self.page_msg("filter_kwargs:", filter_kwargs)
#        self.page_msg("has_childs:", has_childs, " - has_parents:", has_parents)

        context = {
            "sequencing_data": page_data,
            "weights": range(-10, 10),

            "base_url": self.URLs.methodLink("sequencing"),

            "has_childs": has_childs,
            "has_parents": has_parents,
        }
        context["use_%s" % use] = True

        self._render_template("sequencing", context)#, debug=True)


class DeletePageError(Exception):
    """
    Error while deleting one cms page.
    """
    pass



