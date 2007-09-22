#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.models.Preference

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


from setup_environment import setup, make_insert_dump
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=False
)

#______________________________________________________________________________
# Test:

import unittest

from PyLucid.models import Preference, Plugin



class TestPreference(unittest.TestCase):
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
            "The cahing seems not to work for 'value'"
        )

        default_value1 = p.default_value
        default_value2 = p.default_value
        self.assertEqual(
            default_value1 is default_value2, True,
            "The cahing seems not to work for 'default_value'"
        )


    def test_plugin_assoc(self):
        test_value1 = {"plugin": 1, "name": "test1"}
        test_value2 = {"plugin": 1, "name": "test2"}
        test_value3 = {"plugin": 2, "name": "test1"}
        test_value4 = {"plugin": 2, "name": "test2"}

        plugin1 = Plugin(plugin_name="plugin1")
        plugin1.save()
        Preference(
            plugin = plugin1, name = "test1", description = "",
            value = test_value1
        ).save()
        Preference(
            plugin = plugin1, name = "test2", description = "",
            value = test_value2
        ).save()

        plugin2 = Plugin(plugin_name="plugin2")
        plugin2.save()
        Preference(
            plugin = plugin2, name = "test1", description = "",
            value = test_value3
        ).save()
        Preference(
            plugin = plugin2, name = "test2", description = "",
            value = test_value4
        ).save()

        test = Preference.objects.all()
        self.assertEqual(len(test), 4)

        p = Preference.objects.get(plugin=plugin1, name="test1")
        self.assertEqual(p.value, test_value1)

        p = Preference.objects.get(plugin=plugin1, name="test2")
        self.assertEqual(p.value, test_value2)

        p = Preference.objects.get(plugin=plugin2, name="test1")
        self.assertEqual(p.value, test_value3)

        p = Preference.objects.get(plugin=plugin2, name="test2")
        self.assertEqual(p.value, test_value4)


    def test_install_dump(self):
        """
        Test the _install dump.
        This test must naturally update if the dump changed ;)
        """
        self.assertEqual(Preference.objects.all().count(), 0)

        # insert the _install dump:
        make_insert_dump(extra_verbose=False)

        self.assertEqual(Preference.objects.all().count(), 2)

        # Build a new dict, from the current _install dump:
#        for entry in Preference.objects.all():
#            print " "*11,
#            print '"%s": %s,' % (entry.name, entry.value)

        defaults = {
            "index page": 1,
            "auto shortcuts": True,
        }
        for name,value in defaults.iteritems():
            p = Preference.objects.get(name=name)
            self.assertEqual(p.value, value)
            self.assertNotEqual(p._value, value)
            self.assertEqual(p.default_value, value)
            self.assertNotEqual(p._default_value, value)




def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestPreference))
    return suite

if __name__ == "__main__":
    print
    print ">>> Unitest"
    print "_"*79
    unittest.main()
    sys.exit()