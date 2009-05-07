# coding:utf-8

import test_tools # before django imports!

from django.conf import settings
from django.test import TransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site

from django_tools.unittest.unittest_base import BaseTestCase, direct_run

from pylucid.models import PageTree
from test_tools import pylucid_test_data


class PageContentTest(BaseTestCase, TransactionTestCase):   
    def test_page(self):
#       template = Template.objects.get_or_create(
#            name = new_template_name,
#            defaults = {
#                "content": template.content,
#                "creation_date": template.createtime,
#                "last_changed": template.lastupdatetime,
#            }
#        )
#        

#                
#        first_page = PageTree(
#            site = Site.objects.get_current()
#        )
#        first_page.save(request)
        pylucid_test_data.create_pylucid_test_data()
        
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=("PyLucid", "PyLucid - Log in"),
            must_not_contain=("error", "Traceback")
        )
        
#    def test_summary_page(self):
#        self.login(usertype="superuser")
#        response = self.client.get(self.ADMIN_SITE_URL)
#        self.assertResponse(response,
#            must_contain=("PyLucid", "Page trees", "Page contents"),
#            must_not_contain=("Log in", "error", "Traceback")
#        )


if __name__ == "__main__":
    # Run this unitest directly
    direct_run(__file__)