# coding:utf-8

from django import forms, http
from django.db import transaction
from django.core import urlresolvers
from django.template import RequestContext
from django.contrib.sites.models import Site
from django.shortcuts import render_to_response
from django.contrib.auth.models import User, Group
from django.utils.translation import ugettext_lazy as _

from pylucid.models import PageTree, PageMeta, PageContent, PyLucidAdminPage, Design, Language
from pylucid.preference_forms import SystemPreferencesForm

from pylucid_admin.admin_menu import AdminMenu



def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("create content")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new content page", title="Create a new content page.",
        url_name="PageAdmin-new_content_page"
    )
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="new plugin page", title="Create a new plugin page.",
        url_name="PageAdmin-new_plugin_page"
    )

    return "\n".join(output)


#class PageTreeForm(forms.ModelForm):
#    class Meta:
#        model = PageTree
#        exclude = ("site",)
#
#class PageContentForm(forms.ModelForm):
#    class Meta:
#        model = PageContent
#        exclude = ("page", "pagemeta")
#
#class PageMetaForm(forms.ModelForm):
#    class Meta:
#        model = PageMeta
#        exclude = ("page", "lang")
#
#class PageForm(PageTreeForm, PageContentForm, PageMetaForm):
#    pass

class PageContentForm(forms.Form):
    """
    Form vor creating a new content page.
    TODO: Find a DRY way to get the fields directly from the PageTree, PageContent and PageMeta models.
    """
    parent = forms.ModelChoiceField(queryset=PageTree.objects.all(), label=_('Parent'), initial=None, help_text=_('the higher-ranking father page'), required=False)
    position = forms.IntegerField(label=_('Position'), initial=0, help_text=_('ordering weight for sorting the pages in the menu.'))
    slug = forms.SlugField(label=_('Slug'), initial=None, help_text=_('(for building URLs)'))
    design = forms.ModelChoiceField(queryset=Design.objects.all(), label=_('Design'), initial=None, help_text=_('Page Template, CSS/JS files'))
    showlinks = forms.BooleanField(label=_('Showlinks'), initial=True, help_text=_('Put the Link to this page into Menu/Sitemap etc.?'), required=False)
    permitViewGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitViewGroup'), initial=None, help_text=_('Limit viewable to a group?'), required=False)
    permitEditGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitEditGroup'), initial=None, help_text=_('Usergroup how can edit this page.'), required=False)

    lang = forms.ModelChoiceField(queryset=Language.objects.all(), label=_('Language'), initial=None)

    content = forms.CharField(label=_('Content'), initial=None, help_text=_('The CMS page content.'), required=False)
    markup = forms.TypedChoiceField(choices=PageContent.MARKUP_CHOICES, label=_('Markup'), initial=None)

    name = forms.CharField(label=_('Name'), initial=None, help_text=_('Sort page name (for link text in e.g. menu)'), required=False)
    title = forms.CharField(label=_('Title'), initial=None, help_text=_('A long page title (for e.g. page title or link title text)'), required=False)
    keywords = forms.CharField(label=_('Keywords'), initial=None, help_text=_('Keywords for the html header. (separated by commas)'), required=False)
    description = forms.CharField(label=_('Description'), initial=None, help_text=_('For html header'), required=False)
    robots = forms.CharField(label=_('Robots'), initial='index,follow', help_text=_("for html 'robots' meta content."))
    permitViewGroup = forms.ModelChoiceField(queryset=Group.objects.all(), label=_('PermitViewGroup'), initial=None, help_text=_('Limit viewable to a group?'), required=False)




def new_content_page(request):
    """
    can use django.forms.models.inlineformset_factory:
        PageFormSet = inlineformset_factory(PageTree, PageContent, PageMeta)
    get:
        metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of
        the metaclasses of all its bases
    see also: http://code.djangoproject.com/ticket/7837
    """
    def make_kwargs(data, keys):
        kwargs = {}
        for key in keys:
            kwargs[key] = data[key]
        return kwargs

    formset = []
    if request.method == "POST":
        form = PageContentForm(request.POST)
        if form.is_valid():
            sid = transaction.savepoint()
            try:
                pagetree_kwargs = make_kwargs(
                    form.cleaned_data, keys=(
                        "parent", "position", "slug", "design", "showlinks",
                        "permitViewGroup", "permitEditGroup"
                    )
                )
                pagetree_kwargs["type"] = PageTree.PAGE_TYPE
                pagetree_instance = PageTree(**pagetree_kwargs)
                pagetree_instance.save()

                pagemeta_kwargs = make_kwargs(
                    form.cleaned_data,
                    keys=("lang", "name", "title", "keywords", "description", "robots", "permitViewGroup")
                )
                pagemeta_kwargs["page"] = pagetree_instance
                pagemeta_instance = PageMeta(**pagemeta_kwargs)
                pagemeta_instance.save()

                pagecontent_kwargs = make_kwargs(form.cleaned_data, keys=("lang", "content", "markup"))
                pagecontent_kwargs["page"] = pagetree_instance
                pagecontent_kwargs["pagemeta"] = pagemeta_instance
                pagecontent_instance = PageContent(**pagecontent_kwargs)
                pagecontent_instance.save()
            except:# IntegrityError, e:
                transaction.savepoint_rollback(sid)
                raise
            else:
                transaction.savepoint_commit(sid)
                request.page_msg("New page %r created." % pagecontent_instance)
                return http.HttpResponseRedirect(pagecontent_instance.get_absolute_url())
    else:
        form = PageContentForm()

    context = {
        "title": "Create a new page",
        "form_url": request.path,
        "form": form,
    }
    return render_to_response('page_admin/new_content_page.html', context,
        context_instance=RequestContext(request)
    )

def new_plugin_page(request):
    context = {
        "title": "Create a new plugin page",
        "content": "TODO",
    }
    return render_to_response('admin/base_site.html', context,
        context_instance=RequestContext(request)
    )
