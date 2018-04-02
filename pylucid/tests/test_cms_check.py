
"""
    PyLucid
    ~~~~~~~

    :copyleft: 2018 by the PyLucid team, see AUTHORS for more details.
    :created: 2018 by JensDiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from pylucid.tests.test_utils.test_cases import PageInstanceTestCase


class CmsCheckTest(PageInstanceTestCase):
    def test_cms_check(self):
        self.call_manage_py("migrate", "--noinput")
        output = self.call_manage_py("cms", "check")
        print(output)

        self.assertIn("Checking django CMS installation", output)
        self.assertIn("Installation okay", output)

        self.assertNotIn("ERROR", output)
