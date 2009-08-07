# coding:utf-8

from django.conf import settings

from pylucid_project.utils.SimpleStringIO import SimpleStringIO

from pylucid.models import Language
from pylucid.decorators import check_permissions, render_to

from pylucid_admin.admin_menu import AdminMenu


def install(request):
    """ insert PyLucid admin views into PageTree """
    output = []

    admin_menu = AdminMenu(request, output)
    menu_section_entry = admin_menu.get_or_create_section("system")

    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="base check", title="A basic system setup check.",
        url_name="System-base_check"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------

@check_permissions(superuser_only=True)
@render_to("system/base_check.html")
def base_check(request):
    out = SimpleStringIO()

    if settings.DEBUG:
        out.write(
            "*** Error: settings.DEBUG in on!"
            " (Should be off in productive environments!)"
        )
        out.write("\tSee: http://docs.djangoproject.com/en/dev/ref/settings/#debug")
    else:
        out.write("settings.settings.DEBUG, ok")
    out.write("- "*40)


    if settings.PYLUCID.I18N_DEBUG:
        out.write(
            "*** Error: pylucid app_settings.I18N_DEBUG is on!"
            " (Should be off in productive environments!)"
        )
    else:
        out.write("pylucid app_settings.I18N_DEBUG, ok.")
    out.write("- "*40)


    if settings.SECRET_KEY == "":
        out.write(
            "*** Error: settings.SECRET_KEY not set!"
            " (You should add it into local-settings.py!)"
        )
        out.write("\tSee: http://docs.djangoproject.com/en/dev/ref/settings/#secret-key")
    else:
        out.write("settings.SECRET_KEY, ok.")
    out.write("- "*40)

    try:
        lang_entry = Language.objects.get(code=settings.LANGUAGE_CODE)
    except Language.DoesNotExist, err:
        out.write("*** Error: LANGUAGE_CODE %r doesn't exist!" % settings.LANGUAGE_CODE)
        languages = Language.objects.values_list("code", flat=True)
        out.write("\tExisting languages are: %r" % languages)
        out.write("\tset/change LANGUAGE_CODE in local-settings.py or create language %r." % settings.LANGUAGE_CODE)
    else:
        out.write("settings.LANGUAGE_CODE, ok.")
    #out.write("- "*40)

    context = {
        "title": "Basic system setup check",
        "results": out.getlines(),
    }
    return context
