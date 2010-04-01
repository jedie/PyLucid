# coding:utf-8

from pprint import pprint

import test_tools # before django imports!

from django.conf import settings

from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest_utils import unittest_base

from pylucid_project.tests.test_tools.pylucid_test_data import TestSites
from pylucid_project.tests.test_tools import basetest
from pylucid_project.apps.pylucid.models import PageTree, PageMeta

#settings.PYLUCID.I18N_DEBUG = True

class TreeModelTest(basetest.BaseUnittest):
    """
    Low level test for pylucid.models.PageTree + pylucid.tree_model.TreeGenerator
    """
    def _flat_tree_generator(self, tree):
        for node in tree.iter_flat_list():
            indent = "*" * (node.level + 1)
            yield "%-3s %s" % (indent, node.get_absolute_url())

    def _print_flat_tree(self, tree):
        flat_tree = self._flat_tree_generator(tree)
        pprint(list(flat_tree))

    def assertTree(self, tree, should_data):
        for no, is_item in enumerate(self._flat_tree_generator(tree)):
            self.failUnlessEqual(is_item, should_data[no])

    def test_all(self):
        user = AnonymousUser()
        # returns a TreeGenerator instance with all accessable page tree instance
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)

        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             u'**  /2-rootpage/2-2-subpage/',
             u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/',
             u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

    def test_permitViewGroup1(self):
        """
        Test filtering permitViewGroup.
        """
        test_group1 = Group(name="test group1")
        test_group1.save()

        page = PageTree.on_site.get(slug="2-2-subpage")
        page.permitViewGroup = test_group1
        page.save()

        test_group2 = Group(name="test group2")
        test_group2.save()

        page = PageTree.on_site.get(slug="2-2-1-subpage")
        page.permitViewGroup = test_group2
        page.save()

        # --------------------------------------------------------------------
        # Test as AnonymousUser:
        # He can see only pages with permitViewGroup==None

        user = AnonymousUser()
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             #u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             #u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             #u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

        # --------------------------------------------------------------------
        # Test as Superuser:
        # He can see all pages

        user = self._get_user(usertype="superuser")
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

        # --------------------------------------------------------------------
        # Test as normal user:
        # He can see all pages 

        # Test without any groups -> He can see only pages with permitViewGroup==None
        user = self._get_user(usertype="normal")
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             #u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             #u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             #u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

        # Add user to "test group1"
        user.groups.add(test_group1)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             #u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

        # Add user to "test group2", too.
        user.groups.add(test_group2)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )

        # Put user *only* in "test group2"
        user.groups.remove(test_group1)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*   /1-rootpage/',
             u'**  /1-rootpage/1-1-subpage/',
             u'**  /1-rootpage/1-2-subpage/',
             u'*   /2-rootpage/',
             u'**  /2-rootpage/2-1-subpage/',
             #u'**  /2-rootpage/2-2-subpage/', # permitViewGroup == test_group1
             #u'*** /2-rootpage/2-2-subpage/2-2-1-subpage/', # permitViewGroup == test_group2 
             #u'*** /2-rootpage/2-2-subpage/2-2-2-subpage/',
             u'*   /3-pluginpage/']
        )


if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)
