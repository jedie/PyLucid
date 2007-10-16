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
    group_id=None
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
    
    def activate_expanded(self, group_key, group_value):
        """
        enlarged the visible group.
        Same as 'activate', but makes only self node, sub nodes and parent node 
        visible, if data[group_key] == group_value
        """
        def conditional_activate(node):
            if node.data[group_key] == group_value:
                node.visible = True
            else:
                node.visible = False
        
        conditional_activate(self)
        for subnode in self.subnodes:
            conditional_activate(subnode)
            
        if self.parent is not None:
            conditional_activate(self.parent)
        

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
    
    def get_group(self, group_key, id):
        """
        activate a coherent group, which have the same value in the 'group_key'.
        """
        self.deactivate_all()
        
        node = self.nodes[id]
        group_value = node.data[group_key]

        # go to the first parent node how has a other group value:
        while 1:
            if node.parent== None:
                break
            node = node.parent
            if node.data[group_key] != group_value:
                break
        #print "first node with other group value:\n\t", node.data
        
        # activate all subnodes:
        for subnode in node.subnodes:
            subnode.activate_expanded(group_key, group_value)
#            if subnode.data[group_key] == group_value:
#                print "activate:", subnode.data
#                subnode.activate(activate_parent=False)
            
        # return the coherent group
        return node.to_dict()["subitems"]
        
        
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



#_______________________________________________________________________________
# MODULE TEST:



def _test_generator(tree, display_result):
    #
    # Sitemap.
    #
    def print_data(txt, data):
        print '-' * 40
        print "***** %s *****" % txt
        pprint(data)
        
    def check(result, must_be, no):
        failed = result != must_be
        if failed or display_result:
            txt = "No. %s - result:" % no
            print_data(txt, result)
        if failed:
            txt = "ERROR %s - must be:" % no
            print_data(txt, must_be)
            

        
    result = tree.get_sitemap_tree()
    must_be = [{'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None,
      'subitems': [{'group': 'two',
                    'id': 2,
                    'level': 2,
                    'name': '1.1. BBB',
                    'parent': 1},
                   {'group': 'two',
                    'id': 3,
                    'level': 2,
                    'name': '1.2. BBB',
                    'parent': 1,
                    'subitems': [{'group': 'two',
                                  'id': 4,
                                  'level': 3,
                                  'name': '1.2.1. CCC',
                                  'parent': 3},
                                 {'group': 'two',
                                  'id': 5,
                                  'level': 3,
                                  'name': '1.2.2. CCC',
                                  'parent': 3}]}]},
     {'group': 'one',
      'id': 6,
      'level': 1,
      'name': '2. DDD',
      'parent': None,
      'subitems': [{'group': 'two',
                    'id': 7,
                    'level': 2,
                    'name': '2.1. EEE',
                    'parent': 6},
                   {'group': 'two',
                    'id': 8,
                    'level': 2,
                    'name': '2.2. EEE',
                    'parent': 6}]}]
    check(result, must_be, no=1)


    #
    # No menu point activated
    #   => Display the first Level.
    #
    result = tree.get_menu_tree()
    must_be = [
        {'group': 'one', 'id': 1, 'level': 1, 'name': '1. AAA', 'parent': None},
        {'group': 'one', 'id': 6, 'level': 1, 'name': '2. DDD', 'parent': None}
    ]
    check(result, must_be, no=2)


    #
    # Activate the second menu point.
    #
    result = tree.get_menu_tree(2)
    must_be = [{'group': 'one',
      'id': 1,
      'level': 1,
      'name': '1. AAA',
      'parent': None,
      'subitems': [{'group': 'two',
                    'id': 2,
                    'level': 2,
                    'name': '1.1. BBB',
                    'parent': 1},
                   {'group': 'two',
                    'id': 3,
                    'level': 2,
                    'name': '1.2. BBB',
                    'parent': 1}]},
     {'group': 'one', 'id': 6, 'level': 1, 'name': '2. DDD', 'parent': None}]
    check(result, must_be, no=3)


    #
    # Activate the sixth menu point.
    #
    result = tree.get_menu_tree(6)
    must_be = [
        {'group': 'one', 'id': 1, 'level': 1, 'name': '1. AAA', 'parent': None},
         {'group': 'one',
          'id': 6,
          'level': 1,
          'name': '2. DDD',
          'parent': None,
          'subitems': [{'group': 'two',
                        'id': 7,
                        'level': 2,
                        'name': '2.1. EEE',
                        'parent': 6},
                       {'group': 'two',
                        'id': 8,
                        'level': 2,
                        'name': '2.2. EEE',
                        'parent': 6}]}]
    check(result, must_be, no=4)


    #
    # a flat list for all current activated pages
    #
    result = tree.get_flat_list()
    must_be = [
        {'group': 'one', 'id': 1, 'level': 1, 'name': '1. AAA', 'parent': None},
        {'group': 'one', 'id': 6, 'level': 1, 'name': '2. DDD', 'parent': None},
        {'group': 'two', 'id': 7, 'level': 2, 'name': '2.1. EEE', 'parent': 6},
        {'group': 'two', 'id': 8, 'level': 2, 'name': '2.2. EEE', 'parent': 6}
    ]
    check(result, must_be, no=5)


    #
    # generate a flat list from all pages
    #
    tree.activate_all()
    result = tree.get_flat_list()
    must_be = [
        {'group': 'one', 'id': 1, 'level': 1, 'name': '1. AAA', 'parent': None},
        {'group': 'two', 'id': 2, 'level': 2, 'name': '1.1. BBB', 'parent': 1},
        {'group': 'two', 'id': 3, 'level': 2, 'name': '1.2. BBB', 'parent': 1},
        {'group': 'two', 'id': 4, 'level': 3, 'name': '1.2.1. CCC', 'parent': 3},
        {'group': 'two', 'id': 5, 'level': 3, 'name': '1.2.2. CCC', 'parent': 3},
        {'group': 'one', 'id': 6, 'level': 1, 'name': '2. DDD', 'parent': None},
        {'group': 'two', 'id': 7, 'level': 2, 'name': '2.1. EEE', 'parent': 6},
        {'group': 'two', 'id': 8, 'level': 2, 'name': '2.2. EEE', 'parent': 6}
    ]
    check(result, must_be, no=6)
    
    
    #
    # a coherent group, which have the same value in the 'group_key'
    #
    result = tree.get_group(group_key="group", id=5)
    must_be = [
     {'group': 'two', 'id': 2, 'level': 1, 'name': '1.1. BBB', 'parent': 1},
     {'group': 'two',
      'id': 3,
      'level': 1,
      'name': '1.2. BBB',
      'parent': 1,
      'subitems': [{'group': 'two',
                    'id': 4,
                    'level': 2,
                    'name': '1.2.1. CCC',
                    'parent': 3},
                   {'group': 'two',
                    'id': 5,
                    'level': 2,
                    'name': '1.2.2. CCC',
                    'parent': 3}]}
    ]
    check(result, must_be, no=7)
    
    result = tree.get_group(group_key="group", id=8)
    must_be = [
        {'group': 'two', 'id': 7, 'level': 1, 'name': '2.1. EEE', 'parent': 6},
        {'group': 'two', 'id': 8, 'level': 1, 'name': '2.2. EEE', 'parent': 6}
    ]
    check(result, must_be, no=8)

    result = tree.get_group(group_key="parent", id=3)
    must_be = [
         {'group': 'two', 'id': 2, 'level': 1, 'name': '1.1. BBB', 'parent': 1},
         {'group': 'two', 'id': 3, 'level': 1, 'name': '1.2. BBB', 'parent': 1},
    ]
    check(result, must_be, no=9)
    

#_______________________________________________________________________________


if __name__ == "__main__":
    print "module test - START\n"
    from pprint import pprint

    data = [
        {'id': 1, 'parent': None, 'group': 'one', 'name': '1. AAA'},
        {'id': 2, 'parent': 1,    'group': 'two', 'name': '1.1. BBB'},
        {'id': 3, 'parent': 1,    'group': 'two', 'name': '1.2. BBB'},
        {'id': 4, 'parent': 3,    'group': 'two', 'name': '1.2.1. CCC'},
        {'id': 5, 'parent': 3,    'group': 'two', 'name': '1.2.2. CCC'},
        {'id': 6, 'parent': None, 'group': 'one', 'name': '2. DDD'},
        {'id': 7, 'parent': 6,    'group': 'two', 'name': '2.1. EEE'},
        {'id': 8, 'parent': 6,    'group': 'two', 'name': '2.2. EEE'},
    ]
    print "Source data:"
    pprint(data)

    tree = TreeGenerator(data)
    _test_generator(tree, display_result=False)
#    _test_generator(tree, display_result=True)

    print "\nmodule test - END"

