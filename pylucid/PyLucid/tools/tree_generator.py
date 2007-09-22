#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid.tools.tree_generator.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a tree of the cms pages, who are orginised in a parent-model.
    usefull for the main menu and the sitemap.

    Original code by Marc 'BlackJack' Rintsch
    see: http://www.python-forum.de/topic-10852.html (de)


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer and Marc Rintsch.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


class MenuNode(object):
    def __init__(self, id, data={}, parent=None):
        self.id = id
        self.data = data
        self.parent = parent
        self.subnodes = list()
        self.visible = False

    def add(self, node):
        """
        add a new sub node.
        """
        self.subnodes.append(node)
        node.parent = self

    def activate(self):
        """
        activate self + all sub nodes + the parent node
        """
        self.visible = True
        # Activate all subnodes:
        for subnode in self.subnodes:
            subnode.visible = True
        # activate the parent node
        if self.parent is not None:
            self.parent.activate()

    def _get_current_entry(self, level):
        current_entry = self.data.copy()
        current_entry["level"] = level
        return current_entry

    def to_dict(self, level=0):
        """
        built the tree dict of all activated nodes and insert a level info
        """
        current_entry = self._get_current_entry(level)

        subitems = [subnode.to_dict(level + 1)
                    for subnode in self.subnodes
                    if subnode.visible]
        if subitems:
            current_entry['subitems'] = subitems

        return current_entry

    def get_flat_list(self, level=0):
        """
        genrate a flat list for all visible pages and insert a level info
        """
        flat_list=[]

        current_entry = self._get_current_entry(level)
        flat_list.append(current_entry)

        for subnode in self.subnodes:
            if subnode.visible:
                flat_list += subnode.get_flat_list(level + 1)

        return flat_list




class TreeGenerator(object):
    def __init__(self, flat_data):
        # Create a dict with all pages as nodes
        self.nodes = dict((n['id'], MenuNode(n['id'], n))
                          for n in flat_data)

        # Create the root node
        self.root = MenuNode(id=None)
        self.nodes[None] = self.root

        # built the node tree
        for node_data in flat_data:
            id = node_data['id']
            parent = node_data['parent']
            try:
                self.nodes[parent].add(self.nodes[id])
            except KeyError:
                # If the user is not logged in and there exist a secret area,
                # we have some page how assign to a hidden page. All hidden
                # pages are filtered with the django orm. So we can' assign
                # a page how are a parent of a hidden page
                continue

    def to_dict(self):
        """
        built the tree dict of all visible nodes.
        """
        return self.root.to_dict()['subitems']

    def activate_all(self):
        """
        make all nodes visible (for a sitemap)
        """
        for node in self.nodes.itervalues():
            node.visible = True

    def deactivate_all(self):
        """
        makes all nodes invisible.
        """
        for node in self.nodes.itervalues():
            node.visible = False

    def activate(self, id):
        """
        make one node visible. (for the main menu)
        """
        self.nodes[id].activate()

    #___________________________________________________________________________

    def get_menu_tree(self, id=None):
        """
        generate a tree dirct for the main menu.
        If id==None: Only the top pages are visible!
        """
        self.deactivate_all()
        self.activate(id)
        return self.to_dict()

    def get_sitemap_tree(self):
        """
        generate a tree wih all nodes for a sitemap
        """
        self.activate_all()
        return self.to_dict()

    def get_flat_list(self):
        """
        returns a flat list of all visible pages with the level info.
        """
        return self.root.get_flat_list()[1:]


def test_generator(tree, display_result):
    #
    # Sitemap.
    #
    def verbose(result, no):
        if not display_result:
            return
        print '-' * 40
        print "*** No. %s ***" % no
        pprint(result)

    result = tree.get_sitemap_tree()
    must_be = [{'id': 1,
          'level': 1,
          'name': '1. AAA',
          'parent': None,
          'subitems': [{'id': 2,
                        'level': 2,
                        'name': '1.1. BBB',
                        'parent': 1,
                        'subitems': [{'id': 4,
                                      'level': 3,
                                      'name': '1.2.1. CCC',
                                      'parent': 2},
                                     {'id': 5,
                                      'level': 3,
                                      'name': '1.2.2. CCC',
                                      'parent': 2}]},
                       {'parent': 1, 'id': 3, 'name': '1.2. BBB', 'level': 2}]},
         {'id': 6,
          'level': 1,
          'name': '2. AAA',
          'parent': None,
          'subitems': [{'parent': 6, 'id': 7, 'name': '2.1. BBB', 'level': 2}]}]
    verbose(result, 1)
    if result != must_be:
        print '-' * 40
        print "*** ERROR 1 ***"
        pprint(result)


    #
    # Keinen Punkt aktivieren
    #   => Nur die Punkte der ersten Ebene sind zu sehen.
    #
    result = tree.get_menu_tree()
    must_be = [{'parent': None, 'id': 1, 'name': '1. AAA', 'level': 1},
            {'parent': None, 'id': 6, 'name': '2. AAA', 'level': 1}]
    verbose(result, 2)
    if result != must_be:
        print '-' * 40
        print "*** ERROR 2 ***"
        pprint(result)


    #
    # Menüpunkt 2 aktivieren.
    #
    result = tree.get_menu_tree(2)
    must_be = [{'id': 1,
          'level': 1,
          'name': '1. AAA',
          'parent': None,
          'subitems': [{'id': 2,
                        'level': 2,
                        'name': '1.1. BBB',
                        'parent': 1,
                        'subitems': [{'id': 4,
                                      'level': 3,
                                      'name': '1.2.1. CCC',
                                      'parent': 2},
                                     {'id': 5,
                                      'level': 3,
                                      'name': '1.2.2. CCC',
                                      'parent': 2}]},
                       {'parent': 1, 'id': 3, 'name': '1.2. BBB', 'level': 2}]},
         {'parent': None, 'id': 6, 'name': '2. AAA', 'level': 1}]
    verbose(result, 3)
    if result != must_be:
        print '-' * 40
        print "*** ERROR 3 ***"
        pprint(result)


    #
    # Menüpunkt 6 aktivieren.
    #
    result = tree.get_menu_tree(6)
    must_be = [{'parent': None, 'id': 1, 'name': '1. AAA', 'level': 1},
         {'id': 6,
          'level': 1,
          'name': '2. AAA',
          'parent': None,
          'subitems': [{'parent': 6, 'id': 7, 'name': '2.1. BBB', 'level': 2}]}]
    verbose(result, 4)
    if result != must_be:
        print '-' * 40
        print "*** ERROR 4 ***"
        pprint(result)


    tree.activate_all()
    result = tree.get_flat_list()
    must_be = [
        {'id': 1, 'level': 1, 'name': '1. AAA', 'parent': None},
        {'id': 2, 'level': 2, 'name': '1.1. BBB', 'parent': 1},
        {'id': 4, 'level': 3, 'name': '1.2.1. CCC', 'parent': 2},
        {'id': 5, 'level': 3, 'name': '1.2.2. CCC', 'parent': 2},
        {'id': 3, 'level': 2, 'name': '1.2. BBB', 'parent': 1},
        {'id': 6, 'level': 1, 'name': '2. AAA', 'parent': None},
        {'id': 7, 'level': 2, 'name': '2.1. BBB', 'parent': 6}
    ]
    verbose(result, 5)
    if result != must_be:
        print '-' * 40
        print "*** ERROR 5 ***"
        pprint(result)



if __name__ == "__main__":
    from pprint import pprint

    data = [
        {'id': 1, 'parent': None, 'name': '1. AAA'},
        {'id': 2, 'parent': 1,    'name': '1.1. BBB'},
        {'id': 3, 'parent': 1,    'name': '1.2. BBB'},
        {'id': 4, 'parent': 2,    'name': '1.2.1. CCC'},
        {'id': 5, 'parent': 2,    'name': '1.2.2. CCC'},
        {'id': 6, 'parent': None, 'name': '2. AAA'},
        {'id': 7, 'parent': 6,    'name': '2.1. BBB'},
    ]

    print "test..."

    tree = TreeGenerator(data)
#    test_generator(tree, display_result=False)
    test_generator(tree, display_result=True)

    print "\nEND"

