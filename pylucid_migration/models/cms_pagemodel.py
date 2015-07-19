
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.db.models.base import Model

from cms.models import Page


class PageProxyModel(Page):
    """
    Used to add a "normal" django admin model page
    """
    def save(self):
        # print("mro:", PageProxyModel.__mro__)
        """
        <class 'pylucid_migration.models.cms_pagemodel.PageProxyModel'>
        <class 'cms.models.pagemodel.Page'>
        <class 'mptt.models.MPTTModel'>
        <class 'django.db.models.base.Model'>
        <class 'object'>
        """
        Model.save(self)

    class Meta:
        proxy = True
        app_label="cms" # Important for db LegacyRouter()
        verbose_name = _('page (proxy model)')
        verbose_name_plural = _('pages (proxy model)')




class PagePatchModel(models.Model):
    """
    Used to change data in cms.Page model.

    Using the origin model will not easily work, because:
     * created_by & changed_by will set in Page.save() from _thread_locals.users
     * creation_date & changed_date used auto_now / auto_now_add and can't be temporary disabled :(
    """
    created_by = models.CharField(max_length=70)
    changed_by = models.CharField(max_length=70)
    creation_date = models.DateTimeField()
    changed_date = models.DateTimeField()

    class Meta:
        app_label="cms" # Important for db LegacyRouter()
        db_table = "cms_page" # XXX: How to get this from origin model ?!?