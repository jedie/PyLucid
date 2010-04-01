# coding:utf-8

import os
from datetime import datetime
from tempfile import gettempdir

from datetime import datetime, timedelta
from django.utils.tzinfo import FixedOffset
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from django.utils.translation import ugettext as _

from pylucid_project.utils.SimpleStringIO import SimpleStringIO
from pylucid_project.utils.timezone import utc_offset

from pylucid_project.apps.pylucid.models import Language, PageTree, PageMeta, LogEntry
from pylucid_project.apps.pylucid.decorators import check_permissions, render_to

from pylucid_project.apps.pylucid_admin.admin_menu import AdminMenu


MYSQL_ENCODING_VARS = (
    "character_set_server", "character_set_connection", "character_set_results", "collation_connection",
)


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
    admin_menu.add_menu_entry(
        parent=menu_section_entry,
        name="timezone info", title="INformation about timezone settings.",
        url_name="System-timezone"
    )

    return "\n".join(output)

#-----------------------------------------------------------------------------

def _cache_backend_test(request, out):
    out.write(_("\tsettings.CACHE_BACKEND is '%s'") % settings.CACHE_BACKEND)

    if settings.CACHE_BACKEND.startswith("dummy") or settings.CACHE_BACKEND.startswith("locmem"):
        out.write(_("\tPlease setup CACHE_BACKEND in you local_settings.py!"))
        out.write(_("\tmore info: http://docs.djangoproject.com/en/dev/topics/cache/#setting-up-the-cache"))
        tempdir = gettempdir()
        out.write(_("\te.g.: CACHE_BACKEND='file://%s'") % os.path.join(tempdir, "PyLucid_cache"))
        return

    cache_key = "cache test"
    content = "A cache test content..."
    cache_timeout = 50
    cache.set(cache_key, content, cache_timeout)
    cached_content = cache.get(cache_key)
    if cached_content == None:
        out.write(_("\t* Get None back. Cache didn't work!"))
        return
    elif cached_content == content:
        out.write(_("\t* Cache works fine ;)"))
    else:
        # Should never appears
        out.write(_("\t* Error! Cache content not the same!"))

    cache.delete(cache_key)
    cached_content = cache.get(cache_key)
    if cached_content != None:
        out.write(_("\t* Error: entry not deleted!"))

#-----------------------------------------------------------------------------

def _database_encoding_test(request, out):
    """
    Simple database encoding test:
        insert a test string into the database and check if 
        it is the same if we get the same entry back
    Use the PyLucid log table
    """
    out.write("Info: Not all database engines passed all tests!")

    def _test(range_txt, chr_range):
        out.write("\t%s test:" % range_txt)
        TEST_STRING = u"".join([unichr(i) for i in chr_range])
        try:
            log_entry1 = LogEntry.objects.log_action(
                "pylucid_plugin.system", "Database encoding test", request,
                message="%s test" % range_txt, long_message=TEST_STRING
            )
        except Warning, err:
            out.write("\t\tError: get a warning: %s" % err)
            return

        log_entry_id = log_entry1.id
        log_entry2 = LogEntry.objects.get(id=log_entry_id)
        if TEST_STRING == log_entry2.long_message:
            log_entry2.message += " - passed"
            out.write("\t\ttest passed")
        else:
            out.write("\t\ttest *NOT* passed")
            log_entry2.message += " - failed"
        log_entry2.save()

    _test("ASCII (32-126)", xrange(32, 126))
    _test("latin-1 (128-254)", xrange(128, 254))
    _test("ASCII control characters (0-31)", xrange(0, 31))
    _test("unicode plane 1-3 (0-12286 in 16 steps)", xrange(0, 12286, 16))
    _test("all unicode planes (0-65534 in 256 steps)", xrange(0, 65534, 256))



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
        out.write("settings.DEBUG, ok")
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

    if settings.DATABASE_ENGINE == "mysql":
        try:
            import MySQLdb
            out.write("MySQLdb.__version__  : %s" % repr(MySQLdb.__version__))
            out.write("MySQLdb.version_info : %s" % repr(MySQLdb.version_info))
        except Exception, err:
            out.write("MySQLdb info error: %s" % err)

        cursor = connection.cursor()
        out.write("\nSome MySQL encoding related variables:")

        for var_name in MYSQL_ENCODING_VARS:
            cursor.execute("SHOW VARIABLES LIKE %s;", (var_name,))
            raw_result = cursor.fetchall()
            try:
                result = raw_result[0][1]
            except IndexError, err:
                out.write("%30s: Error: %s (raw result: %r)" % (var_name, err, raw_result))
            else:
                out.write("%30s: %s" % (var_name, result))
        out.write("- "*40)


    out.write("\nDatabase unicode test:")
    _database_encoding_test(request, out)
    out.write("- "*40)

    out.write("\nTest cache backend:")
    _cache_backend_test(request, out)
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
    out.write("- "*40)

    out.write("Check if all PageTree has at lease a PageMeta instance in the default system language:")
    default_lang_entry = Language.objects.get_or_create_default(request)
    exist_all = True
    # TODO: Can we but this into a big QuerySet?
    for pagetree in PageTree.on_site.all():
        exist = PageMeta.objects.filter(pagetree=pagetree, language=default_lang_entry)
        if not exist:
            exist_all = False
            out.write(
                "*** Error: PageTree entry %r has no PageMeta in default language (%r)!!!" % (
                    pagetree, default_lang_entry
                )
            )
    if exist_all:
        out.write("ok.")
    out.write("- "*40)

    context = {
        "title": "Basic system setup check",
        "results": out.getlines(),
    }
    return context




@check_permissions(superuser_only=True)
@render_to("system/timezone.html")
def timezone(request):
    """
    Display some informations about timezone
    """
    # get a timestamp from Django ORM datetime with 'auto_now_add'
    temp_log_entry = LogEntry.objects.log_action("pylucid_plugin.system", "timezone test", request)
    auto_now_add = temp_log_entry.createtime
    temp_log_entry.delete()

    context = {
        "datetime_now": datetime.now(),
        "datetime_utcnow": datetime.utcnow(),
        "auto_now_add": auto_now_add,
        "settings_TIME_ZONE": settings.TIME_ZONE,
        "environ_TZ": os.environ.get("TZ", "----"),
        "utc_offset": utc_offset(),
    }
    return context

