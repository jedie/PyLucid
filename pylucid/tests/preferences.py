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

from datetime import datetime

import tests
from PyLucid.models import Plugin, Preference

from django.contrib.auth.models import User


TEST_DICT1 = {"i": 1, "s": "test", "t": (1,2,3), "l": [1,2,3]}
TEST_DICT2 = {"FooBar": None}


class TestPreferences(tests.TestCase):
    """
    Test the preference model directly.
    """
    fixtures = [] # Use no test fixtures (empy database)

    def setUp(self):
        self.test_plugin = Plugin.objects.get_or_create(
            package_name = "test_package_name",
            plugin_name = "test_plugin",
            active = True,
        )[0]

    def test_create(self):
        """
        Create a new preference entry and check the data
        """
        # The p.id tests failed, if the database not empty
        self.assertEqual(Preference.objects.all().count(), 0)

        p = Preference.objects.create(
            plugin = self.test_plugin,
            comment = "one",
            data = TEST_DICT1,
            user = None
        )
        self.assertEqual(p.get_data(), TEST_DICT1)
        self.assertEqual(p.id, 1)

        # insert a second entry for the same plugin
        p = Preference.objects.create(
            plugin = self.test_plugin,
            comment = "two",
            data = TEST_DICT2,
            user = None
        )
        self.assertEqual(p.get_data(), TEST_DICT2)
        self.assertEqual(p.id, 2)


class TestPluginPreferences(tests.TestCase):
    """
    Test the preferences API throu the plugin model.
    """
    fixtures = [] # Use no test fixtures (empy database)

    def setUp(self):
        self.test_plugin = Plugin.objects.get_or_create(
            package_name = "test_package_name",
            plugin_name = "test_plugin",
            active = True,
        )[0]

    def test_default_pref(self):
        """
        Test the default preference api
        """
        self.assertEqual(self.test_plugin.default_pref, None)

        pref_obj1 = self.test_plugin.set_default_preference(
            comment = "default pref",
            data = TEST_DICT1,
            user = None,
        )
        self.failUnless(isinstance(self.test_plugin.default_pref, Preference))
        self.assertEqual(pref_obj1.get_data(), TEST_DICT1)

        # set a new default preferences
        pref_obj2 = self.test_plugin.set_default_preference(
            comment = "default pref",
            data = TEST_DICT2,
            user = None,
        )
        self.assertEqual(pref_obj2.get_data(), TEST_DICT2)

        # It sound not be created a new preferences entry, the existing should
        # be updated.
        self.assertEqual(pref_obj1.id, pref_obj2.id)


    def test_create(self):
        """
        Test normal preference instances
        """
        # Create
        pref_obj = self.test_plugin.add_preference(
            comment = "pref one",
            data = TEST_DICT1,
            user = None,
        )
        self.failUnless(isinstance(pref_obj, Preference))
        self.assertEqual(pref_obj.get_data(), TEST_DICT1)

        # Test plugin.get_preference
        id = pref_obj.id
        pref_obj = self.test_plugin.get_preference(id = id)
        self.failUnless(isinstance(pref_obj, Preference))
        self.assertEqual(pref_obj.get_data(), TEST_DICT1)

        # Check pref entries 1
        pref_entries = Preference.objects.filter(plugin=self.test_plugin)
        self.assertEqual(len(pref_entries), 1)
        # Check pref entries 2
        pref_entries = self.test_plugin.get_all_preferences()
        self.assertEqual(len(pref_entries), 1)

        # Add a new preference entry
        pref_two_obj = self.test_plugin.add_preference(
            comment = "pref two",
            data = TEST_DICT2,
            user = None,
        )
        self.failUnless(isinstance(pref_two_obj, Preference))
        self.assertEqual(pref_two_obj.get_data(), TEST_DICT2)

        # Check pref entries 1
        pref_entries = Preference.objects.filter(plugin=self.test_plugin)
        self.assertEqual(len(pref_entries), 2)
        # Check pref entries 2
        pref_entries = self.test_plugin.get_all_preferences()
        self.assertEqual(len(pref_entries), 2)

    def test_update(self):
        """
        Update a exiting preferences entry
        """
        # Create
        pref_obj1 = self.test_plugin.add_preference(
            comment = "pref one",
            data = TEST_DICT1,
            user = None
        )
        self.failUnless(isinstance(pref_obj1, Preference))
        self.assertEqual(pref_obj1.get_data(), TEST_DICT1)

        id = pref_obj1.id
        pref_obj2 = self.test_plugin.get_preference(id = id)
        pref_obj2.set_data(TEST_DICT2, user=None)
        pref_obj2.save()

        pref_obj3 = self.test_plugin.get_preference(id = id)
        self.assertEqual(pref_obj3.get_data(), TEST_DICT2)


    def test_user_assign(self):
        """
        Check user assign and timestamps
        """
        # Test Plugin.add_preference
        test_user1 = tests.create_user(**tests.TEST_USERS["superuser"])
        pref_obj = self.test_plugin.add_preference(
            comment = "pref one",
            data = TEST_DICT1,
            user = test_user1
        )
        self.assertEqual(pref_obj.createby, test_user1)
        self.assertEqual(pref_obj.lastupdateby, test_user1)
        createtime1 = pref_obj.createtime
        lastupdatetime1 = pref_obj.lastupdatetime

        # Test timestamps
        self.failUnless(createtime1 < datetime.now())
        self.failUnless(lastupdatetime1 < datetime.now())

        # Test Preferences.set_data
        test_user2 = tests.create_user(**tests.TEST_USERS["staff"])
        pref_obj.set_data(TEST_DICT2, user=test_user2)
        pref_obj.save()
        self.assertEqual(pref_obj.createby, test_user1)
        self.assertEqual(pref_obj.lastupdateby, test_user2)

        # Test timestamps
        self.failUnless(pref_obj.createtime == createtime1)
        self.failUnless(pref_obj.lastupdatetime > lastupdatetime1)



#
#
#class TestPreferenceOLD:
#
#    """
#    Tests with test data. (_install dump data deleted and test data inserted)
#    """
#
#    def setUp(self):
#        " Delete all preferences "
#        self.test_value = {"i": 1, "s": "test", "t": (1,2,3), "l": [1,2,3]}
#
#        Preference.objects.all().delete()
#
#        self.assertEqual(Preference.objects.all().count(), 0)
#
#    def test_create(self):
#        """
#        Create a new preference entry without a default value.
#        """
#        Preference(
#            plugin = None, name = "test1", description = "",
#            value = self.test_value
#        ).save()
#
#        p = Preference.objects.get(name = "test1")
#        self.assertEqual(p._value       , p._default_value)
#        self.assertEqual(p.value        , self.test_value)
#        self.assertEqual(p.default_value, self.test_value)
#
#        p.value = u"new value"
#        p.save()
#        p = Preference.objects.get(name = "test1")
#        self.assertEqual(p.value, u"new value")
#        # The default should be the old value:
#        self.assertEqual(p.default_value, self.test_value)
#
#    def test_diff_default(self):
#        """
#        Create a new preference entry with different value <-> default_value
#        """
#        Preference(
#            plugin = None, name = "test1", description = "",
#            value = self.test_value, default_value = [1,2,3]
#        ).save()
#
#        p = Preference.objects.get(name = "test1")
#        self.assertEqual(p.value        , self.test_value)
#        self.assertEqual(p.default_value, [1,2,3])
#
#        p.value = u"new value"
#        p.save()
#        p = Preference.objects.get(name = "test1")
#        self.assertEqual(p.value, u"new value")
#        # The default should be the old value:
#        self.assertEqual(p.default_value, [1,2,3])
#
#    def test_cache(self):
#        """
#        Test if the cache works.
#        If the cache work: We get everytime the same python object back.
#        If it dosn't work: Everytime pickle.loads() build a new python object.
#        """
#        Preference(
#            plugin = None, name = "test1", description = "",
#            value = self.test_value
#        ).save()
#        p = Preference.objects.get(name = "test1")
#
#        value1 = p.value
#        value2 = p.value
#        self.assertEqual(
#            value1 is value2, True,
#            "The caching seems not to work for 'value'"
#        )
#
#    def test_plugin_assoc(self):
#        """
#        Test the association between plugins and preferences to it.
#
#        Important: The test use values with the same name but different
#        plugin associations.
#        """
#        def test_data():
#            """
#            a simple iterator for creating test data
#            """
#            count = 0
#            for plugin_name in (None, "p1", "p2"):
#                for pref_name in ("A", "B"):
#                    count += 1
#                    pref_desc = "desc %s" % count
#                    pref_value = (plugin_name, pref_name, count,)
#                    yield plugin_name, pref_name, pref_desc, pref_value
#
#        # Create Plugins and insert preferences
#        plugins = {None:None}
#        for plugin_name, pref_name, pref_desc, pref_value in test_data():
#            #print plugin_name, pref_name, pref_value
#            if plugin_name not in plugins:
#                # Create a new test plugin entry
#                plugin = Plugin(plugin_name=plugin_name)
#                plugin.save()
#                plugins[plugin_name] = plugin
#            else:
#                # Use a old plugin directly from the dict
#                plugin = plugins[plugin_name]
#
#            # Insert the preference pref_value
#            p = Preference(
#                plugin = plugin,
#                name = pref_name,
#                description = pref_desc,
#                value = pref_value,
#            )
#            p.save()
#
#        # Compare the inserted data
#        for plugin_name, pref_name, pref_desc, pref_value in test_data():
#            plugin = plugins[plugin_name]
#            try:
#                p = Preference.objects.get(plugin = plugin, name = pref_name)
#            except Preference.DoesNotExist, e:
#                msg = (
#                    "Can't get prefereces plugin name: '%s' pref.name: '%s'"
#                    " - original error: %s"
#                ) % (plugin_name, pref_name, e)
#                raise AssertionError(msg)
#
#            self.assertEqual(p.description, pref_desc)
#            self.assertEqual(p.value, pref_value)
#
#
#
##class TestPreferenceDump(tests.TestCase):
#class TestPreferenceDump:
#    """
#    Tests with the _install dump inserted in the test database.
#    """
#    def test_install_dump(self):
#        """
#        Test the _install dump.
#
#        The defaults dict must be updated if the dump changed !
#        """
#        # Check that every page has default properties.
#        defaults = {
#            "index page": 1,
#            "auto shortcuts": True,
#        }
#
#        preferences = Preference.objects.all()
#        self.assertEqual(len(preferences), len(defaults))
#
#        # compare the database data with the defaults dict
#        for p in preferences:
#            default_value = defaults[p.name]
#            self.assertEqual(default_value, p.value)
#            self.assertEqual(default_value, p.default_value)
#
#            # The pickled version must be different ;)
#            self.assertNotEqual(p._value, p.value)
#            self.assertNotEqual(p._default_value, p.default_value)



if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
