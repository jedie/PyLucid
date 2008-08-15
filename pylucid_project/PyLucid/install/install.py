
"""
1. install

sollte ich mir mal ansehen:
http://code.djangoproject.com/wiki/CookBookScriptsMiniFlush
"""

from django.conf import settings

from django.utils.translation import ugettext as _
from django import forms
from django.contrib.auth.models import User

from PyLucid.install.BaseInstall import BaseInstall

import sys, os

#______________________________________________________________________________

syncdb_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>syncdb</h1>
<pre>{{ output|escape }}</pre>
{% endblock %}
"""
class Sync_DB(BaseInstall):

    # Drop this tables before syncdb:
    DROP_TABLES = (
#        "PyLucid_pagearchiv",
        "PyLucid_plugin",
        "PyLucid_preference",
        "PyLucid_preference2",
    )

    def view(self):
        self._redirect_execute(self._drop_tables)
        self._redirect_execute(self._syncdb)
        return self._render(syncdb_template)

    def _drop_tables(self):
        """
        This is only important for development, if we create a new model and
        change it.
        Should be not used in productive environment!
        """
        print
        print "drop tables:"
        print "-"*80
        from django.db import connection
        from django.db.models import get_app

        app = get_app("PyLucid")

        from django.core.management import sql
        from django.core.management.color import no_style
        statements = sql.sql_delete(app, no_style())

        cursor = connection.cursor()
        for statement in statements:
            for table_name in self.DROP_TABLES:
                if table_name in statement:
                    print "Delete table '%s' (%s):" % (table_name, statement),
                    try:
                        cursor.execute(statement)
                    except Exception, e:
                        print "Error:", e
                    else:
                        print "OK"
        print "-"*80

    def _syncdb(self):
        print
        print "syncdb:"
        print "-"*80
        from django.core import management
        management.call_command('syncdb', verbosity=1, interactive=False)
        print "-"*80
        print "syncdb ok."


def syncdb(request):
    """
    1. install Db tables (syncdb)
    """
    return Sync_DB(request).start_view()

#______________________________________________________________________________

class DB_DumpFakeOptions(object):
    """ Fake optparse options """
    datadir = 'PyLucid/db_dump_datadir'
    verbose = True
    stdout = None
    # Remain the records of the tables, default will delete all the records:
    remain = True
    settings = "PyLucid.settings"

class Init_DB2(BaseInstall):
    def view(self):
        from PyLucid.tools.db_dump import loaddb

        self._redirect_execute(
            loaddb,
            app_labels = [], format = "py", options = DB_DumpFakeOptions()
        )

        return self._simple_render(headline="init DB (using db_dump.py)")

def init_db2(request):
    """
    2. init DB data (using db_dump.py, Note: old preferences lost!)
    TODO: In the final we should not delete the preferences!
    """
    return Init_DB2(request).start_view()

#______________________________________________________________________________

install_modules_template = """
{% extends "install_base.html" %}
{% block pre_page_msg_content %}
<h1>Install all internal plugins:</h1>
{% endblock %}
"""
class InstallPlugins(BaseInstall):
    def view(self):
        from PyLucid.system.plugin_manager import auto_install_plugins

        auto_install_plugins(
            self.request.debug, self.page_msg, verbosity = 1
        )

        return self._render(install_modules_template)

def install_plugins(request):
    """
    3. install internal plugins
    """
    return InstallPlugins(request).start_view()

#______________________________________________________________________________

create_user_template = """{% extends "install_base.html" %}
{% load i18n %}
{% block content %}
<h1>{% trans 'Add user' %}</h1>

{% if output %}
    <pre>{{ output|escape }}</pre>
{% endif %}

<form method="post">
  <table class="form">
    {{ form }}
  </table>
  <ul>
      <strong>{% trans 'Note' %}:</strong>
      <li>
        {% blocktrans %}Every User you create here,
        is a superuser how can do everything!{% endblocktrans %}
      </li>
      <li>
        {% blocktrans %}After you have created the first user,
        you can login and create normal user, using{% endblocktrans %}
        <a href="/{{ admin_url_prefix }}/auth/user/">{% trans 'Django administration' %}</a>.
      </li>
  </ul>
  <input type="submit" value="{% trans 'Add user' %}" />
</form>

{% endblock %}
"""
def _create_or_update_superuser(user_data):
    """
    create a new user in the database.
    This function used in CreateUser() and in the SHA1-JS-Unittest!
    """
    print "Create/update a django superuser:"
    created = False
    try:
        user = User.objects.get(username=user_data["username"])
    except User.DoesNotExist:
        user = User.objects.create_user(
            user_data["username"], user_data["email"], user_data["password"]
        )
        created = True
    else:
        # Set a new password for a existing user
        user.set_password(user_data["password"])

    user.is_staff = True
    user.is_active = True
    user.is_superuser = True
    user.first_name = user_data.get("first_name", "")
    user.last_name = user_data.get("last_name", "")
    user.email = user_data.get("email", "")
    user.save()
    if created:
        print _("creaded a new User, OK")
    else:
        print _("update a existing User, OK")


class CreateUserForm(forms.ModelForm):
    """
    form for input the username, used in auth.login()
    """
    class Meta:
        model = User
        fields=("username", "first_name", "last_name", "email", "password")


class CreateUser(BaseInstall):
    def view(self):
        """
        Display the user form.
        """
        self._redirect_execute(self.create_user)
        return self._render(create_user_template)

    def create_user(self):
        # Change the help_text, because there is a URL in the default text
        CreateUserForm.base_fields['password'].help_text = ""

        if self.request.method == 'POST':
            user_form = CreateUserForm(self.request.POST)
            if user_form.is_valid():
                user_data = user_form.cleaned_data
                _create_or_update_superuser(user_data)
        else:
            user_form = CreateUserForm()

        self.context["form"] = user_form.as_table()
        self.context["admin_url_prefix"] = settings.ADMIN_URL_PREFIX



def create_user(request):
    """
    4. create or update a superuser
    """
    return CreateUser(request).start_view()


