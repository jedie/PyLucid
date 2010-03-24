# coding: utf-8

from django import http
from django.conf import settings
from django.db import transaction
from django.forms.models import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from page_admin.forms import MassesEditorSelectForm

@render_to("page_admin/bulk_editor.html")
@check_permissions(superuser_only=True)
def bulk_editor(request):
    """ Edit one attribute for all model items at once. """
    title = "Bulk Editor"
    context = {
        "form_url": request.path,
        "abort_url": request.path,
    }
    if request.method == 'POST': # Stage 1: MassesEditorSelectForm was send
        #request.page_msg(request.POST)
        form = MassesEditorSelectForm(request.POST)
        if form.is_valid():
            #request.page_msg(form.cleaned_data)
            model_attr = form.cleaned_data["model_attr"]
            model, filter_lang, attr = model_attr
            language = form.cleaned_data["language"]

            queryset = model.on_site.all()

            # We can't use .only() here. Otherwise a tagging TagField() would not updated correctly
            # See also: http://www.python-forum.de/post-154432.html#154432 (de)
            #queryset = queryset.only(attr)

            if filter_lang:
                queryset = queryset.filter(language=language)

            ModelFormset = modelformset_factory(model=model, extra=0, fields=(attr,))

            if "form-TOTAL_FORMS" in request.POST: # Stage 2: The ModelFormset POST data exist
                formset = ModelFormset(request.POST, queryset=queryset)
                if formset.is_valid():
                    sid = transaction.savepoint()
                    try:
                        instances = formset.save(commit=False)
                        formset.save_m2m()
                        formset.save()
                    except:
                        transaction.savepoint_rollback(sid)
                        raise
                    else:
                        transaction.savepoint_commit(sid)

                    if not instances:
                        request.page_msg(_("No items changed."))
                    else:
                        try:
                            id_list = ", ".join([str(int(item.pk)) for item in instances])
                        except ValueError: # No number as primary key?
                            id_list = ", ".join([repr(item.pk) for item in instances])

                        request.page_msg(_("%(count)s items saved (IDs: %(ids)s)") % {
                            "count": len(instances), "ids": id_list
                        })
                        if settings.DEBUG:
                            request.page_msg("Debug saved items:")
                            for instance in instances:
                                request.page_msg(instance.get_absolute_url(), instance)
                                #request.page_msg("saved value: %r" % getattr(instance, attr))

                    return http.HttpResponseRedirect(request.path)
            else:
                formset = ModelFormset(queryset=queryset)

            context["formset"] = formset
            context["model_name"] = model.__name__
            context["attr"] = attr
            context["filter_lang"] = filter_lang
            context["language"] = language
            title += " - %s.%s (%s)" % (model.__name__, attr, language)

            # Change all field label to the absolute url
            for formset_form in formset.forms:
                instance = formset_form.instance
                absolute_url = instance.get_absolute_url()
                for field_name, field in formset_form.fields.iteritems():
                    field.label = absolute_url

            # Sort by absolute_url, used the label value from the first field 
            formset.forms.sort(
                cmp=lambda x, y: cmp(x.fields.values()[0].label.lower(), y.fields.values()[0].label.lower())
            )

            # Hide the MassesEditorSelectForm fields. They should not changed, yet.
            form.hide_all_fields()
    else:
        form = MassesEditorSelectForm()

    context["form"] = form
    context["title"] = title
    return context
