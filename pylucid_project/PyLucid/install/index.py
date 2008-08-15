
"""
The index view
 - generate the _install section menu

TODO: rewrite _get_members
"""

import inspect

from PyLucid.settings import INSTALL_COOKIE_NAME
from PyLucid import install as install_package
from PyLucid.install.BaseInstall import BaseInstall
from PyLucid.tools.content_processors import render_string_template

from django.http import HttpResponse


def run_method(request, module_name, method_name, url_args):
    """
    run a _install method
    """
    from_name = ".".join(["PyLucid.install", module_name])
    module_object = __import__(from_name, {}, {}, [method_name])

    unbound_method = getattr(module_object, method_name)

    return unbound_method(request, *url_args)


def _get_members(obj, predicate, skip_name=[]):
    """
    get all members for generating the dynamic _install section menu
    - sort based on the first line of the docstring
    - renumber the docstring
    """
    result = []

    member_list = inspect.getmembers(obj, predicate)
    member_list = [i[0] for i in member_list]
    for member_name in member_list:
        if member_name.startswith("_"):
            # Skip all "secret" members.
            continue

        if member_name in skip_name:
            continue

        member_obj = getattr(obj, member_name)

        doc = member_obj.__doc__
        if doc:
            doc = doc.strip()
            doc = doc.splitlines()[0]
        else:
            doc = member_obj.__name__

        result.append((doc, member_name))

    result.sort()

    for no,data in enumerate(result):
        doc, name = data
        doc = "%s. %s" % (no+1, doc.lstrip("1234567890."))
        result[no] = {"doc": doc, "name": name}

    return result

LOGOUT_TEMPLATE = """
{% extends "install_base.html" %}
{% block content %}
<h1>{% trans 'Log out' %}</h1>

<h3>{% trans 'You logged out.' %}</h3>
<p><a href="{% url PyLucid.install.index.menu . %}">{% trans 'continue' %}</a></p>
<p>
{% trans 'You should disable the _install section!' %}<br />
{% trans 'Set "ENABLE_INSTALL_SECTION = False" in your settings.py' %}
</p>

{% endblock %}
"""

MENU_TEMPLATE = """
{% extends "install_base.html" %}
{% block content %}
<h1>{% trans 'menu' %}</h1>
<ul>
{% for item in module_list %}
    <li><h2>{{ item.doc }}</h2>
    <ul>
    {% for sub_item in item.views %}
        <li>
            <a href="{% url PyLucid.install.index.menu . %}/{{ item.name }}/{{ sub_item.name }}/">{{ sub_item.doc }}</a>
        </li>
    {% endfor %}
    </ul>
    </li>
{% endfor %}
</ul>
{% endblock %}
"""
class Index(BaseInstall):
    def view(self):
        """
        Generate and display the install section menu
        """
        menu_data = {}

        module_list = _get_members(
            obj=install_package, predicate=inspect.ismodule,
            skip_name=install_package.SKIP_MODULES
        )
        for no, module_data in enumerate(module_list):
            module_name = module_data["name"]

            module_obj = getattr(install_package, module_name)
            members = _get_members(
                obj=module_obj, predicate=inspect.isfunction,
                skip_name=[]
            )

            module_list[no]["views"] = members

        self.context["module_list"] = module_list

        # Do not display the "back to menu" link
        self.context["no_menu_link"] = True

        return self._render(MENU_TEMPLATE)

    def logout(self):
        """
        Delete the instpass cookie, so the user is logout.
        """
        self.context["no_menu_link"] = True # no "back to menu" link
        html = render_string_template(LOGOUT_TEMPLATE, self.context)
        response = HttpResponse(html)
        response.set_cookie(INSTALL_COOKIE_NAME, value="")
        return response


def menu(request):
    "Display the _install section main menu"
    return Index(request).start_view()


def logout(request, *args):
    "logout from the _install section"
    return Index(request).logout()











