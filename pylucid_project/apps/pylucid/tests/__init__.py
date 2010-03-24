
if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid.tests.testutils.test_settings"

from pylucid_project.apps.pylucid.tests.test_url_patterns import TestWithRegexURLResolver, TestWithReverse
from pylucid_project.apps.pylucid.tests.test_apply_markup import TestApplyMarkup

if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', 'pylucid')
