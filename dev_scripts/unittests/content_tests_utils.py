#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid content tests utilities
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Some shared test utilities for testing the content of PyLucid componets.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2008 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""


### Uncomment only for self-test!!!
###----------------------------------------------------------------------------
#from setup_environment import setup
#setup(
#    path_info=False, extra_verbose=False,
#    syncdb=True, insert_dump=True,
#    install_plugins=True
#)
####---------------------------------------------------------------------------

import os, webbrowser, traceback, tempfile, unittest, pprint, re

from django.test.client import Client

from PyLucid.models import Page, User, Template, Style, Markup
from PyLucid.tools.Diff import display_plaintext_diff


# vebose test?
#DEBUG = True
DEBUG = False

# The global test user for many testes.
# creaded in TestUserModels().testcreate_or_update_superuser()
TEST_USERNAME = "unittest"
TEST_USER_EMAIL = "a_test@email-adress.org"
TEST_PASSWORD = "test"

# A user with a unusable password
# creaded in TestUserModels().test_unusable_password()
TEST_UNUSABLE_USER = "unittest2"


# A simple regex to get all html links out of a page content
HREF_RE = re.compile('<a href="(.+?)".*?>(.+?)</a>')


# Bug with Firefox under Ubuntu.
# http://www.python-forum.de/topic-11568.html
webbrowser._tryorder.insert(0, 'epiphany') # Use Epiphany, if installed.


# Variable to save if the browser is opend in the past.
ONE_DEBUG_DISPLAYED = False


# A example page tree for some tests:
TEST_PAGES = [{
    'name': '1_AAA',
    'subitems': [
        {'name': '1_1_BBB'},
        {'name': '1_2_BBB',
            'subitems': [
                {'name': '1_2_1_CCC'},
                {'name': '1_2_2_CCC'}
            ]
        }
    ]
}, {
    'name': '2_DDD',
    'subitems': [
        {'name': '2_1_EEE'},
        {'name': '2_2_EEE'}
    ]
}]
# A list of shortcuts (from the example page tree)
TEST_PAGES_SHORTCUTS = [
    u'/1_AAA/',
    u'/1_AAA/1_1_BBB/',
    u'/1_AAA/1_2_BBB/',
    u'/1_AAA/1_2_BBB/1_2_1_CCC/',
    u'/1_AAA/1_2_BBB/1_2_2_CCC/',
    u'/2_DDD/',
    u'/2_DDD/2_1_EEE/',
    u'/2_DDD/2_2_EEE/'
]




def debug_response(response, one_browser_traceback=True, msg="", \
                                                            display_tb=True):
    """
    Display the response content with a error reaceback in a webbrowser.
    TODO: We should delete the temp files after viewing!
    """
    if one_browser_traceback:
        # Only one traceback should be opend in the browser.
        global ONE_DEBUG_DISPLAYED
        if ONE_DEBUG_DISPLAYED:
            # One browser instance started in the past, skip this error
            return
        else:
            # Save for the next traceback
            ONE_DEBUG_DISPLAYED = True

    content = response.content

    stack = traceback.format_stack(limit=3)[:-1]
    stack.append(msg)
    if display_tb:
        print
        print "debug_response:"
        print "-"*80
        print "\n".join(stack)
        print "-"*80

    stack_info = "".join(stack)
    info = (
        "\n<br /><hr />\n"
        "<strong><pre>%s</pre></strong>\n"
        "</body>"
    ) % stack_info

    content = content.replace("</body>", info)


    fd, file_path = tempfile.mkstemp(prefix="PyLucid_unittest_", suffix=".html")
    os.write(fd, content)
    os.close(fd)
    url = "file://%s" % file_path
    print "\nDEBUG html page in Browser! (url: %s)" % url
    webbrowser.open(url)

#    time.sleep(0.5)
#    os.remove(file_path)




class ContentTestBase(unittest.TestCase):
    """
    Base class to check response content.
    Used the browser traceback with debug_response().
    """

    # Open only one traceback in a browser?
    one_browser_traceback = True

    client = Client() # django test client

    # _________________________________________________________________________
    # create test users:

    def _create_or_update_user(self, username, email, password):
        """
        Delete a existing User and create a fresh new test user
        """
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            user.delete()

        user = User.objects.create_user(username, email, password)
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True
        user.save()

        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise self.failureException("Created user doesn't exist!")

    def create_test_user(self):
        """
        Create a test user with a usable password and return the instance
        """
        return self._create_or_update_user(
            TEST_USERNAME, TEST_USER_EMAIL, TEST_PASSWORD
        )

    def create_test_unusable_user(self):
        """
        Create a test user with a unusable password and return the instance
        """
        return self._create_or_update_user(TEST_UNUSABLE_USER, "", "")

    # _________________________________________________________________________
    # asserts with browser traceback:

    def assertStatusCode(self, response, status_code, msg=None):
        """
        Check if the status code of the given response is ok.
        """
        if response.status_code == status_code:
            # Page ok
            return

        debug_response(response, self.one_browser_traceback)
        self.fail(msg)

    def assertResponse(self, response, must_contain, must_not_contain=()):
        """
        Check the content of the response
        must_contain - a list with string how must be exists in the response.
        must_not_contain - a list of string how should not exists.
        """
        def error(respose, msg):
            debug_response(
                response, self.one_browser_traceback, msg, display_tb=False
            )
            raise self.failureException, msg

        for txt in must_contain:
            if not txt in response.content:
                error(response, "Text not in response: '%s'" % txt)

        for txt in must_not_contain:
            if txt in response.content:
                error(response, "Text should not be in response: '%s'" % txt)

    # _________________________________________________________________________
    # some spezial asserts:

    def assertLists(self, is_list, should_be_list, sort=True):
        """
        sompares two lists how should be the same.
        If the lists has different content, is display a diff and raised a
        AssertionError.
        """
        if sort:
            is_list.sort()
            should_be_list.sort()

        if is_list != should_be_list:
            is_list2 = pprint.pformat(is_list)
            should_be_list2 = pprint.pformat(should_be_list)
            display_plaintext_diff(should_be_list2, is_list2)

        self.assertEqual(
            is_list, should_be_list, "The two lists are not the same!"
        )

    # _________________________________________________________________________
    # create test content:

    def create_template(self, content):
        """
        Create a new template and return the instance
        """
        Template.objects.all().delete()

        template = Template(
            content = content
        )
        template.save()
        return template
#        template.content = "{% lucidTag back_links %}"
#        template.save()



    def create_pages(self, data, parent = None, **kwargs):
        """
        Create recursive pages.
        """
        for page_data in data:
            page_data = page_data.copy()
            page_data.update(kwargs)
            page_data["parent"] = parent
            last_page = self.create_page(page_data)
            if "subitems" in page_data:
                self.create_pages(
                    page_data["subitems"], last_page, **kwargs
                )

#        kwargs["parent"] = None

    def create_page(self, data):
        """
        Create one page and returned the instance.
        If one data field doesn't exist, we use a default one.
        """
        try:
            default_user = User.objects.get(username=TEST_USERNAME)
        except User.DoesNotExist:
            default_user = self.create_test_user()

        default_template = Template.objects.all()[0]
        default_style = Style.objects.all()[0]
        default_markup = Markup.objects.all()[0]

        new_page = Page(
            name             = data.get("name", "New Page"),
            shortcut         = data.get("shortcut", None),
            template         = data.get("template", default_template),
            style            = data.get("style", default_style),
            markup           = data.get("markup", default_markup),
            createby         = data.get("user", default_user),
            lastupdateby     = data.get("user", default_user),
            showlinks        = data.get("showlinks", True),
            permitViewPublic = data.get("permitViewPublic", True),
            permitViewGroup  = data.get("permitViewGroup", None),
            permitEditGroup  = data.get("permitEditGroup", None),
            parent           = data.get("parent", None),
        )
        new_page.save()
        return new_page

    # _________________________________________________________________________
    # methods to get information and test the content:

    def get_links(self, content):
        """
        return all links found with the HREF_RE
        """
        return HREF_RE.findall(content)

    def create_link_snapshot(self, print_result=True):
        """
        Build a a reference snapshot for a unittest.
        Display it via pprint and returned it, too.
        Usefull for copy&paste the output into this source file :)
        """
        if print_result:
            print "Build a snapshot for the unittest compare:"
            print "-"*79
        data = {}
        for page in Page.objects.all():
            url = page.get_absolute_url()

            response = self.client.get(url)
            self.assertStatusCode(response, 200)

            content = response.content.strip()
            links = self.get_links(content)

            if DEBUG:
                print "-"*79
                print "create_snapshot Debug for '%s':" % url
                print "-"*79
                print content
                print "-"*79
                print links
                print "-"*79

            data[url] = links

        if print_result:
            pprint.pprint(data)
            print "-"*79
        return data

    def link_snapshot_test(self, snapshot):
        """
        compare a reference snapshot with the real links.
        """
        is_links = []
        should_be_links = []
        for page in Page.objects.all():
            url = page.get_absolute_url()

            response = self.client.get(url)
            self.assertStatusCode(response, 200)

            content = response.content.strip()
            is_links.append(self.get_links(content))
            should_be_links.append(snapshot[url])

        self.assertLists(is_links, should_be_links, sort=False)





class TestSelf(ContentTestBase):
    def setUp(self):
        Page.objects.all().delete() # Delete all existins pages

    def test_create_pages(self):
        """
        Tests if ContentTestBase.create_pages() works fine ;)
        """
        self.create_pages(TEST_PAGES) # Create the test pages

        # Check if the db data is ok:
        pages = Page.objects.all()
        test_list = []
        for page in pages:
            test_list.append(page.get_absolute_url())

        self.assertLists(test_list, TEST_PAGES_SHORTCUTS)

    def test_create_pages_kwargs(self):
        """
        simple test for the kwargs in create_pages.
        """
        self.create_pages(TEST_PAGES, name="jojo") # Create the test pages

        # Check if the db data is ok:
        pages = Page.objects.all()
#        test = []
        for page in pages:
            if not page.name.startswith("jojo"):
                raise AssertionError("pagename dosn't start with jojo!")

    def test_snaphot(self):
        """
        create a link snaphot and test it with the link_snapshot_test() method
        """
        self.create_pages(TEST_PAGES) # Create the test pages

        # Generate a link snapshot
        snapshot = self.create_link_snapshot(print_result=False)
#        pprint.pprint(snapshot)

        # The snapshot should have the same page count as the TEST_PAGES
        page_len = Page.objects.all().count()
        self.assertEqual(len(snapshot), page_len)

        # Test the generated link snapshot
        self.link_snapshot_test(snapshot)






# Self test
if __name__ == "__main__":
    # Note: For the self test you must uncomment the block above!
    print
    print "_"*79
    unittest.main()