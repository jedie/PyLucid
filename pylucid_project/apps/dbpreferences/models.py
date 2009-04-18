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
        """ save the initial form values as the preferences into the database """
        form_dict = forms_utils.get_init_dict(form)
        new_entry = Preference(
            site = current_site,
            app_label = app_label,
            form_name = form_name,
            preferences = form_dict,
        )
        new_entry.save()
        return form_dict
        
    def get_pref(self, form):
        """
        returns the preferences for the given form
        stores the preferences into the database, if not exist.
        """
        assert isinstance(form, forms.Form), ("You must give a form instance and not only the class!")
        
        current_site = Site.objects.get_current()
        app_label = form.Meta.app_label
        form_name = form.__class__.__name__
        
        try:
            db_entry = self.get(site=current_site, app_label=app_label, form_name=form_name)
        except Preference.DoesNotExist:
            # Save initial form values into database
            form_dict = self.save_form_init(form, current_site, app_label, form_name)
        else:
            form_dict = db_entry.preferences
        
        return form_dict



class DictFormWidget(forms.Textarea):
    """ form widget for preferences dict """
    def render(self, name, value, attrs=None):
        """
        FIXME: Can we get the original non-serialized db value here?
        """
        value = serialize(value)
        return super(DictFormWidget, self).render(name, value, attrs)


class DictFormField(forms.CharField):
    """ form field for preferences dict """
    widget = DictFormWidget
    
    def clean(self, value):
        """
        validate the form data
        FIXME: How can we get the pref form class for validating???
        """
        value = super(DictFormField, self).clean(value)
        try:
            return deserialize(value)
        except Exception, err:
            raise forms.ValidationError("Can't deserialize: %s" % err)


class DictField(models.TextField):
    """
    A dict field.
    Stores a python dict into a text field. 
    """
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        """ decode the data dict using simplejson.loads() """
        if isinstance(value, dict):
            return value
        return deserialize(value)

    def get_db_prep_save(self, value):
        "Returns field's value prepared for saving into a database."
        assert isinstance(value, dict)
        return serialize(value)
#    
    def formfield(self, **kwargs):
        # Always use own form field and widget:
        kwargs['form_class'] = DictFormField
        kwargs['widget'] = DictFormWidget
        return super(DictField, self).formfield(**kwargs)



class Preference(models.Model):
    """    
    Plugin preferences
    """
    objects = PreferencesManager()

    id = models.AutoField(primary_key=True, help_text="The id of this preference entry, used for lucidTag")

    site = models.ForeignKey(Site, editable=False, verbose_name=_('Site'))
    app_label = models.CharField(max_length=128, editable=False,
        help_text="app lable, must set via form.Meta.app_label")
    form_name = models.CharField(max_length=128, editable=False,
        help_text="preference form class name")

    preferences = DictField(null=False, blank=False, #editable=False,
        help_text="serialized preference form data dictionary")

    createtime = models.DateTimeField(auto_now_add=True, help_text="Create time",)
    lastupdatetime = models.DateTimeField(auto_now=True, help_text="Time of the last change.",)
    lastupdateby = models.ForeignKey(User, editable=False, null=True, blank=True,
        related_name="%(class)s_lastupdateby", help_text="User as last edit the current page.",)

    #__________________________________________________________________________
    
    def get_form_class(self):
        """ returns the form class for this preferences item """
        from_name = "%s.%s" % (self.app_label, PREF_FORM_FILENAME)
        form = easy_import.import3(from_name, self.form_name)
        return form
    
    #__________________________________________________________________________

    def __unicode__(self):
        return u"Preferences for %s.%s.%s" % (self.site, self.app_label, self.form_name)

    class Meta:
        unique_together = ("site", "app_label", "form_name")
        permissions = (("can_change_preferences", "Can change preferences"),)
        ordering = ("site", "app_label", "form_name")
        verbose_name = verbose_name_plural = "preferences"
#        db_table = 'PyLucid_preference'
#        app_label = 'PyLucid'
        
        
        
if __name__ == "__main__":
    import doctest
    doctest.testmod(
#        verbose=True
        verbose=False
    )
    print "DocTest end."