# coding: utf-8

"""
    PyLucid blog forms
    ~~~~~~~~~~~~~~~~~~

    Forms for the blog.

    :copyleft: 2008-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from pylucid_project.apps.pylucid.forms.utils import TagLanguageSitesFilter

from pylucid_project.pylucid_plugins.blog.models import BlogEntryContent


class BlogContentForm(TagLanguageSitesFilter, forms.ModelForm):
    """
    Like a normal model form. But it protects against overwriting newer content:
    * Save the last update time in a hidden field
    * Check if the current last update time is newer
    * Add a checkbox for overwrite newer changes

    Example:
    Last edit was at 12:00
    User A starts editing (hidden field == 12:00)
    User B starts editing (hidden field == 12:00)
    User B saves at 12:02 -> new last edit time is now 12:02
    User A saves later than User B:
        * In his form was save the last edit at 12:00, but now the instance
          has the last edit time 12:02
        * User A get the form back with a form error in a new checkbox field
    User A must activate the checkbox and saves the form again, to overwrite.
    """
    sites_filter = "entry__sites__id__in" # for TagLanguageSitesFilter
    
    last_update = forms.DateTimeField(
        widget = forms.widgets.HiddenInput
    )
    overwrite = forms.BooleanField(required=False,
        help_text="Activate this for overwrite the current blog entry.",
        widget = forms.widgets.HiddenInput
    )

    def clean(self):
        cleaned_data = super(BlogContentForm, self).clean()
        old_last_update = cleaned_data["last_update"]
        last_save_datetime = self.instance.lastupdatetime
        last_save_datetime = last_save_datetime.replace(microsecond=0) # strip microseconds
        if last_save_datetime > old_last_update and not cleaned_data.get("overwrite", False):
            # The entry was save before from a other user and overwrite was not checked, yet.
            msg = (
                "This blog entry was changed by user '%s' since you edit it!"
                " Activate this checkbox to save anyway."
            ) % self.instance.lastupdateby
            if settings.DEBUG:
                msg += " (current: %s - your old: %s)" % (last_save_datetime, old_last_update)

            self._errors["overwrite"] = self.error_class([msg])

            # Add the overwrite checkbox to the form by make it visible:
            self.fields["overwrite"].widget = forms.widgets.CheckboxInput()

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(BlogContentForm, self).__init__(*args, **kwargs)
        # Saves the current last update time as the *initial* value:
        self.fields["last_update"].initial = self.instance.lastupdatetime

    class Meta:
        model = BlogEntryContent
        exclude = ("entry",)

class BlogForm(TagLanguageSitesFilter, forms.ModelForm):
    """
    Form for create/edit a blog entry.
    """
    sites_filter = "entry__sites__id__in" # for TagLanguageSitesFilter
    sites = forms.MultipleChoiceField(
        # choices= Set in __init__, so the Queryset would not execute at startup
        help_text=_("On which site should this entry exists?")
    )

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        self.fields["sites"].choices = Site.objects.all().values_list("id", "name")
        self.fields["sites"].initial = settings.SITE_ID

    class Meta:
        model = BlogEntryContent
        exclude = ("entry",)
