# coding:utf-8

"""
    auth pylucid admin views
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyleft: 2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


if __name__ == "__main__":
    # For doctest only
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "django.conf.global_settings"
    from django.conf import global_settings
    global_settings.SITE_ID = 1

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu

from pylucid_project.utils import crypt

from pylucid_project.pylucid_plugins.auth.views import _get_challenge, \
    _get_loop_count



def install(request):
    """ install PyLucid admin views """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("tools")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="user profile", title="Your user profile (e.g. change your password)",
        url_name="Auth-profile_index"
    )

    return "\n".join(output)


#-----------------------------------------------------------------------------


@check_permissions(superuser_only=False, must_staff=False)
@render_to("auth/profile_index.html")
def profile_index(request):
    context = {
        "title": _("Your user profile"),
    }
    return context


@render_to("auth/JS_password_change.html")
def JS_password_change(request):
    user_profile = request.user.get_profile()
    sha_login_salt = user_profile.sha_login_salt

    # create a new challenge and add it to session
    challenge = _get_challenge(request)

    loop_count = _get_loop_count() # get "loop_count" from AuthPreferencesForm

    context = {
        "title": _("JavaScript password change"),
        "challenge": challenge,
        "sha_login_salt": sha_login_salt,
        "salt_len": crypt.SALT_LEN,
        "hash_len": crypt.HASH_LEN,
        "loop_count": loop_count,
        "get_salt_url": request.path + "?auth=get_salt",
        "sha_auth_url": request.path + "?auth=sha_auth",
    }
    return context


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
