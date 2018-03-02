
from .test_utils.test_cases import BaseTestCase, PageInstanceTestCase


# class ExampleProjectSettingsTest(BaseTestCase):
#     """
#     Check settings in:
#         pylucid_installer.page_instance_template.example_project
#     """
#     def test_settings(self):
#         # 'createcachetable' is needed, because django-cms used the cache
#         # in init phase, see:
#         # https://github.com/divio/django-cms/issues/5079
#         self.call_manage_py(["createcachetable"])
#
#         output = self.call_manage_py(
#             ["diffsettings"],
#             #debug=True
#         )
#
#         self.assertNotIn("ERROR", output)
#
#         self.assertIn("SETTINGS_MODULE = 'example_project.settings'", output)
#         self.assertIn("SECRET_KEY = 'CHANGE ME!!!'", output)
#         self.assertIn("/path/to/page_instance", output)
#
#         # DATABASE
#         self.assertIn("page_instance_template/example_project/example_project.db", output)


class PageInstanceSettingsTest(PageInstanceTestCase):
    def test_settings(self):
        output = self.call_manage_py("diffsettings")

        self.assertNotIn("ERROR", output)

        self.assertIn("SETTINGS_MODULE = 'test_settings.settings'", output)

        # changed from pylucid_installer:
        self.assertNotIn("SECRET_KEY = 'CHANGE ME!!!'", output)
        self.assertNotIn("/path/to/page_instance", output)

        # DATABASE
        self.assertIn("test_settings/test_settings.db", output)
