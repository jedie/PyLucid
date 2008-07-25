
"""
3. low level admin

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

import pickle

from django.conf import settings
from PyLucid.models import Page, Template
from PyLucid.install.BaseInstall import BaseInstall

from django import forms
from django.core import serializers




#______________________________________________________________________________

#===============================================================================
#serializer_formats = serializers.get_serializer_formats()
#class DumpForm(forms.Form):
#    """
#    django newforms
#    """
#    format = forms.ChoiceField(
#        choices=[(i,i) for i in serializer_formats],
#    )
#    write_file = forms.BooleanField(initial=False, required=False)
#
#dump_template = """
#{% extends "PyLucid/install/base.html" %}
#{% block content %}
#<h1>Dump DB</h1>
#
#<form method="post">
#    {{ DumpForm }}
#    <input value="execute" name="execute" type="submit">
#</form>
#{% if output %}
#<fieldset><legend>{{ file_name|escape }}</legend>
#    <pre>{{ output|escape }}</pre>
#</fieldset>
#{% endif %}
#{% endblock %}
#"""
#class Dump_DB(BaseInstall):
#    def view(self):
#        if "format" in self.request.POST:
#            # Form has been sended
#            init_values = self.request.POST.copy()
#        else:
#            # Requested the first time -> insert a init codeblock
#            init_values = {
#                "format": serializer_formats[0],
#                "write_file": False,
#            }
#
#        dump_form = DumpForm(init_values)
#
#        dump_form_html = dump_form.as_p()
#        self.context["DumpForm"] = dump_form_html
#
#        if (not "format" in self.request.POST) or (not dump_form.is_valid()):
#            # Requested the first time -> display the form
#            return self._render(dump_template)
#
#        format = dump_form.clean_data["format"]
#        write_file = dump_form.clean_data["write_file"]
#
#        from django.db.models import get_app, get_apps, get_models
#        from django.core import serializers
#
#        app_list = get_apps()
#
#        # Check that the serialization format exists; this is a shortcut to
#        # avoid collating all the objects and _then_ failing.
#        serializers.get_serializer(format)
#
#        fixture_filename = "PyLucid/fixtures/initial_data.%s" % format
#        self.context["file_name"] = fixture_filename
#        if write_file:
#            output = ["Open output file '%s'..." % fixture_filename]
#            try:
#                dumpfile = file(fixture_filename, "w")
#            except Exception, e:
#                output.append("Error: %s" % e)
#                return response
#            else:
#                output.append("OK\n")
#
#        objects = []
#        for app in app_list:
#            for model in get_models(app):
#                model_objects = model.objects.all()
#                objects.extend(model_objects)
#
#        db_data = serializers.serialize(format, objects)
#
#        if write_file:
#            output.append("Write to file...")
#            if format=="python":
#                try:
#                    pickle.dump(db_data, dumpfile)
#                except Exception, e:
#                    output.append("Error: %s" % e)
#                else:
#                    output.append("OK\n")
#            else:
#                try:
#                    dumpfile.write(db_data)
#                except Exception, e:
#                    output.append("Error: %s" % e)
#                else:
#                    output.append("OK\n")
#            dumpfile.close()
#        else:
#            if format=="xml":
#                mimetype='text/xml'
#            else:
#                mimetype='text/plain'
#            response = HttpResponse(mimetype=mimetype)
#            response.write(db_data)
#            return response
#
#        self.context["output"] = "".join(output)
#        return render(dump_template)
#
#def _dump_db(request):# deactivated with the unterscore!
#    """
#    dump db data (using fixture)
#    """
#    return Dump_DB(request).start_view()
#===============================================================================

#______________________________________________________________________________

class Options(object):
    """ Fake optparse options """
    def __init__(self):
        self.datadir = settings.INSTALL_DATA_DIR
        self.verbose = True
        self.stdout = None
        self.remain = None
        self.settings = "PyLucid.settings"

class Dump_DB(BaseInstall):
    def view(self):
        from PyLucid.tools.db_dump import dumpdb
        apps = []

        self._redirect_execute(
            dumpdb, apps, 'py', Options()
        )

        return self._simple_render(headline="DB dump (using db_dump.py)")

def dump_db(request):
    """
    1. dump db data (using db_dump.py)
    """
    return Dump_DB(request).start_view()

#______________________________________________________________________________

class CleanupDjangoTables(BaseInstall):
    def view(self):
        from PyLucid.tools.clean_tables import clean_contenttypes, clean_permissions
        self._redirect_execute(
            clean_contenttypes, debug=False
        )
        self.context["output"] += "\n\n"
        self._redirect_execute(
            clean_permissions, debug=False
        )
        return self._simple_render(headline="Cleanup django tables")


def cleanup_django_tables(request):
    """
    cleanup django tables
    """
    return CleanupDjangoTables(request).start_view()

#______________________________________________________________________________

syncdb_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>Recreate all django tables</h1>
<h2>Note:</h2>
<p>After this you must recreate a user and assign the pages</p>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""

from PyLucid.install.install import Sync_DB
class RecreateDjangoTables(Sync_DB):
    DJANGO_TABLE_PREFIXES = ("auth", "django")
    def view(self):

        self._redirect_execute(
            self.delete_tables
        )
        self.context["output"] += "\n\n"

        # self.syncdb is inherited from Sync_DB
        self._redirect_execute(self._syncdb)

        return self._render(syncdb_template)

    def delete_tables(self):
        print "Delete django tables:"
        print "-"*80

        from django.db import connection

        cursor = connection.cursor()
        SQLcommand = "Drop table %s;"

        from django.core.management import sql
        table_list = sql.table_list()

        for table_name in table_list:
            prefix = table_name.split("_")[0]
            if not prefix in self.DJANGO_TABLE_PREFIXES:
                continue

            SQL = SQLcommand % table_name
            print "%s..." % SQL,
            cursor.execute(SQL)
            print "OK"

def recreate_django_tables(request):
    """
    Recreate all django tables (WARNING: user/groups/permission lost!)
    """
    return RecreateDjangoTables(request).start_view()





class CheckPreferences(BaseInstall):
    def view(self):
        self._redirect_execute(
            self.check_preferences
        )
        return self._simple_render(headline="Check and correct Preferences")

    def check_preferences(self):
        self._check_index_page()
        self._check_auto_shortcuts()

    def _verbose_get(self, name):
        print "_"*80
        print "Check '%s'..." % name
        p = Preference.objects.get(name = name)
        try:
            print "Description:", p.description
            print "default value:", p.default_value
            print "current value:", p.value
        except Exception, msg:
            print "Error:", msg
        return p

    def _check_index_page(self):
        try:
            p = self._verbose_get("index page")
            page_id = p.value
            # page_id = 9999999 # Not exist test
            page = Page.objects.get(id = page_id)
        except Exception, msg:
            print "Error:", msg
            page = Page.objects.all().order_by("parent", "position")[0]
            print "Assign the page:", page
            p = Preference.objects.get(name = "index page")
            p.value = page.id
            p.save
            print "saved."
        else:
            print "OK"

    def _check_auto_shortcuts(self):
        try:
            p = self._verbose_get('auto shortcuts')
            value = p.value
            # value = 123 # Failed test
            assert value in (True, False)
        except Exception, msg:
            print "Error:", msg
            print "set to 'True'"
            p = Preference.objects.get(name = "auto shortcuts")
            p.value = True
            p.save()
            print "saved."
        else:
            print "OK"

def check_preferences(request):
    """
    Check and correct Preferences.
    """
    return CheckPreferences(request).start_view()



user_admin_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>Low level user administration</h1>
<strong>Note:</strong> Passwords will send in plain text :(
<form method="post">
{% if user_form %}
    <h3>set a new password:</h3>
    {{ user_form.as_p }}
    <input value="save" name="save" type="submit">
{% else %}
    <h3>user list</h3>
    <ul>
    {% for user in user_list %}
        <li>
            {{ user.username }}
            <input value="change_pass" name="{{ user.id }}" type="submit">
        </li>
    {% endfor %}
    </ul>
{% endif %}
</form>
{% endblock %}
"""
class PasswordForm(forms.Form):
    password = forms.CharField(
        min_length=8, max_length=128,
        widget = forms.PasswordInput()
    )
    user_id = forms.IntegerField(widget = forms.HiddenInput())


class UserAdmin(BaseInstall):
    """
    This is a quick but bad way to change the user password.
    """
    def view(self, *url_args):
        self._build_context()
#        self.page_msg(self.context)
        return self._render(user_admin_template)

    def _put_userlist(self):
        from PyLucid.models import User
        user_list = User.objects.all()
        self.context["user_list"] = user_list

    def _build_context(self):
        from PyLucid.models import User

        if not self.request.POST:
            self._put_userlist()
            return

#        self.page_msg(self.request.POST)

        if "save" in self.request.POST:
            pass_form = PasswordForm(self.request.POST)
            if pass_form.is_valid():
                raw_password = pass_form.cleaned_data["password"]
                user_id = pass_form.cleaned_data["user_id"]
                user = User.objects.get(id = user_id)
                user.set_password(raw_password)
                user.save()
                self.page_msg.green("New password saved.")
                self._put_userlist()
                return
        elif len(self.request.POST) == 1:
            try:
                user_id = int(self.request.POST.keys()[0])
                user = User.objects.get(id = user_id)
                self.context["user_id"] = user_id
                self.context["user_form"] = PasswordForm({"user_id": user_id})
            except Exception, e:
                self.page_msg.red("Error: %s" % e)
        else:
            self.page_msg.red("POST Error!")


def user_admin(request, *url_args):
    """
    User administration
    """
    return UserAdmin(request).start_view(*url_args)



class CheckPageTree(BaseInstall):
    """
    If a page has a parent-page-id witch not exists, we have corrupt data in
    the page tree. We can correct it here.
    """
    def view(self):
        self._redirect_execute(self.check_page_tree)
        return self._simple_render(headline="Check and correct the page tree")

    def check_page_tree(self):
        page_data = Page.objects.values(
            "id", "parent", "name", "title", "shortcut"
        ).order_by("position")
        page_dict = {}
        for page in page_data:
            page_dict[page["id"]] = page

        for page in page_data:
            parent_id = page["parent"]
            if parent_id == None:
                # A root page
                print "Skip root page '%s' - '%s'" % (
                    page["name"], page["title"]
                )
                continue
            print page
            if not parent_id in page_dict:
                print "Error:"
                print "Parent page for the page '%s' - '%s' not exists!" % (
                    page["name"], page["title"]
                )
                print "Assign the page to the root (set parent=None)...",
                page_obj = Page.objects.get(id__exact=page["id"])
                page_obj.parent = None
                page_obj.save()
                print "OK"
                print


def check_page_tree(request, *url_args):
    """
    Check and correct the page tree
    """
    return CheckPageTree(request).start_view(*url_args)


#______________________________________________________________________________


class RepairAutoIncrement(BaseInstall):
    """
    repair 'auto increment'.
    MySQL only!
    For users how forgott to insert auto increment in a SQL dump ;)
    """
    def view(self):
        self._redirect_execute(self.repair_auto_increment)
        return self._simple_render(headline="repair 'auto increment'")

    def repair_auto_increment(self):
        from django.db import connection

        cursor = connection.cursor()
        SQLcommand = "Drop table %s;"

        from django.core.management import sql
        table_list = sql.table_list()

        for table_name in table_list:
            print "_"*79
            print table_name
            SQL = "SHOW COLUMNS FROM %s LIKE 'id';" % table_name
            cursor.execute(SQL)
            result = cursor.fetchone()
            if result in ((), None):
                print "No 'id' in table, ok."
                continue

            cursor_info = {}
            for no, info in enumerate(cursor.description):
                cursor_info[info[0]] = no

            if result[cursor_info["Extra"]] == "auto_increment":
                print "'auto_increment' exist, ok."
                continue

            SQL = (
                "ALTER TABLE %(table_name)s CHANGE %(field)s"
                " %(field)s %(type)s AUTO_INCREMENT;"
            ) % {
                "table_name": table_name,
                "field": result[cursor_info["Field"]],
                "type": result[cursor_info["Type"]],
            }
            print "set auto_increment...",
            try:
                cursor.execute(SQL)
            except Exception, e:
                print "Error:", e
            else:
                print "ok"



def repair_auto_increment(request, *url_args):
    """
    repair 'auto increment' (MySQL only!)
    """
    return RepairAutoIncrement(request).start_view(*url_args)
