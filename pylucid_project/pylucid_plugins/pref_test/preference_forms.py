# coding: utf-8

from django import forms

from dbpreferences.forms import DBPreferencesBaseForm


class TestForm(DBPreferencesBaseForm):
    """ test preferences form """
    subject = forms.CharField(initial="foobar", help_text="Some foo text")   
    foo_bool = forms.BooleanField(initial=True, required=False, help_text="Yes or No?")
    count = forms.IntegerField(initial=10, min_value=1, help_text="A max number")
    font_size = forms.FloatField(initial=0.7, min_value=0.1, help_text="font size")

    class Meta:
        app_label = 'pref_test'