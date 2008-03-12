#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= "$Rev:1070 $"

import posixpath

from PyLucid.tools.utils import escape

from django import newforms as forms
from django.newforms.util import ValidationError
from django.db import models
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

from django.conf import settings
from PyLucid.models import Page, Plugin, MARKUPS
from PyLucid.db.page import flat_tree_list, get_sitemap_tree
from PyLucid.db.page_archiv import archive_page
from PyLucid.system.BasePlugin import PyLucidBasePlugin
from PyLucid.system.detect_page import get_default_page_id
from PyLucid.tools.content_processors import apply_markup, \
                                                        render_string_template
from PyLucid.plugins_internal.page_style.page_style import replace_add_data


class ParentChoiceField(forms.IntegerField):
    def clean(self, parent_id):
        """
        returns the parent page instance.
        Note:
            In PyLucid.models.Page.save() it would be checkt if the selected
            parent page is logical valid. Here we check only, if the page with
            the given ID exists.
        """
        # let convert the string into a integer:
        parent_id = super(ParentChoiceField, self).clean(parent_id)
        assert isinstance(parent_id, int)

        if parent_id == 0:
            # assigned to the tree root.
            return None

        try:
            #parent_id = 999999999 # Not exists test
            page = Page.objects.get(id=parent_id)
            return page
        except Exception, msg:
            raise ValidationError(_(u"Wrong parent POST data: %s" % msg))


def get_parent_choices():
    """
    generate a verbose page name tree for the parent choice field.
    """
    page_list = flat_tree_list()
    choices = [(0, "---[root]---")]
    for page in page_list:
        choices.append((page["id"], page["level_name"]))
    return choices

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

    parent = ParentChoiceField(
        widget=forms.Select(choices=get_parent_choices()),
        # FIXME: How to set invalid_choice here?
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


    def _delete_cache(self, page_instance):
        """
        Delete the old page data in the cache, so anonymous users
        see directly the new page content
        """
        shortcut = page_instance.shortcut
        cache_key = settings.PAGE_CACHE_PREFIX + shortcut
        cache.delete(cache_key)

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
            edit_comment = html_form.cleaned_data["edit_comment"]
            # achive the old page data:
            archive_page(self.current_page, edit_comment)
            self.page_msg(_("Old page data archived."))

        # Transfer the form values into the page instance
        for key, value in html_form.cleaned_data.iteritems():
            if key != "edit_comment": # The comment is only for the page archiv
                setattr(page_instance, key, value)

        try:
            page_instance.save()
        except Exception, msg:
            self.page_msg("Can't save the page data:", msg)
            return

        # Delete the old page data cache:
        self._delete_cache(page_instance)

        if page_instance.id == self.current_page.id:
            # Normal page edit
            self.page_msg(_("Page data updated."))
        else:
            self.page_msg(_("The new page created."))

            # refresh the current page data:
            self._refresh_curent_page(page_instance)

            # return the new page content for rendering
            return self.current_page.content


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
            "url_textile_help": self.URLs.methodLink("tinyTextile_help"),
            "url_taglist": self.URLs.methodLink("tag_list"),
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
                "description": page_instance.description
            })
        else: # POST
            #self.page_msg(self.request.POST)
            html_form = EditPageForm(self.request.POST)
            if html_form.is_valid():
                if "preview" in self.request.POST:
                    content = apply_markup(
                        html_form.cleaned_data["content"], self.context,
                        html_form.cleaned_data["markup"]
                    )
                    # Render possibly existing django tags:
                    # ToDo: Should we add a "disable" switch to this?
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
        # The default page can't delete:
        default_page_id = get_default_page_id()
        if id == default_page_id:
            msg = _(
                    "Can't delete the page with ID:%s,"
                    " because this is the default page!"
            ) % id
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

        if id == self.current_page.id:
            # The current page was deleted, so we must go to a other page.
            # The easyest way, if to go to the default page ;)
            self.current_page.id = default_page_id
            self.current_page = Page.objects.get(id=default_page_id)


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


    def _get_html(self, sitemap_tree, default_page_id):
        """
        generate from the sitemap_tree a "checkbox-list" for the delete
        page html form dialog.
        The default page and pages with sub pages would get no checkbox.
        """
        result = ["<ul>\n"]
        for entry in sitemap_tree:
            result.append('<li>')

            if entry["id"]==default_page_id:
                html = (
                    '<span title="Can not delete this pages,'
                    ' because it the default page.">%(name)s</span>'
                )
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
                    self._get_html(entry["subitems"], default_page_id)
                )

            result.append('</li>\n')

        result.append("</ul>\n")
        return "".join(result)


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

        # The default page can't delete, so we need the ID of these page:
        default_page_id = get_default_page_id()

        # Generate the HTML form code:
        html = self._get_html(page_tree, default_page_id)
        html = mark_safe(html) # turn djngo auto-escaping off

        # Render the Template:
        context = {
            "html_data": html,
        }
        self._render_template("delete_pages", context)

    #___________________________________________________________________________

    def tinyTextile_help(self):
        """
        Render the tinyTextile Help page.
        """
        context = {
            "add_data_tag": mark_safe(settings.ADD_DATA_TAG)
        }
        content = self._get_rendered_template("tinyTextile_help", context)
        # insert CSS data from the internal page into the rendered page:
        content = replace_add_data(self.context, content)
        return HttpResponse(content)

    #___________________________________________________________________________

    def tag_list(self):
        """
        Render a help page with a list of all available django template tags
        and all available lucidTag's (List of all available plugins).

        TODO: Find a way to put the tag parameter syntax into the plugin_list:
            e.g. without..: {{ lucidTag page_update_list }}
            e.g. with.....: {{ lucidTag page_update_list count=10 }}
            idea: Import the plugin class and use inspect?
        """

        def get_plugin_list():
            """
            Generate a list of all Plugins how are active.
            """
            plugin_list = Plugin.objects.values(
                "id", "plugin_name", "version", "author", "url", "description",
                "long_description",
            ).order_by('package_name')
            plugin_list = plugin_list.filter(active = True)
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



