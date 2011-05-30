# coding:utf-8

import os


if __name__ == "__main__":
    # run all unittest directly
    os.environ['DJANGO_SETTINGS_MODULE'] = "pylucid_project.settings"


from django import forms
from django.forms.util import flatatt

from pylucid_project.tests.test_tools import basetest


class TestForm(forms.Form):
    foo = forms.CharField(max_length=100)


class FlatattPatchTest(basetest.BaseUnittest):
    """
    Test flatatt Monkey-patch (done in pylucid test.test_tools.test_runner)
    """
    TEST_ATTRS = {"m":5, "a":1, "b":2, "c":3, "z":8, 1:1, 2:2}

    def test_function(self):
        output = flatatt(self.TEST_ATTRS)
        self.failUnlessEqual(u' 1="1" 2="2" a="1" b="2" c="3" m="5" z="8"', output)

    def test_widget_patch(self):
        test_widget = forms.TextInput()
        self.failUnlessEqual(
            test_widget.render("foo", "bar", attrs=self.TEST_ATTRS),
            '<input 1="1" 2="2" a="1" b="2" c="3" m="5" name="foo" type="text" value="bar" z="8" />'
        )

    def test_forms_patch(self):
        form = TestForm()
        foo_field = form["foo"]
        self.failUnlessEqual(
            foo_field.label_tag(attrs=self.TEST_ATTRS),
            '<label for="id_foo" 1="1" 2="2" a="1" b="2" c="3" m="5" z="8">Foo</label>'
        )


if __name__ == "__main__":
    # Run all unittest directly
    from django.core import management

    tests = __file__
#    tests = "apps.pylucid_admin.tests.PyLucidPluginsTest.test_access_admin_views"

    management.call_command('test', tests,
#        verbosity=0,
        verbosity=1,
        failfast=True
    )
