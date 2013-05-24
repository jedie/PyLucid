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

from django.conf import settings
from django.contrib import auth, messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.models.log import LogEntry
from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu
from pylucid_project.pylucid_plugins.auth.forms import JSPasswordChangeForm
from pylucid_project.pylucid_plugins.auth.preference_forms import AuthPreferencesForm

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



def _wrong_old_password(request, debug_msg, user=None):
    """ username or password is wrong. """
    if settings.DEBUG:
        error_msg = debug_msg
    else:
        error_msg = _("Wrong old password. Try again.")

    messages.error(request, error_msg)

    # Protection against DOS attacks.
    pref_form = AuthPreferencesForm()
    preferences = pref_form.get_preferences()
    min_pause = preferences["min_pause"]
    ban_limit = preferences["ban_limit"]
    try:
        LogEntry.objects.request_limit(
            request, min_pause, ban_limit, app_label="pylucid_plugin.auth", action="old password error", no_page_msg=True
        )
    except LogEntry.RequestTooFast, err:
        # min_pause is not observed
        error_msg = unicode(err) # ugettext_lazy

    # Log this error (Important: must be logged after LogEntry.objects.request_limit() stuff!
    if user is not None:
        data = {"user_username": user.username}
    else:
        data = None
    LogEntry.objects.log_action(
        app_label="pylucid_plugin.auth", action="old password error", message=debug_msg, data=data
    )

    url = reverse("Auth-JS_password_change")
    return HttpResponseRedirect(url)


@render_to("auth/JS_password_change.html")
def JS_password_change(request):
    """
    set a new password with encryption directly in the browser

    Currently we only support the Django salted SHA1 password hasher
    implemented in hashers.SHA1PasswordHasher() witch is not recommended anymore.

    TODO:
    Use http://code.google.com/p/crypto-js/
    to support hashers.PBKDF2PasswordHasher() in JS Code
    """
    context = {
        "title": _("JavaScript password change"),
    }

    user = request.user
    user_profile = user.get_profile()

    loop_count = _get_loop_count() # get "loop_count" from AuthPreferencesForm

    if request.method == 'POST':
        form = JSPasswordChangeForm(request.POST)
        if not form.is_valid():
            debug_msg = "form error: %s" % ", ".join(form.errors)
            return _wrong_old_password(request, debug_msg, user)
        else:
            # old password "JS-SHA1" values for pre-verification:
            sha_a = form.cleaned_data["sha_a"]
            sha_b = form.cleaned_data["sha_b"]
            cnonce = form.cleaned_data["cnonce"]

            # new password as salted SHA1 hash:
            salt = form.cleaned_data["salt"]
            sha1hash = form.cleaned_data["sha1hash"]

            challenge = request.session.pop("challenge")
            sha_checksum = user_profile.sha_login_checksum
            try:
                # authenticate with:
                # pylucid.system.auth_backends.SiteSHALoginAuthBackend
                user2 = auth.authenticate(
                    user=user, challenge=challenge,
                    sha_a=sha_a, sha_b=sha_b,
                    sha_checksum=sha_checksum,
                    loop_count=loop_count, cnonce=cnonce
                )
            except Exception, err: # e.g. low level error from crypt
                debug_msg = "JS_password_change: auth.authenticate() failed: %s" % err
                return _wrong_old_password(request, debug_msg, user)

            if user2 is None:
                debug_msg = "JS_password_change: auth.authenticate() failed. (must be a wrong password)"
                return _wrong_old_password(request, debug_msg, user)

            # pre-verification success -> save new password

            django_salted_hash = "sha1$%s$%s" % (salt, sha1hash)
            sha_login_salt, sha_login_checksum = crypt.django_to_sha_checksum(django_salted_hash)

            # save new password in django.contrib.auth.model.User():
            user.password = django_salted_hash
            user.save()

            # save new password in PyLucid user profile:
            user_profile.sha_login_checksum = sha_login_checksum
            user_profile.sha_login_salt = sha_login_salt
            user_profile.save()

            messages.success(request, "TODO: New user password set.")

        url = reverse("Auth-JS_password_change")
        return HttpResponseRedirect(url)
    else:
        sha_login_salt = user_profile.sha_login_salt

        # create a new challenge and add it to session
        challenge = _get_challenge(request)

        context.update({
            "challenge": challenge,
            "sha_login_salt": sha_login_salt,
            "old_salt_len": crypt.OLD_SALT_LEN,
            "salt_len": crypt.SALT_LEN,
            "hash_len": crypt.HASH_LEN,
            "loop_count": loop_count,
            "get_salt_url": request.path + "?auth=get_salt",
            "sha_auth_url": request.path + "?auth=sha_auth",
        })
    return context


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
#        verbose=True
        verbose=False
    )
