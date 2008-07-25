
"""
4. some tests
"""

import os, cgi, sys, time

from django.conf import settings

from django import forms
from django.core import management
from django.core.cache import cache

from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.system.response import SimpleStringIO



#______________________________________________________________________________

class CacheBackendTest(BaseInstall):
    def _print_infoline(self, txt):
        print
        print "_"*80
        print txt
        print "-"*80

    def _test_cache(self):
        """
        Test the cache backend.
        """
        if settings.CACHE_BACKEND.startswith("dummy"):
            return
        self._print_infoline(
            "Test cache backend '%s':" % settings.CACHE_BACKEND
        )
        cache_key = "cache test"
        content = "A cache test content..."
        cache_timeout = 50
        print "Save into cache with key '%s'." % cache_key
        cache.set(cache_key, content, cache_timeout)
        print "Try to get the saved content from the cache."
        cached_content = cache.get(cache_key)
        if cached_content == None:
            print " * Get None back. Cache didn't work!"
            return
        elif cached_content==content:
            print " * Cache works fine ;)"
        else:
            # Should never appears
            print " * Error! Cache content not the same!"

        print "Try to delete the cache entry."
        cache.delete(cache_key)
        cached_content = cache.get(cache_key)
        if cached_content == None:
            print "OK, entry deleted."
        else:
            print "Error: entry not deleted!"


    def _verbose_try_import(self, module_name):
        """
        try to import the given >module_name< and print information.
        """
        try:
            __import__(module_name)
        except ImportError, msg:
            print "The module '%s' is not available. (%s)" % (module_name, msg)
        else:
            print "The module '%s' is available." % module_name

    def _print_tempdir_info(self):
        """
        Try to write temp files into the default system temp directory.
        """
        def write_test(file_path):
            f = file(file_path, "w")
            f.write("Test if PyLucid can write into the temp directory.")
            f.close()
            os.remove(file_path)

        host = self.request.META.get("HTTP_HOST", "").replace(".", "_")
        if host:
            suffix = "_" + host
        else:
            suffix = ""

        test_filename = "PyLucid_test%s.txt" % suffix

        from tempfile import gettempdir
        tempdir = gettempdir()
        print "The system default temp dir is: '%s'" % tempdir
        print

        #______________________________________________________________________
        # Try if we can make files directly into the temp directory:

        test_fn = os.path.join(tempdir, test_filename)
        try:
            write_test(test_fn)
        except OSError, msg:
            print "Error write the test file '%s': %s" % (test_fn, msg)
            print "You can't use the filesystem caching backend :("
            return
        else:
            print "Write a test file '%s' allowed, ok." % test_fn
            useable_dir = tempdir

        #______________________________________________________________________
        # Try if we can use a subdirectory:

        test_dir = os.path.join(tempdir, "PyLucid_cache" + suffix)
        try:
            if not os.path.isdir(test_dir):
                # test only if not exists (os.rmdir failed in the past?)
                os.makedirs(test_dir)

            # Try to write a temp file
            test_fn = os.path.join(test_dir, test_filename)
            write_test(test_fn)
            try:
                os.rmdir(test_dir)
            except:
                # don't care: only important we can create directory/files ;)
                pass
        except OSError, msg:
            print "Error using the sub directory '%s': %s" % (test_dir, msg)
        else:
            print "Using a sub directory '%s' allowed, ok." % test_dir
            useable_dir = test_dir

        print (
            "\n"
            "You can use the filesystem caching backend!\n"
            "You should insert the following line into your settings.py"
            " to enable this:\n"
            "CACHE_BACKEND = 'file://%s'"
        ) % useable_dir

    def view(self):
        self._redirect_execute(self.print_info)
        return self._simple_render(
            headline="Available cache backend test"
        )

    def print_info(self):
        self._test_cache()

        self._print_infoline("Tests for the memcache backend:")
        self._verbose_try_import("cmemcache")
        self._verbose_try_import("memcache")

        self._print_infoline("Tests for the filesystem caching backend:")
        self._print_tempdir_info()


def cache_backend_test(request):
    """
    1. Available cache backend test
    """
    return CacheBackendTest(request).start_view()


#______________________________________________________________________________

class InspectDB(BaseInstall):
    def view(self):
        self._redirect_execute(self._inspectdb)
        return self._simple_render(headline="inspectdb")

    def _inspectdb(self):
        management.call_command('inspectdb')

def inspectdb(request):
    """
    1. inspect the database
    """
    return InspectDB(request).start_view()

#______________________________________________________________________________

class SQLInfo(BaseInstall):
    def view(self):
        self._redirect_execute(self.print_info)
        return self._simple_render(
            headline="SQL create Statements from the current models"
        )

    def print_info(self):
        from django.db.models import get_apps

        app_list = get_apps()
#        output.append("App list: %s" % app_list)

        from django.core.management import sql
        from django.core.management.color import no_style

        def print_out(app, method_name):
            method = getattr(sql, method_name)
            try:
                output = method(app, no_style())
            except:
                # sql_custom takes no stype... why?
                output = method(app)
            if output==[]:
                return
            print "--\n-- %s:\n--" % method_name
            for line in output:
                print line

        for app in app_list:
            print "--\n--",
            print "_"*77
            print "-- %s\n--" % app.__name__

            print_out(app, "sql_create")
            print_out(app, "sql_custom")
            print_out(app, "sql_indexes")

def sql_info(request):
    "2. SQL info"
    return SQLInfo(request).start_view()

#______________________________________________________________________________

info_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>Info</h1>
<ul>
    <li><a href="#app_info">apps/models list</a></li>
    <li><a href="#db_info">db info</a></li>
    <li><a href="#settings">settings</a></li>
    <li><a href="#user_info">user info</a></li>
    <li><a href="#environ">os.environ</a></li>
    <li><a href="#request_meta">request.META</a></li>
    <li><a href="#request">request objects</a></li>
    <li><a href="#request_context">request context</a></li>
</ul>

<a name="app_info"></a>
<a href="#top">&#x5E; top</a>
<h2>apps/models list</h2>
<ul>
{% for app in apps_info %}
    <li>{{ app.name }}</li>
    <ul>
    {% for model in app.models %}
        <li>{{ model }}</li>
    {% endfor %}
    </ul>
{% endfor %}
</ul>

<a name="db_info"></a>
<a href="#top">&#x5E; top</a>
<h2>db info</h2>
<dl>
{% for item in db_info %}
  <dt>{{ item.0 }}</dt>
  <dd>{{ item.1 }}</dd>
{% endfor %}
</dl>

<a name="settings"></a>
<a href="#top">&#x5E; top</a>
<h2>current settings</h2>
<dl>
{% for item in current_settings %}
  <dt>{{ item.0 }}</dt>
  <dd><pre>{{ item.1|pprint }}</pre></dd>
{% endfor %}
</dl>

<a name="user_info"></a>
<a href="#top">&#x5E; top</a>
<h2>user info (request.user)</h2>
<dl>
{% for item in user_info %}
  <dt>{{ item.0 }}</dt>
  <dd><pre>{{ item.1|pprint }}</pre></dd>
{% endfor %}
</dl>

<a name="environ"></a>
<a href="#top">&#x5E; top</a>
<h2>os.environ:</h2>
<ul>
{% for item in environ %}
    <li>{{ item.0 }}: {{ item.1|escape }}</li>
{% endfor %}
</ul>

<a name="request_meta"></a>
<a href="#top">&#x5E; top</a>
<h2>request meta:</h2>
<ul>
{% for item in request_meta %}
    <li>{{ item.0 }}: {{ item.1|escape }}</li>
{% endfor %}
</ul>

<a name="request"></a>
<a href="#top">&#x5E; top</a>
<h2>request objects:</h2>
<ul>
{% for item in objects %}
    <li>{{ item }}</li>
{% endfor %}
</ul>

<a name="request_context"></a>
<a href="#top">&#x5E; top</a>
<h2>request context:</h2>
<p><pre>{{ request_context|pprint }}</pre></p>

{% endblock %}
"""
class Info(BaseInstall):
    def view(self):
        from django.conf import settings
#        from PyLucid.db import DB_Wrapper
#        import sys
#        db = DB_Wrapper(sys.stderr)#request.page_msg)
#        db_info = [
#            ("API", "%s v%s" % (db.dbapi.__name__, db.dbapi.__version__)),
#            ("Server Version", "%s (%s)" % (db.server_version, db.RAWserver_version)),
#            ("paramstyle", db.paramstyle),
#            ("placeholder", db.placeholder),
#            ("table prefix", db.tableprefix),
#        ]

        #______________________________________________________________________
        # apps/models list

        from django.db.models import get_apps, get_models

        apps_info = []
        for app in get_apps():
            models = [model._meta.object_name for model in get_models(app)]
            apps_info.append({
                    "name": app.__name__,
                    "models": models,
            })

        self.context["apps_info"] = apps_info

        #______________________________________________________________________
        # os.environ + request.META

        def get_list(obj):
            l = [(k,v) for k,v in obj.iteritems()]
            l.sort()
            return l

        self.context["environ"] = get_list(os.environ)
        self.context["request_meta"] = get_list(self.request.META)

        #______________________________________________________________________
        # request objects

        self.context["objects"] = []
        for item in dir(self.request):
            if not item.startswith("__"):
                self.context["objects"].append("request.%s" % item)

        #______________________________________________________________________
        # settings

        self.context["current_settings"] = self._get_obj_infos(settings)

        #______________________________________________________________________
        # user info + request context

        if "django.contrib.sessions.middleware.SessionMiddleware" in \
                                                    settings.MIDDLEWARE_CLASSES:
            self.context["user_info"] = self._get_obj_infos(self.request.user)

            from django.template import RequestContext
            self.context["request_context"] = RequestContext(self.request)

        # Importand: This page_msg output would be used in the unitest
        # tests.install_section.TestInstallSection.test_page_msg !
        self.page_msg("some information for developers:")

        return self._render(info_template)

    def _get_obj_infos(self, obj):
        """
        shared method to get a list of all relevant attributes from the given
        object.
        """
        info = []
        for obj_name in dir(obj):
            if obj_name.startswith("_"):
                continue

            try:
                current_obj = getattr(obj, obj_name)
            except Exception, e:
                etype = sys.exc_info()[0]
                info.append(
                    (obj_name, "[%s: %s]" % (etype, cgi.escape(str(e))))
                )
                continue

            if not isinstance(current_obj, (basestring, int, tuple, bool, dict)):
                #~ print ">>>Skip:", obj_name, type(current_obj)
                continue
            info.append((obj_name, current_obj))
        info.sort()
        return info

def info(request):
    """
    3. Display some information (for developers)
    """
    return Info(request).start_view()


#______________________________________________________________________________

url_info_template = """
{% extends "install_base.html" %}
{% block content %}
<h1>URL Info for '{{ domain }}':</h1>
<table>
{% for item in url_info %}
    <tr>
        <td>{{ item.0|escape }}</td>
        <td>{{ item.1|escape }}</td>
    </tr>
{% endfor %}
</table>
{% endblock %}
"""
class URL_Info(BaseInstall):
    def view(self):
#        from django.contrib.sites.models import Site
        from PyLucid.urls import urls

        self.context["url_info"] = urls

#        current_site = Site.objects.get_current()
#        domain = current_site.domain
#        self.context["domain"] = domain

        return self._render(url_info_template)

def url_info(request):
    """
    4. Display the current used urlpatterns
    """
    return URL_Info(request).start_view()

#______________________________________________________________________________

class PythonEvalForm(forms.Form):
    """
    django newforms
    """
    codeblock = forms.CharField(
        widget=forms.widgets.Textarea(attrs={"rows":10, "style": "width: 95%;"})
    )
    object_access = forms.BooleanField(required=False)

access_deny = """
{% extends "install_base.html" %}
{% block content %}
<h2>Access Error:</h2>
<h3>Python Webshell is disabled.</h3>
<p>
    You must enable this features in your settings.py!
</p>
{% endblock %}
"""
python_input_form = """
{% extends "install_base.html" %}
{% block content %}
Execute code with Python v{{ sysversion }}:<br />

<form method="post">
    {{ PythonEvalForm }}
    <input value="execute" name="execute" type="submit">
</form>
{% if output %}
<fieldset><legend>executed in {{ duration|stringformat:".1f" }}ms:</legend>
    <pre>{{ output }}</pre>
</fieldset>
{% endif %}
<p>
    With 'Object access' you can use every object binded to 'self'.<br />
    Use 'print dir(self)' to print out a list.<br />
    A usefull object are: 'self.request'
</p>
<br />
{% endblock %}
"""
def _execute_codeblock(codeblock, globals):
    code = compile(codeblock, "<stdin>", "exec", 0, 1)

    locals = {}
    exec code in globals, locals

class EvilEval(BaseInstall):
    def view(self):
        from PyLucid.settings import INSTALL_EVILEVAL
        if not INSTALL_EVILEVAL:
            # Feature is not enabled.
            return self._render(access_deny)

        if "codeblock" in self.request.POST:
            # Form has been sended
            init_values = self.request.POST.copy()
        else:
            # Requested the first time -> insert a init codeblock
            init_values = {
                "codeblock": (
                    "# sample code\n"
                    "for i in xrange(5):\n"
                    "    print 'This is cool', i"
                ),
            }

        eval_form = PythonEvalForm(init_values)
        self.context.update({
            "sysversion": sys.version,
            "PythonEvalForm": eval_form.as_p(),
        })

        if "codeblock" in self.request.POST and eval_form.is_valid():
            # a codeblock was submited and the form is valid -> run the code
            codeblock = eval_form.cleaned_data["codeblock"]
            codeblock = codeblock.replace("\r\n", "\n") # Windows

            if eval_form.cleaned_data["object_access"] == True:
                globals = {"self": self}
            else:
                globals = {}

            start_time = time.time()
            try:
                self._redirect_execute(
                    _execute_codeblock, codeblock, globals
                )
            except:
                import traceback
                self.context["output"] += traceback.format_exc()

            self.context["duration"] = (time.time() - start_time) * 1000
            self.context["output"] = cgi.escape(self.context["output"])

        return self._render(python_input_form)

def evileval(request):
    """
    5. a Python web-shell
    """
    return EvilEval(request).start_view()


