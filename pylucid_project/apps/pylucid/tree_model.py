# encoding: utf-8

"""
    Tree Model/Manager
    ~~~~~~~~~~~~~~~~~~

    Generate a tree of the cms pages, who are orginised in a parent-model.
    usefull for the main menu and the sitemap.

    Based on code by Marc 'BlackJack' Rintsch
    see: http://www.python-forum.de/topic-10852.html (de)

    TODO: move this to django-tools


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-11-13 12:53:39 +0100 (Do, 13 Nov 2008) $
    $Rev: 1792 $
    $Author: JensDiemer $

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

if __name__ == "__main__":
    # run unittest for this module
    import sys
    import test_tools # before django imports!
    from django.core import management
    management.call_command('test', "test_TreeModel.TreeModelTest")
    sys.exit()

from django.db import models


class MenuNode(object):
    def __init__(self, id, db_instance=None, parent=None):
        self.id = id
        self.db_instance = db_instance
        self.parent = parent
        self.subnodes = []
        self.active = False  # the complete path back to root
        self.current = False # current node in main menu?
        self.visible = True  # Seen in main menu?
        self.level = None

    def add(self, node):
        """
        add a new sub node.
        """
        self.subnodes.append(node)
        node.parent = self

    def activate(self):
        """
        activate self + all sub nodes + the parent nodes
        """
        #print " *** activate: %r" % self
        self.visible = True
        self.active = True

        # Activate all subnodes:
        for subnode in self.subnodes:
            subnode.visible = True

        # activate the parent node
        if self.parent is not None:
            self.parent.activate()

    def __repr__(self):
        if self.id == None:
            return "Root MenuNode object"
        return repr(self.db_instance)

#    def activate_expanded(self, group_key, group_value):
#        """
#        enlarged the visible group.
#        Same as 'activate', but makes only self node, sub nodes and parent node 
#        visible, if data[group_key] == group_value
#        """
#        def conditional_activate(node):
#            if node.data[group_key] == group_value:
#                node.visible = True
#            else:
#                node.visible = False
#
#        conditional_activate(self)
#        for subnode in self.subnodes:
#            conditional_activate(subnode)
#
#        if self.parent is not None:
#            conditional_activate(self.parent)


#    def _get_current_entry(self, level):
#        if self.id == None:
#            # root item
#            return self
#
#        self.db_instance.level = level
#        self.db_instance.active = self.active
#        return self.db_instance

#    def to_dict(self, level=0):
#        """
#        built the tree dict of all active nodes and insert a level info
#        """
#        current_entry = self._get_current_entry(level)
#
#        subnodes = [subnode.to_dict(level + 1)
#                    for subnode in self.subnodes
#                    if subnode.visible]
#        if subnodes:
#            current_entry.subnodes = subnodes
#
#        return current_entry
#
#    def get_flat_list(self, level=0):
#        """
#        genrate a flat list for all visible pages and insert a level info
#        """
#        flat_list = []
#
#        current_entry = self._get_current_entry(level)
#        flat_list.append(current_entry)
#
#        for subnode in self.subnodes:
#            if subnode.visible:
#                flat_list += subnode.get_flat_list(level + 1)
#
#        return flat_list




class TreeGenerator(object):
    def __init__(self, queryset):
        self.related_objects = [] # List of added related objects

        # Create a dict with all pages as nodes
        self.nodes = dict((n.id, MenuNode(n.id, n))
                          for n in queryset)

        # Create the root node
        self.root = MenuNode(id=None)
        self.nodes[None] = self.root

        # built the node tree
        for node_data in queryset:
            if node_data.parent:
                parent_id = node_data.parent.id
            else:
                parent_id = None

            self.nodes[parent_id].add(self.nodes[node_data.id])

        # add level number to all nodes
        self.setup_level()

    def get_first_nodes(self):
        """ return a list of all 'top' nodes (all root subnodes) """
        return self.root.subnodes

    def setup_level(self, nodes=None, level=0):
        """ add level number to all nodes """
        if nodes == None:
            nodes = self.get_first_nodes()
        for node in nodes:
            node.level = level
            if node.subnodes:
                self.setup_level(node.subnodes, level + 1)

    def debug(self, nodes=None):
        def debug1(nodes):
            for node in nodes:
                indent = "   " * (node.level - 1)
                print indent, node.id, "v:", node.visible, node

                for related_object_name in self.related_objects:
                    if hasattr(node, related_object_name):
                        print indent, "   * %r: %r" % (related_object_name, getattr(node, related_object_name))

                if node.subnodes:
                    debug1(node.subnodes)

        def debug2(nodes):
            for node in nodes:
                if node.visible:
                    indent = "   " * (node.level - 1)
                    print indent, node.id, "a:", node.active, node
                if node.subnodes:
                    debug2(node.subnodes)

        if nodes == None:
            nodes = self.get_first_nodes()

        print "_" * 79
        print "Tree model debug:"
        debug1(nodes)
        print "-" * 79
        print "Only visible nodes:"
        debug2(nodes)
        print "-" * 79

    def add_related(self, queryset, field, attrname):
        """ Attach related objects from querset to all visible nodes. """

        # Generate a id list of all visible nodes 
        ids = [id for id, node in self.nodes.items() if node.visible and id != None]

        lookup_kwargs = {"%s__in" % field: ids}
        #print "lookup_kwargs:", lookup_kwargs
        related_objects = queryset.filter(**lookup_kwargs)
        #print "related objects:", related_objects

        # Attach objects to the related node
        for related_object in related_objects:
            parent_field = getattr(related_object, field)
            parent_id = parent_field.id
            parent_node = self.nodes[parent_id]
            setattr(parent_node, attrname, related_object)

        # append the attribute name into self.related_objects list
        self.related_objects.append(attrname)

    def set_current_node(self, id):
        """
        setup all node visible item for main menu template. 
        """
        self.deactivate_all()
        current_node = self.nodes[id]
        current_node.activate()
        current_node.current = True

#    def to_dict(self):
#        """
#        built the tree dict of all visible nodes.
#        """
#        return self.root.to_dict().subnodes

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

#    def activate(self, id):
#        """
#        make one node visible. (for the main menu)
#        """
#        self.nodes[id].activate()

#    def get_menu_tree(self, id=None):
#        """
#        generate a tree dirct for the main menu.
#        If id==None: Only the top pages are visible!
#        """
#        self.deactivate_all()
#        self.activate(id)
#        if id:
#            self.nodes[id].data["is_current"] = True
#        return self.to_dict()
#
#    def get_sitemap_tree(self):
#        """
#        generate a tree wih all nodes for a sitemap
#        """
#        self.activate_all()
#        return self.to_dict()
#
#    def get_flat_list(self):
#        """
#        returns a flat list of all visible pages with the level info.
#        """
#        return self.root.get_flat_list()[1:]




class TreeManager(models.Manager):
    def get_tree(self):
        data = self.model.objects.all()
        print data
        tree = TreeGenerator(data)
        return tree

class BaseTreeModel(models.Model):
    """ Base tree model used in PyLucidAdminPage and PageTree """
    objects = TreeManager()

    parent = models.ForeignKey("self", null=True, blank=True, help_text="the higher-ranking father page")
    position = models.SmallIntegerField(default=0,
        help_text="ordering weight for sorting the pages in the menu.")

    class Meta:
        abstract = True
        # FIXME: It would be great if we can order by get_absolute_url()
        ordering = ("id", "position")


