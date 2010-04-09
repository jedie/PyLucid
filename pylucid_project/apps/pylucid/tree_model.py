# encoding: utf-8

"""
    PyLucid - Tree Model/Manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a tree of the cms pages, who are orginised in a parent-model.
    usefull for the main menu and the sitemap.

    Based on code by Marc 'BlackJack' Rintsch
    see: http://www.python-forum.de/topic-10852.html (de)


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: 2008-11-13 12:53:39 +0100 (Do, 13 Nov 2008) $
    $Rev: 1792 $
    $Author: JensDiemer $

    :copyleft: 2007-2010 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class MenuNode(object):
    def __init__(self, id, data=None, parent=None):
        self.id = id
        self.data = data
        self.parent = parent
        self.subnodes = []
        self.active = False  # the complete path back to root
        self.current = False # current node in main menu?
        self.visible = True  # Seen in main menu?

        self.level = None # The level count, starts with 0
        self.first = False # Is the first node in the current level
        self.last = False # Is the last node in the current level

    def css_class(self):
        """
        returns a css class string, for: ... class="{{ node.css_class }}"
        So it's not needed to add a few {% if %} template statements. 
        """
        class_names = "level_%s" % self.level
        if self.active:
            class_names += " active"
        if self.current:
            class_names += " current"
        if self.first:
            class_names += " first"
        if self.last:
            class_names += " last"
        return class_names

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

    def get_absolute_url(self):
        """ absolute url *without* language code (without domain/host part) """
        data = self.data

        if self.parent:
            parent_shortcut = self.parent.get_absolute_url()
            return parent_shortcut + data["slug"] + "/"
        else:
            return "/" # root node

    def __repr__(self):
        if self.id == None:
            return "Root MenuNode object"
        return repr(self.data)





class TreeGenerator(object):
    def __init__(self, items, skip_no_parent=False):
        """
        Load the tree with all queryset items.
        Use skip_no_parent if the tree has "holes": e.g.: Filtered not accessible items.
        """
        self.related_objects = [] # List of added related objects

        # Create a dict with all pages as nodes
        self.nodes = dict((n["id"], MenuNode(n["id"], n))
                          for n in items)

        # Create the root node
        self.root = MenuNode(id=None)
        self.nodes[None] = self.root

        if items:
            # built the node tree
            for node_data in items:
                parent_id = node_data["parent"]
                try:
                    parent = self.nodes[parent_id]
                except KeyError:
                    if skip_no_parent == True:
                        # Skip item if parent does not exist.
                        continue
                    else:
                        raise

                parent.add(self.nodes[node_data["id"]])

            # add level number to all nodes and mark first/last nodes
            self.setup_nodes()

    def get_first_nodes(self, nodes=None):
        """ return a list of all 'top' nodes (all root subnodes) """
        return self.root.subnodes
        if nodes == None:
            nodes = self.root.subnodes

        for node in nodes:
            if node.visible:
                return nodes

        for node in nodes:
            if node.subnodes:
                nodes2 = self.get_first_nodes(node.subnodes)
                if nodes2:
                    return nodes2

    def setup_nodes(self, nodes=None, level=0):
        """ add level number to all nodes and mark first/last nodes """
        if nodes == None:
            nodes = self.root.subnodes

        nodes[0].first = True
        nodes[-1].last = True

        for node in nodes:
            node.level = level
            if node.subnodes:
                self.setup_nodes(node.subnodes, level + 1)

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
            nodes = self.root.subnodes

        print "_" * 79
        print "Tree model debug:"
        debug1(nodes)
        print "-" * 79
        print "Only visible nodes:"
        debug2(nodes)
        print "-" * 79

    def add_related(self, queryset, ids, field, attrname):
        """ Attach related objects from a queryset """
        lookup_kwargs = {"%s__in" % field: ids}
        #print "lookup_kwargs:", lookup_kwargs
        related_objects = queryset.filter(**lookup_kwargs).select_related()
        #print "related objects:", related_objects

        # Attach objects to the related node
        for related_object in related_objects:
            parent_field = getattr(related_object, field)
            parent_id = parent_field.id
            parent_node = self.nodes[parent_id]
            setattr(parent_node, attrname, related_object)

        # append the attribute name into self.related_objects list
        self.related_objects.append(attrname)


    def add_missing_related_objects(self, queryset, attrname):
        """ Adding related object items, if not all attached. """
        # Generate a id list of all menu entries witch has no related object
        ids = [
            id for id, node in self.nodes.items()
            if node.visible and id != None and not hasattr(node, attrname)
        ]
        if not ids: # All menu items has related objects entries
            return None

        # Add all missing related object from given queryset
        self.add_related(queryset, ids, field="pagetree", attrname="pagemeta")
        return ids


    def add_pagemeta(self, request):
        """ add all PageMeta objects into tree """
        # import here -> import-loop
        from pylucid_project.apps.pylucid.models import PageMeta, Language

        current_lang = request.PYLUCID.current_language
        default_lang = Language.objects.get_or_create_default(request)

        # Generate a id list of all visible nodes 
        ids = [id for id, node in self.nodes.items() if node.visible and id != None]
        #print "Get pagemeta for: %r" % ids
        queryset = PageMeta.objects.filter(language=current_lang)

        # Add all pagemeta in current client language
        self.add_related(queryset, ids, field="pagetree", attrname="pagemeta")

        # Add all missing PageMeta in system default language
        queryset = PageMeta.objects.filter(language=default_lang)
        ids = self.add_missing_related_objects(queryset, attrname="pagemeta")
        #print "Missing PageMeta added: %r" % ids

        # Add at least all missing PageMeta, no matter what language
        if ids is not None: # Skip, if all PageMeta exist previously
            queryset = PageMeta.objects.all()
            self.add_missing_related_objects(queryset, attrname="pagemeta")


    def slice_menu(self, min, max, parent=None):
        """
        Slice the visible menu items.
        """
        #print "slice menu - min: %r - max: %r" % (min, max)
        def remove_max(max, parent):
            """ Remove subnodes, if there are too deep. """
            for node in parent.subnodes:
                if node.level >= max - 1:
                    node.subnodes = [] # remove subnodes
                elif node.subnodes:
                    remove_max(max, parent=node)

        if max > 0: # skip if max == 0
            remove_max(max, parent=self.root)

        def reassign_root(min, parent):
            """ Reassign the root node, for cut the menu tree start point. """
            for node in parent.subnodes:
                if node.active != True: # Walk only through active nodes
                    continue

                if node.level < min - 1:
                    self.root = node
                    if node.level <= min - 2:
                        # Found the needed menu start point.
                        return

                if node.subnodes: # go deeper to find the menu start point.
                    reassign_root(min, parent=node)

        if min > 1: # reassign menu start point only if needed
            reassign_root(min, parent=self.root)

#        self.debug()


    def set_current_node(self, id, delete_hidden=True):
        """
        setup all node visible item for main menu template. 
        """
        self.deactivate_all()
        nodes = self.nodes
        current_node = nodes[id]
        current_node.activate()
        current_node.current = True

        if delete_hidden:
            # Remove all not visible items, because they not needed anymore.
            def build_tree(nodes):
                new_node_list = []
                for node in nodes:
                    if node.visible:
                        new_node_list.append(node)
                        if node.subnodes:
                            node.subnodes = build_tree(node.subnodes)
                return new_node_list

            self.root.subnodes = build_tree(self.root.subnodes)

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

    def iter_flat_list(self, nodes=None):
        """
        returns a flat list of all visible pages with the level info.
        """
        if nodes == None:
            nodes = self.root.subnodes

        for node in nodes:
            if node.visible:
                yield node
            if node.subnodes:
                for node in self.iter_flat_list(nodes=node.subnodes):
                    if node.visible:
                        yield node







class TreeManager(models.Manager):
    def get_tree(self):
        data = self.model.objects.all()
        tree = TreeGenerator(data)
        return tree

class BaseTreeModel(models.Model):
    """ Base tree model used in PyLucidAdminPage and PageTree """
    objects = TreeManager()

    parent = models.ForeignKey("self", null=True, blank=True, help_text="the higher-ranking father page")
    position = models.SmallIntegerField(default=0,
        help_text="ordering weight for sorting the pages in the menu.")

    def clean_fields(self, exclude):
        """
        check if parent is the same entry: child <-> parent loop
        """
        if "parent" not in exclude and self.parent is not None and self.pk == self.parent.pk:
            message_dict = {"parent": (_("child-parent loop error!"),)}
            raise ValidationError(message_dict)

    class Meta:
        abstract = True
        # FIXME: It would be great if we can order by get_absolute_url()
        ordering = ("id", "position")


