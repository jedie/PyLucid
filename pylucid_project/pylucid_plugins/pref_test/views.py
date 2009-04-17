
import pprint

from django.http import HttpResponse

from dbpreferences.models import Preference

from pref_test.preference_forms import TestForm


def lucidTag(request):
    form = TestForm()
    pref_data = Preference.objects.get_pref(form)
    
    return HttpResponse("<pre>%s</pre>" % pprint.pformat(pref_data))