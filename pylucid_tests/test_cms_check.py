from pylucid_tests.test_utils.test_cases import PageInstanceTestCase


class CmsCheckTest(PageInstanceTestCase):
    def test_cms_check(self):
        self.call_manage_py("migrate", "--noinput")
        output = self.call_manage_py("cms", "check")

        self.assertNotIn("ERROR", output)
