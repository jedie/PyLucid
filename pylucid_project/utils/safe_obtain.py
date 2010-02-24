# coding: utf-8

from django.conf import settings
from django.utils.translation import ugettext as _

def safe_get_integer(request, get_key, default, min, max):
    """
    safe way to get a integer from a request.GET parameter.
    use default, if GET parameter doesn't exist or is not a integer.
    Limit the number to min and max. 
    """
    error = None
    number = request.GET.get(get_key, default)
    try:
        number = int(number)
    except ValueError:
        error = _("%r is not a integer. (Use default number)") % get_key
        number = default

    if number < min:
        error = _("%(get_key)r is too small. (Use: %(min)s)") % {
            "get_key": get_key, "min": min
        }
        return min, error
    if number > max:
        error = _("%(get_key)r is too large. (Use: %(max)s)") % {
            "get_key": get_key, "max": max
        }
        return max, error

    return number, error


def safe_pref_get_integer(request, get_key, Preferences,
              default_key, default_fallback,
              min_key, min_fallback,
              max_key, max_fallback):
    """
    returns a integer from request.GET[get_key] in a safe way.
    
    Use information from a DBPreferences class for limiting with min/max.
    If GET Parameter doesn't exist or is not a integer, use default number.

    default_key, min_key and max_key:
        names of the DBPreferences Attributes
        
    default_fallback, min_fallback and max_fallback:
        fallback, if preferences doesn't exist, yet.
    """
    pref_form = Preferences()
    preferences = pref_form.get_preferences()

    default = preferences.get(default_key, default_fallback)
    min = preferences.get(min_key, min_fallback)
    max = preferences.get(max_key, max_fallback)

    number, error = safe_get_integer(request, get_key, default, min, max)
    return number, error
