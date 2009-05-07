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
        pylucid_test_data.create_pylucid_test_data()
        
        response = self.client.get("/")
        self.assertResponse(response,
            must_contain=(
                '<a href="/firstpage/">first english page</a>',
                '<h1>The first test page!</h1>',
            ),
            must_not_contain=("Traceback",)#"error"),
        )


if __name__ == "__main__":
    # Run this unitest directly
    direct_run(__file__)