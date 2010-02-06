# coding: utf-8

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# http://code.google.com/p/django-tagging/
from tagging.utils import parse_tag_input

from pylucid_project.utils.site_utils import SitePreselectPreference

from dbpreferences.forms import DBPreferencesBaseForm

TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"

SKIP_TAGS_CACHE = None

class LexiconPrefForm(SitePreselectPreference, DBPreferencesBaseForm):
    skip_tags = forms.CharField(
        required=False,
        initial="a input h1 h2 h3 h4 h5 h6 textarea fieldset script",
        help_text=mark_safe(
            _('Don\'t replace a word if it exist in the given html tags.'
            ' (tagging field <a href="%s" class="openinwindow"'
            ' title="Information about splitting.">format help</a>)') % TAG_INPUT_HELP_URL
        )
    )

    def clean(self, *args, **kwargs):
        """ hook into admin change validation for cleaning SKIP_TAGS_CACHE """
        global SKIP_TAGS_CACHE
        SKIP_TAGS_CACHE = None
#        print "*** Clean skip tags cache"
        return super(LexiconPrefForm, self).clean(*args, **kwargs)

    def get_skip_tags(self):
        global SKIP_TAGS_CACHE
        if SKIP_TAGS_CACHE is None:
#            print "*** Fill skip tags cache"
            self.get_preferences()
            skip_tag_string = self.data.get("skip_tags", "a input h1 h2 h3 h4 h5 h6 textarea fieldset")
            SKIP_TAGS_CACHE = parse_tag_input(skip_tag_string)

#        print "*** skip tags: %r" % SKIP_TAGS_CACHE

        return SKIP_TAGS_CACHE

    class Meta:
        app_label = 'lexicon'
