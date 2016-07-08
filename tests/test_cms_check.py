
from .test_utils.test_cases import PageInstanceTestCase

class ManageTest(PageInstanceTestCase):
    def test_cms_check(self):
        status, output = self.call_manage_py(["migrate", "--noinput"])
        self.assertEqual(status, 0)

        status, output = self.call_manage_py(["cms", "check"])
        #print(output)

        self.assertNotIn("ERROR", output)
        self.assertEqual(status, 0)