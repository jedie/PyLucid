# coding:utf-8

from pprint import pprint

import test_tools # before django imports!

from django.conf import settings

from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest import unittest_base

from pylucid_project.tests.test_tools.pylucid_test_data import TestSites
from pylucid_project.tests.test_tools import basetest
from pylucid.models import PageTree, PageMeta

#settings.PYLUCID.I18N_DEBUG = True

class TreeModelTest(basetest.BaseUnittest):
    """
    Low level test for pylucid.models.PageTree + pylucid.tree_model.TreeGenerator
    """
    def _flat_tree_generator(self, nodes):
        for node in nodes:
            indent = "*" * (node.level + 1)
            pagetree = node.db_instance
            yield "%-4s (id:%s) %s" % (indent, pagetree.pk, pagetree.slug)
#            print indent, node.id, "v:", node.visible, node
#
#            for related_object_name in self.related_objects:
#                if hasattr(node, related_object_name):
#                    print indent, "   * %r: %r" % (related_object_name, getattr(node, related_object_name))

            if node.subnodes:
                for item in self._flat_tree_generator(node.subnodes):
                    yield item

    def _print_flat_tree(self, tree):
        nodes = tree.get_first_nodes()
        flat_tree_generator = self._flat_tree_generator(nodes)
        pprint(list(flat_tree_generator))

    def assertTree(self, tree, should_data):
        nodes = tree.get_first_nodes()
        flat_tree_generator = self._flat_tree_generator(nodes)
        for no, is_item in enumerate(flat_tree_generator):
            self.failUnlessEqual(is_item, should_data[no])

    def test_all(self):
        user = AnonymousUser()
        # returns a TreeGenerator instance with all accessable page tree instance
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
#        self._print_flat_tree(tree)

        self.assertTree(tree, should_data=
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             u'**   (id:6) 2-2-subpage',
             u'***  (id:7) 2-2-1-subpage',
             u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )

    def test_permitViewGroup1(self):
        """
        Test filtering permitViewGroup.
        """
        test_group1 = Group(name="test group1")
        test_group1.save()

        page = PageTree.objects.get(id=6)
        page.permitViewGroup = test_group1
        page.save()

        test_group2 = Group(name="test group2")
        test_group2.save()

        page = PageTree.objects.get(id=7)
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
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             #u'**   (id:6) 2-2-subpage',   # permitViewGroup == test_group1
             #u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             #u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )

        # --------------------------------------------------------------------
        # Test as Superuser:
        # He can see all pages

        user = self._get_user(usertype="superuser")
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             u'**   (id:6) 2-2-subpage', # permitViewGroup == test_group1
             u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
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
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             #u'**   (id:6) 2-2-subpage',   # permitViewGroup == test_group1
             #u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             #u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )

        # Add user to "test group1"
        user.groups.add(test_group1)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             u'**   (id:6) 2-2-subpage', # permitViewGroup == test_group1
             #u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )

        # Add user to "test group2", too.
        user.groups.add(test_group2)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             u'**   (id:6) 2-2-subpage', # permitViewGroup == test_group1
             u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )

        # Put user *only* in "test group2"
        user.groups.remove(test_group1)
        tree = PageTree.objects.get_tree(user)
        #tree.debug()
        #self._print_flat_tree(tree)
        self.assertTree(tree, should_data=
            [u'*    (id:1) 1-rootpage',
             u'**   (id:2) 1-1-subpage',
             u'**   (id:3) 1-2-subpage',
             u'*    (id:4) 2-rootpage',
             u'**   (id:5) 2-1-subpage',
             #u'**   (id:6) 2-2-subpage',   # permitViewGroup == test_group1
             #u'***  (id:7) 2-2-1-subpage', # permitViewGroup == test_group2
             #u'***  (id:8) 2-2-2-subpage',
             u'*    (id:9) 3-pluginpage']
        )


if __name__ == "__main__":
    # Run this unitest directly
    unittest_base.direct_run(__file__)
