# coding: utf-8


"""
    PyLucid base models
    ~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2009-2012 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from django.contrib import messages
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools.middlewares import ThreadLocal


class PermissionsBase(object):
    """
    Shared model methods around view/edit permissions.
    Used in PageTree and PageMeta
    """
    def validate_permit_group(self, attribute, exclude, message_dict):
        """
        Prevents that a unprotected page created below a protected page.
        validate self.permitViewGroup and self.permitEditGroup
        """
        if attribute in exclude:
            return

        parent_page = self.recusive_attribute(attribute)
        if parent_page is None:
            # So parent page back to root has set a permission group
            return

        # we are below a protected page -> Check if permission group is the same.
        parent_page_group = getattr(parent_page, attribute)
        own_group = getattr(self, attribute)

        if parent_page_group == own_group:
            # permission is the same -> ok
            return

        # Add validation error message
        msg = _(
            "Error: Parent page <strong>%(parent_page)s</strong> used <strong>%(parent_page_group)s</strong>!"
            " You must used <strong>%(parent_page_group)s</strong> for this page, too."
        ) % {
            "parent_page": parent_page.get_absolute_url(),
            "parent_page_group": parent_page_group,
        }
        message_dict[attribute] = (mark_safe(msg),)

    def check_sub_page_permissions(self, attributes, exclude, message_dict, queryset):
        """
        Warn user if PageTree permissions mismatch with sub pages.
        
        self.check_sub_page_permissions(
            ("permitViewGroup", "permitEditGroup"),
            exclude, message_dict, queryset
        )
        
        """
        request = ThreadLocal.get_current_request()
        if request is None:
            # Check only if we are in a request
            return

        attributes2 = []
        for attribute in attributes:
            if attribute not in exclude and attribute not in message_dict:
                # ...and don't check if ValidationError exist for this field
                attributes2.append(attribute)

        if not attributes2:
            return

        sub_pages = queryset.only(*attributes2)

        for attribute in attributes2:
            own_permission = getattr(self, attribute)
            for sub_page in sub_pages:
                sub_page_permission = getattr(sub_page, attribute)
                if sub_page_permission != own_permission:
                    msg = _(
                        "Permission mismatch:"
                        " current %(attribute)s is set to '%(own_permission)s'"
                        " and sub page '%(slug)s' used '%(sub_permission)s'."
                        " This may be ok."
                    ) % {
                        "slug": sub_page.get_absolute_url(),
                        "attribute": attribute,
                        "own_permission": own_permission,
                        "sub_permission": sub_page_permission,
                    }
                    messages.warning(request, msg)
