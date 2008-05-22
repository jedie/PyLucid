# -*- coding: utf-8 -*-

"""
    PyLucid.managers
    ~~~~~~~~~~~~~~

    The database models managers for PyLucid.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from django.db import models

from django.utils.translation import ugettext as _
from PyLucid.system.exceptions import AccessDenied, LowLevelError


class PageManager(models.Manager):
    """
    Manager for Page model.
    """

    class WrongShortcut(LookupError):
        """ URL string contained invalid shortcuts at the end. """
        pass
    
    @property
    def default_page(self):
        """ Return default "index" page """ 
        from PyLucid.models import Plugin
        try:
            preferences = Plugin.objects.get_preferences("system_settings")
            page_id = preferences["index_page"]
            return self.get(id__exact=page_id)
        except Exception, e:
            # The defaultPage-ID from the Preferences is wrong! Return first
            # page if anything exists.
            try:
                return self.all().order_by("parent", "position")[0]
            except IndexError, e:
                msg = _("Error getting a cms page.")
                raise LowLevelError(msg, e)

    def _check_permission_tree(self,page,test_fcn):
        """
        Check permissions of page and its parents. The second parameter
        test_fcn(page_object) is the test function which must return true or false
        corresponding to permssion to view specific page.
        """
        while page:
            if not test_fcn(page):
                return False
            page = page.parent
        return True

    def __check_publicView(self, page):
        """
        Return true/false if page permits anonymous view.
        """
        return page.permitViewPublic

    def __check_groupView(self, user_group_ids):
        """
        Return true/false if page permits anonymous view.
        """
        def check(page):
            if page.permitViewGroup == None:
                return True
            else:
                return page.permitViewGroup.id in user_group_ids
        return check
    

    def get_by_shortcut(self,url_shortcuts,user):
        """
        Returns a page object matching the shortcut. 

        PyLucid urls are build from the page shortcuts:
        domain.tld/shortcut1/shortcut2/. Only the last existing shortcut will
        be used. All other parts of the url are simply ignored.

        If url_shortcuts contains no shortcut -> Return the default page (stored in the
        Preference table).
        If a part of the url is wrong -> Raise WrongShortcut, with correct path in message
        If a anonymous user would get a permitViewPublic page -> Raise AccessDenied.
        If no matching page is found -> Raise Page.DoesNotExist

        TODO: Support user group based access control.
        """

        # /shortcut1/shortcut2/ -> ['shortcut1','shortcut2']
        shortcuts = url_shortcuts.strip("/").split('/')

        if shortcuts[0] == "":
            # No shortcuts return default_page
            return self.default_page
        
        # Check shortcuts in reversed order
        shortcuts.reverse()
        wrong_shortcut = False
        if not user.is_anonymous():
            user_groups = [x['id'] for x in user.groups.all().values('id')]
        for shortcut in shortcuts:
            try:
                page = self.select_related().get(shortcut__exact=shortcut)
            except self.model.DoesNotExist:
                wrong_shortcut = True
                continue            
            if user.is_anonymous():
                if not self._check_permission_tree(page,self.__check_publicView):
                    # the page or its parent is not viewable for anonymous user
                    raise AccessDenied
            elif not user.is_superuser:
                # Superuser can see all pages.
                if not self._check_permission_tree(page,self.__check_groupView(user_groups)):
                    # User is logged in. Check if page is restricted to user group
                    raise AccessDenied

            # Found an existing, viewable page
            if wrong_shortcut:
                # At least one of the shortcuts in the url was wrong -> raise
                raise self.WrongShortcut, page.get_absolute_url()
            return page
        # No right page found
        raise self.model.DoesNotExist

