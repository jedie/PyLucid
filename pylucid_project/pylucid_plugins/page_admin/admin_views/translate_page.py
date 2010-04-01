# coding:utf-8

"""
    translate a PageContent.
"""

from django import http
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from pylucid_project.utils.translate import translate
from pylucid_project.apps.pylucid.models import PageTree, PageMeta, PageContent, Language
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup.converter import apply_markup

from page_admin.forms import PageMetaForm, PageContentForm, \
                                                                    LanguageSelectForm



def _select_language(request, context, source_pagemeta):
    """
    choose the translation destination language.
    If one one other language available -> return it directly.
    """
    other_languages = Language.objects.exclude(code=source_pagemeta.language.code)
    if len(other_languages) == 0:
        # should not happend
        request.page_msg.error("Error: There exist only one Language!")
        return http.HttpResponseRedirect(source_pagemeta.get_absolute_url())
    elif len(other_languages) == 1:
        # Only one other language available, so the user must not choose one ;)
        return other_languages[0]
    else:
        # There are more than one other language -> display a form for choose one.
        if "language" in request.GET:
            form = LanguageSelectForm(other_languages, request.GET)
            if form.is_valid():
                lang_code = form.cleaned_data["language"]
                for lang in other_languages:
                    if lang.code == lang_code:
                        return lang
                raise RuntimeError() # should never happen
        else:
            default_lang_entry = Language.objects.get_or_create_default(request)
            form = LanguageSelectForm(other_languages, initial={
                    "language": default_lang_entry.code, # FIXME: Seems not to work
                })
        context.update({
            "title": _("Translate page '%(name)s' (%(desc_lang)s) - Select destination language") % {
                "name": source_pagemeta.name,
                "desc_lang": source_pagemeta.language.description
            },
            "template_name": "page_admin/select_translate_language.html",
            "form": form,
        })
        return context





@check_permissions(superuser_only=False, permissions=(
    "pylucid.add_pagecontent", "pylucid.add_pagemeta",
    "pylucid.change_pagecontent", "pylucid.change_pagemeta",
))
@render_to()
def translate_page(request, pagemeta_id=None):
    if not pagemeta_id:
        raise

    source_pagemeta = PageMeta.objects.get(id=pagemeta_id)
    pagetree = source_pagemeta.pagetree
    source_language = source_pagemeta.language

    is_pluginpage = pagetree.page_type == PageTree.PLUGIN_TYPE
    if is_pluginpage:
        request.page_msg.error("TODO: Translate a plugin page!")
        return http.HttpResponseRedirect(source_pagemeta.get_absolute_url())
    else:
        source_pagecontent = PageContent.objects.get(pagemeta=source_pagemeta)

    context = {
        "abort_url": source_pagemeta.get_absolute_url(),
    }

    # select the destination languare
    result = _select_language(request, context, source_pagemeta)
    if isinstance(result, Language):
        # Language was selected or they exit only one other language
        dest_language = result
    elif isinstance(result, dict):
        # template context returned -> render language select form
        return result
    elif isinstance(result, http.HttpResponse):
        # e.g. error
        return result
    else:
        raise RuntimeError() # Should never happen


    context.update({
        "title": _("Translate page '%(name)s' (%(source_lang)s) into %(dest_lang)s.") % {
            "name": source_pagemeta.name,
            "source_lang": source_pagemeta.language.description,
            "dest_lang": dest_language.description,
        },
        "template_name": "page_admin/translate_page.html",
    })

    try:
        dest_pagemeta = PageMeta.objects.get(pagetree=pagetree, language=dest_language)
    except PageMeta.DoesNotExist:
        dest_pagemeta = None
    else:
        dest_pagecontent = PageContent.objects.get(pagemeta=dest_pagemeta)

    if request.method == "POST":
        source_pagemeta_form = PageMetaForm(
            request.POST, prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            request.POST, prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(request.POST, prefix="dest")
            dest_pagecontent_form = PageContentForm(request.POST, prefix="dest")
        else:
            dest_pagemeta_form = PageMetaForm(
                request.POST, prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                request.POST, prefix=dest_language.code, instance=dest_pagecontent
            )

        if not (source_pagemeta_form.is_valid() and source_pagecontent_form.is_valid() and
                            dest_pagemeta_form.is_valid() and dest_pagecontent_form.is_valid()):
            context["has_errors"] = True
        else:
            context["has_errors"] = False
            if "preview" in request.POST:
                context["source_preview"] = apply_markup(
                    source_pagecontent_form.cleaned_data["content"],
                    source_pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["dest_preview"] = apply_markup(
                    dest_pagecontent_form.cleaned_data["content"],
                    dest_pagecontent_form.cleaned_data["markup"],
                    request.page_msg, escape_django_tags=True
                )
                context["has_errors"] = False
            else: # All forms are valid and it's not a preview -> Save all.
                sid = transaction.savepoint()
                try:
                    source_pagecontent_form.save()
                    source_pagemeta_form.save()

                    # Create new PageMeta entry
                    new_pagemeta = dest_pagemeta_form.save(commit=False)
                    new_pagemeta.pagetree = pagetree
                    new_pagemeta.language = dest_language
                    new_pagemeta.save()

                    # Create new PageContent entry
                    new_pagecontent = dest_pagecontent_form.save(commit=False)
                    new_pagecontent.pagemeta = new_pagemeta
                    new_pagecontent.save()
                except:
                    transaction.savepoint_rollback(sid)
                    raise
                else:
                    transaction.savepoint_commit(sid)
                    if dest_pagemeta is None:
                        request.page_msg("New content %r crerated." % new_pagecontent)
                    else:
                        request.page_msg("All updated.")
                    return http.HttpResponseRedirect(new_pagemeta.get_absolute_url())
    else:
        context["has_errors"] = False
        source_pagemeta_form = PageMetaForm(
            prefix="source", instance=source_pagemeta
        )
        source_pagecontent_form = PageContentForm(
            prefix="source", instance=source_pagecontent
        )
        if dest_pagemeta is None:
            dest_pagemeta_form = PageMetaForm(
                prefix="dest", initial={
                    "robots": source_pagemeta.robots,
                    "permitViewGroup": source_pagemeta.permitViewGroup, # FIXME: Doesn't work
                }
            )
            dest_pagecontent_form = PageContentForm(
                prefix="dest", initial={
                    "markup": source_pagecontent.markup,
                }
            )
        else:
            dest_pagemeta_form = PageMetaForm(
                prefix=dest_language.code, instance=dest_pagemeta
            )
            dest_pagecontent_form = PageContentForm(
                prefix=dest_language.code, instance=dest_pagecontent
            )


        if "prefill" in request.GET:
            filled_fields = []
            if "content" not in dest_pagecontent_form.initial:
                source_content = source_pagecontent_form.initial["content"]
                try:
                    translated_content = translate(
                        source_content, src=source_language.code, to=dest_language.code
                    )
                except ValueError, err:
                    request.page_msg("Can't translate content with google: %s" % err)
                else:
                    dest_pagecontent_form.initial["content"] = translated_content
                    filled_fields.append("content")
                    dest_pagecontent_form.fields['content'].widget.attrs['class'] = 'auto_translated'

            for key, source_value in source_pagemeta_form.initial.iteritems():
                if not source_value \
                    or not isinstance(source_value, basestring)\
                    or key == "robots" \
                    or dest_pagemeta_form.initial.get(key, None):
                    # Skip empty, non string, robots field and if dest. value exist
                    continue

                try:
                    dest_value = translate(
                        source_value, src=source_language.code, to=dest_language.code
                    )
                except ValueError, err:
                    request.page_msg(
                        "Can't translate %(key)s with google: %(err)s" % {"key":key, "err":err}
                    )
                else:
                    dest_pagemeta_form.initial[key] = dest_value
                    filled_fields.append(key)
                    dest_pagemeta_form.fields[key].widget.attrs['class'] = 'auto_translated'

            if filled_fields:
                request.page_msg("These fields are translated via google: %s" % ", ".join(filled_fields))
            else:
                request.page_msg("No fields translated via google.")



    source_pagecontent_form.language = source_language
    dest_pagecontent_form.language = dest_language

    pagemeta_fields = []
    for source_field, dest_field in zip(source_pagemeta_form, dest_pagemeta_form):
        source_field.language = source_language
        pagemeta_fields.append(source_field)
        dest_field.language = dest_language
        pagemeta_fields.append(dest_field)

    context.update({
        "all_forms": [
            source_pagemeta_form, source_pagecontent_form,
            dest_pagemeta_form, dest_pagecontent_form
        ],
        "source_pagemeta_form": source_pagemeta_form,
        "source_pagecontent_form": source_pagecontent_form,
        "dest_pagemeta_form": dest_pagemeta_form,
        "dest_pagecontent_form": dest_pagecontent_form,

        "pagemeta_fields": pagemeta_fields,
    })
    return context


