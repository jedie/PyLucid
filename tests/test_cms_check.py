
from .test_utils.test_cases import PageInstanceTestCase

class CmsCheckTest(PageInstanceTestCase):
    def test_cms_check(self):
        status, output = self.call_manage_py(["migrate", "--noinput"])
        self.assertEqual(status, 0)

        status, output = self.call_manage_py(["cms", "check"])

        self.assertNotIn("ERROR", output)
        self.assertEqual(status, 0)