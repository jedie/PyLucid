
import pprint

from django.http import HttpResponse

from dbpreferences.models import Preference

from pref_test.preference_forms import TestForm


def lucidTag(request):
    form = TestForm()
    pref_data = form.get_preferences()
    
    request.user.message_set.create(message="pref_test.lucidTag - Test with request.user.message_set.create")
    request.page_msg("pref_test.lucidTag - Test with request.page_msg")
    
    return HttpResponse("<pre>%s</pre>" % pprint.pformat(pref_data))