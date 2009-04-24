
if __name__ == "__main__":
    # run unittest directly
    import os
    os.environ["DJANGO_SETTINGS_MODULE"] = "pylucid.tests.testutils.settings"

from pylucid.tests.testcases.url_patterns import TestWithRegexURLResolver, TestWithReverse

if __name__ == "__main__":
    # Run this unittest directly
    from django.core import management
    management.call_command('test', 'pylucid')
