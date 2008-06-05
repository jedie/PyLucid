#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.models.Preference

    OBSOLETE
    TODO: Must be complete rewritten!

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import tests
from PyLucid.models import Plugin


#class TestPreference(tests.TestCase):
class TestPreference:
    """
    Tests with test data. (_install dump data deleted and test data inserted)
    """
    def setUp(self):
        " Delete all preferences "
        self.test_value = {"i": 1, "s": "test", "t": (1,2,3), "l": [1,2,3]}

        Preference.objects.all().delete()

        self.assertEqual(Preference.objects.all().count(), 0)

    def test_create(self):
        """
        Create a new preference entry without a default value.
        """
        Preference(
            plugin = None, name = "test1", description = "",
            value = self.test_value
        ).save()

        p = Preference.objects.get(name = "test1")
        self.assertEqual(p._value       , p._default_value)
        self.assertEqual(p.value        , self.test_value)
        self.assertEqual(p.default_value, self.test_value)

        p.value = u"new value"
        p.save()
        p = Preference.objects.get(name = "test1")
        self.assertEqual(p.value, u"new value")
        # The default should be the old value:
        self.assertEqual(p.default_value, self.test_value)

    def test_diff_default(self):
        """
        Create a new preference entry with different value <-> default_value
        """
        Preference(
            plugin = None, name = "test1", description = "",
            value = self.test_value, default_value = [1,2,3]
        ).save()

        p = Preference.objects.get(name = "test1")
        self.assertEqual(p.value        , self.test_value)
        self.assertEqual(p.default_value, [1,2,3])

        p.value = u"new value"
        p.save()
        p = Preference.objects.get(name = "test1")
        self.assertEqual(p.value, u"new value")
        # The default should be the old value:
        self.assertEqual(p.default_value, [1,2,3])

    def test_cache(self):
        """
        Test if the cache works.
        If the cache work: We get everytime the same python object back.
        If it dosn't work: Everytime pickle.loads() build a new python object.
        """
        Preference(
            plugin = None, name = "test1", description = "",
            value = self.test_value
        ).save()
        p = Preference.objects.get(name = "test1")

        value1 = p.value
        value2 = p.value
        self.assertEqual(
            value1 is value2, True,
            "The caching seems not to work for 'value'"
        )

    def test_plugin_assoc(self):
        """
        Test the association between plugins and preferences to it.

        Important: The test use values with the same name but different
        plugin associations.
        """
        def test_data():
            """
            a simple iterator for creating test data
            """
            count = 0
            for plugin_name in (None, "p1", "p2"):
                for pref_name in ("A", "B"):
                    count += 1
                    pref_desc = "desc %s" % count
                    pref_value = (plugin_name, pref_name, count,)
                    yield plugin_name, pref_name, pref_desc, pref_value

        # Create Plugins and insert preferences
        plugins = {None:None}
        for plugin_name, pref_name, pref_desc, pref_value in test_data():
            #print plugin_name, pref_name, pref_value
            if plugin_name not in plugins:
                # Create a new test plugin entry
                plugin = Plugin(plugin_name=plugin_name)
                plugin.save()
                plugins[plugin_name] = plugin
            else:
                # Use a old plugin directly from the dict
                plugin = plugins[plugin_name]

            # Insert the preference pref_value
            p = Preference(
                plugin = plugin,
                name = pref_name,
                description = pref_desc,
                value = pref_value,
            )
            p.save()

        # Compare the inserted data
        for plugin_name, pref_name, pref_desc, pref_value in test_data():
            plugin = plugins[plugin_name]
            try:
                p = Preference.objects.get(plugin = plugin, name = pref_name)
            except Preference.DoesNotExist, e:
                msg = (
                    "Can't get prefereces plugin name: '%s' pref.name: '%s'"
                    " - original error: %s"
                ) % (plugin_name, pref_name, e)
                raise AssertionError(msg)

            self.assertEqual(p.description, pref_desc)
            self.assertEqual(p.value, pref_value)



#class TestPreferenceDump(tests.TestCase):
class TestPreferenceDump:
    """
    Tests with the _install dump inserted in the test database.
    """
    def test_install_dump(self):
        """
        Test the _install dump.

        The defaults dict must be updated if the dump changed !
        """
        # Check that every page has default properties.
        defaults = {
            "index page": 1,
            "auto shortcuts": True,
        }

        preferences = Preference.objects.all()
        self.assertEqual(len(preferences), len(defaults))

        # compare the database data with the defaults dict
        for p in preferences:
            default_value = defaults[p.name]
            self.assertEqual(default_value, p.value)
            self.assertEqual(default_value, p.default_value)

            # The pickled version must be different ;)
            self.assertNotEqual(p._value, p.value)
            self.assertNotEqual(p._default_value, p.default_value)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
