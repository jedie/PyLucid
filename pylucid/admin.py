

from cms.models.pagemodel import Page

from reversion_compare.helpers import patch_admin


# Patch django-cms Page Model to add reversion-compare functionality:
patch_admin(Page)
