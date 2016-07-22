
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import override, ugettext_lazy as _

from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool


@toolbar_pool.register
class DesignDemoToolbar(CMSToolbar):
    def populate(self):
        admin_menu = self.toolbar.get_or_create_menu('design_demo', _('switch template'))
        for path, name in settings.CMS_TEMPLATES:
            url = reverse('switch_template', kwargs={"page_id":self.request.current_page.pk, "template":path})
            admin_menu.add_link_item("%s (%s)" % (name, path), url=url)
