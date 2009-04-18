# coding: utf-8

"""
    DBPreferences - models
    ~~~~~~~~~~~~~~~~~~~~~~

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"

from django import forms
from django.db import models
from django.utils import simplejson
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User, Group

from dbpreferences.tools import forms_utils, easy_import

# The filename in witch the form should be stored:
PREF_FORM_FILENAME = "preference_forms"


def serialize(data):
    return simplejson.dumps(data, sort_keys=True, indent=4)

def deserialize(stream):
    return simplejson.loads(stream)


class PreferencesManager(models.Manager):
    """ Manager class for Preference model """
    def save_form_init(self, form, current_site, app_label, form_name):
        data_dict = forms_utils.get_init_dict(form)
        pref_data_string = serialize(data_dict)
        new_entry = Preference(
            site = current_site,
            app_label = app_label,
            form_name = form_name,
            pref_data_string = pref_data_string,
        )
        new_entry.save()
        return data_dict
        
    def get_pref(self, form):
        assert isinstance(form, forms.Form), ("You must give a form instance and not only the class!")
        
        current_site = Site.objects.get_current()
        app_label = form.Meta.app_label
        form_name = form.__class__.__name__
        
        try:
            db_entry = self.get(site=current_site, app_label=app_label, form_name=form_name)
        except Preference.DoesNotExist:
            data_dict = self.save_form_init(form, current_site, app_label, form_name)
        else:
            pref_data_string = db_entry.pref_data_string
            data_dict = deserialize(pref_data_string)
        
        return data_dict


class Preference(models.Model):
    """
    Plugin preferences
    """
    objects = PreferencesManager()

    id = models.AutoField(primary_key=True, help_text="The id of this preference entry, used for lucidTag")

    site = models.ForeignKey(Site, verbose_name=_('Site'))
    app_label = models.CharField(max_length=128, help_text="The app lable, must set via form.Meta.app_label")
    form_name = models.CharField(max_length=128, help_text="The form class name")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    lastupdateby = models.ForeignKey(User, editable=False, null=True, blank=True,
        related_name="%(class)s_lastupdateby", help_text="User as last edit the current page.",)

    comment = models.CharField(max_length=255, null=True, blank=True,
        help_text="Small comment for this preference entry")
    
    pref_data_string = models.TextField(null=False, blank=False,
        help_text="printable representation of the newform data dictionary")

    #__________________________________________________________________________

    def set_data(self, data_dict, user):
        """ set the dict encoded via simplejson.dumps() """
        self.pref_data_string = simplejson.dumps(data_dict, sort_keys=True, indent=4)
        self.lastupdateby = user

    def get_data(self):
        """ decode the data dict using simplejson.loads() """
        return simplejson.loads(self.pref_data_string)

    #__________________________________________________________________________
    
    def get_form_class(self):
        from_name = "%s.%s" % (self.app_label, PREF_FORM_FILENAME)
        form = easy_import.import3(from_name, self.form_name)
        return form
    
    #__________________________________________________________________________

    def __unicode__(self):
        return u"Preferences for %s.%s.%s" % (self.site, self.app_label, self.form_name)

    class Meta:
        unique_together = ("site", "app_label", "form_name")
#        db_table = 'PyLucid_preference'
#        app_label = 'PyLucid'
        
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."