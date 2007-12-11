#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the PyLucid SHA1-JS-Login

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from setup_environment import setup, make_insert_dump
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=True,
    install_plugins=True
)

#______________________________________________________________________________
# Test:

import unittest, sys, re, tempfile, os, webbrowser, traceback, time

from PyLucid import models, settings
from PyLucid.plugins_internal.auth.auth import auth
from PyLucid.models import User, JS_LoginData
from PyLucid.install.install import _create_or_update_superuser
from PyLucid.tools import crypt

from django.contrib.auth.models import UNUSABLE_PASSWORD
from django.test.client import Client


# Set the Debug mode on:
crypt.DEBUG = True


# The global test user for many testes.
# creaded in TestUserModels().testcreate_or_update_superuser()
TEST_USERNAME = "unittest"
TEST_USER_EMAIL = "a_test@email-adress.org"
TEST_PASSWORD = "test"

# A user with a unusable password
# creaded in TestUserModels().test_unusable_password()
TEST_UNUSABLE_USER = "unittest2"



# Bug with Firefox under Ubuntu.
# http://www.python-forum.de/topic-11568.html
webbrowser._tryorder.insert(0, 'epiphany') # Use Epiphany, if installed.

ONE_DEBUG_DISPLAYED = False

def debug_response(response, msg="", display_tb=True):
    """
    Display the response content in a webbrowser.
    """
    global ONE_DEBUG_DISPLAYED
    if ONE_DEBUG_DISPLAYED:
        return
    else:
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


js_regex1 = re.compile(r'<script .+?>(.*?)</script>(?imuxs)')
js_regex2 = re.compile(r"(\w+)\s*=\s*['\"]*([^'\"]+)['\"]*;")

def _get_JS_data(content):
    """
    retuned the JS variable statements from the given html page content.
    """
    result = {}
    for txt in js_regex1.findall(content):
        data = dict(js_regex2.findall(txt))
        result.update(data)

    return result



def _build_sha_data(JS_data, password):
    """
    Simulate the JS Routines to build the SHA1 login data from the given
    plaintext password.
    """
    salt = JS_data["salt"]
    challenge = JS_data["challenge"]

    password_hash = crypt.make_hash(password, salt)

#    print "password:", password
#    print "salt:", salt
#    print "challenge:", challenge
#    print "password_hash:", password_hash

    # Split the SHA1-Hash in two pieces
    sha_a = password_hash[:(crypt.HASH_LEN/2)]
    sha_b = password_hash[(crypt.HASH_LEN/2):]

    sha_a2 = crypt.make_hash(sha_a, challenge)

    return sha_a2, sha_b








class TestCryptModul(unittest.TestCase):
    """
    The the PyLucid.tools.crypt modul
    """
    def test_hash_function(self):
        """
        Check if crypt.make_hash() build the same hash as the routine in:
        django.contrib.auth.models.User.set_password()
        """
        raw_password = "a raw password"
        u = User.objects.create_user('hashtestuser', '', raw_password)
        u.save()

        django_password = u.password
        type, django_salt, django_hash = django_password.split("$")
        assert type == "sha1"

        password_hash = crypt.make_hash(raw_password, django_salt)

        assert django_hash == password_hash, (
            "django_hash: %s\n"
            "password_hash: %s"
        ) % (django_hash, password_hash)



#______________________________________________________________________________
#______________________________________________________________________________
#______________________________________________________________________________



class TestBase(unittest.TestCase):

    _open = []

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
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise self.failureException("Created user doesn't exist!")

    def _create_test_user(self):
        self._create_or_update_user(
            TEST_USERNAME, TEST_USER_EMAIL, TEST_PASSWORD
        )

    def _create_test_unusable_user(self):
        self._create_or_update_user(TEST_UNUSABLE_USER, "", "")

    def setUp(self):
        url_base = "/%s/1/auth/%%s/" % settings.COMMAND_URL_PREFIX
        self.login_url = url_base % "login"
        self.pass_reset_url = url_base % "pass_reset"

        self._create_test_user()
        self._create_test_unusable_user()

        self.client = Client()

    def assertStatusCode(self, response, status_code, msg=None):
        if response.status_code == status_code:
            # Page ok
            return

        debug_response(response)
        self.fail(msg)

    def assertResponse(self, response, must_contain, must_not_contain=()):
        def error(respose, msg):
            debug_response(response, msg, display_tb=False)
            raise self.failureException, msg

        for txt in must_contain:
            if not txt in response.content:
                error(response, "Text not in response: '%s'" % txt)

        for txt in must_not_contain:
            if txt in response.content:
                error(response, "Text should not be in response: '%s'" % txt)

#______________________________________________________________________________
#______________________________________________________________________________
#______________________________________________________________________________

class TestUserModels(TestBase):
    """
    Test the JS_LoginData
    """

    def _check_userpassword(self, username):
        """
        Get the userdata from the database and check the creaded JS_LoginData.
        """
        user = User.objects.get(username = username)
        js_login_data = JS_LoginData.objects.get(user = user)

        salt, sha_checksum = crypt.django_to_sha_checksum(user.password)

        DEBUG_HASH_LEN = 52

#        print "user:", user
#        print "js_login_data:", js_login_data
#        print "user.password:", user.password
#        print "js_login_data.salt:", js_login_data.salt
#        print "js_login_data.sha_checksum:", js_login_data.sha_checksum
#        print "DEBUG_HASH_LEN:", DEBUG_HASH_LEN

        assert salt != js_login_data.salt
        assert sha_checksum != js_login_data.sha_checksum
        assert len(user.password) == crypt.SALT_HASH_LEN
        assert len(sha_checksum) == DEBUG_HASH_LEN, "%s %s %s" % (
            sha_checksum, len(sha_checksum)
        )
        assert len(js_login_data.sha_checksum) == DEBUG_HASH_LEN, "%s %s" % (
            js_login_data.sha_checksum, len(js_login_data.sha_checksum)
        )

    def test_normal_test_user(self):
        """
        Test the "normal test user"
        """
        # Check the
        self._check_userpassword(username = TEST_USERNAME)

    def test_unusable_test_user(self):
        """
        Test the "unusable test user"
        """
        user = User.objects.get(username = TEST_UNUSABLE_USER)
        self.assertEqual(user.password, UNUSABLE_PASSWORD)
        
        try:
            js_login_data = JS_LoginData.objects.get(user = user)
        except JS_LoginData.DoesNotExist:
            # User with unusable password, doesn't have a JS_LoginData entry
            pass
        else:
            raise self.failureException(
                "JS_LoginData entry should not exist for a user with a"
                " unuseable password!"
            )


    def test_delete_user(self):
        """
        Delete the user and check if he and the JS_LoginData still exists.
        """
        user = User.objects.get(username = TEST_USERNAME)
        js_login_data = JS_LoginData.objects.get(user = user)
            
        old_id = js_login_data.id
        
        # Delete the user object. The JS_LoginData entry should be deleted, too.
        user.delete()
        
        try:
            user = User.objects.get(username = TEST_USERNAME)
        except User.DoesNotExist:
            pass
        else:
            self.fail("Django User account still exists!")

        try:
            js_login_data = JS_LoginData.objects.get(id = old_id)
        except JS_LoginData.DoesNotExist:
            pass
        else:
            self.fail("JS_LoginData entry still exists!")


    def testcreate_or_update_superuser2(self):
        """
        Test the create_new_superuser routine from the _install section.
        Check the User Password and JS_LoginData.
        """
        user_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "email": TEST_USER_EMAIL,
            "first_name": "", "last_name": ""
        }
        _create_or_update_superuser(user_data)

        self._check_userpassword(username = TEST_USERNAME)

        user = User.objects.get(username = TEST_USERNAME)
        self.failUnless(user.email == TEST_USER_EMAIL)


#______________________________________________________________________________

class TestDjangoLogin(TestBase):
    """
    Test the django admin panel login
    FIXME!!!
    """
    def test_user_account(self):
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        response = self.client.get("/%s/" % settings.ADMIN_URL_PREFIX)
        self.assertStatusCode(response, 200)
#        self.assertResponse(
#            response, must_contain=("Log in", "PyLucid site admin")
#        )

    def test_django_login(self):
        # Make a session
#        del(self.client.cookies)
        print "1", self.client.cookies
        response = self.client.get("/%s/" % settings.ADMIN_URL_PREFIX)
        self.assertStatusCode(response, 200)
        self.assertResponse(
            response, must_contain=("Log in", "PyLucid site admin")
        )
        print "2", self.client.cookies
        print self.client.exc_info

        # login into the django admin panel
        response = self.client.post(
            "/%s/" % settings.ADMIN_URL_PREFIX,
            {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
            }
        )
        self.assertStatusCode(response, 200)
        print "3", self.client.cookies
        print self.client.exc_info
        self.assertResponse(
            response, must_contain=("Log in", "PyLucid site admin"),
            must_not_contain=("log in again", "session has expired")
        )
#        debug_response(response)

    def test_username_input(self):
        response = self.client.get(self.login_url)
        self.assertStatusCode(response, 200)

    def test_send_wrong_username(self):
        response = self.client.post(
            self.login_url, {"username": "not exists"}
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response, must_contain=("User does not exist.",))

#______________________________________________________________________________

class TestPlaintextLogin(TestBase):

    def test_send_username(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "PyLucid unsecure plaintext LogIn - step 2",
                "Password:"
            )
        )

    def test_plaintext_login_wrong(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "password": "a-wrong-password",
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "Wrong password.",
                "PyLucid unsecure plaintext LogIn - step 2",
                "Password:",
                "Request a password reset.",
            )
        )

    def test_plaintext_login(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "password": TEST_PASSWORD,
                "plaintext_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "Password ok.",
                "Log out [%s]" % TEST_USERNAME
            )
        )

    def test_unusable_password(self):
        """
        Check if we get the password reset form, after we send a SHA-Login
        for a user with a unusable password.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_UNUSABLE_USER,
                "plaintext_login" : True
            }
        )
        self.assertResponse(response,
            must_contain=(
                "No usable password was saved.",
                "You must reset your password.",
                "Reset your password:",
            )
        )

#______________________________________________________________________________


class TestSHALogin(TestBase):

    def test_send_username2(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "step 2",
                "Log in"
            )
        )

    def test_SHA_wrong1(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "wrong", "sha_b": "wrong",
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "step 2", "Log in", "Form data is not valid. Please correct."
            ),
            must_not_contain=("Request a password reset.",),
        )

    def test_SHA_wrong2(self):
        """
        right length of sha_a2 and sha_b, but int(sha, 16) failed.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "x234567890123456789012345678901234567890",
                "sha_b": "x2345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=("Log in", "Form data is not valid. Please correct."),
            must_not_contain=("Request a password reset.",),

        )
#        debug_response(response)

    def test_SHA_wrong3(self):
        """
        No Session.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=("Log in", "Session Error."),
            must_not_contain=("Request a password reset.",),
        )
#        debug_response(response)

    def test_SHA_wrong4(self):
        """
        Wrong Password
        """
        # Make a session.
        self.test_send_username2()

        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "Log in", "Wrong password.", "Request a password reset."
            )
        )
#        debug_response(response)

    def test_SHA_login(self):
        """
        Test a SHA login with a correct password.
        """
        # Make a session.
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_login" : True
            }
        )

        JS_data = _get_JS_data(response.content)
        sha_a2, sha_b = _build_sha_data(JS_data, TEST_PASSWORD)

        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERNAME,
                "sha_a2": sha_a2,
                "sha_b": sha_b,
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.assertStatusCode(response, 200)
        self.assertResponse(response,
            must_contain=(
                "Password ok.",
                "Log out [%s]" % TEST_USERNAME
            )
        )

#______________________________________________________________________________


class TestPasswordReset(TestBase):

    def test_pass_reset_form1(self):
        """
        Check if we get the password reset form.
        """
        response = self.client.get(
            self.pass_reset_url,

        )
#        debug_response(response)
        self.assertResponse(response, must_contain=("Reset your password:",))


    def test_unusable_password_sha_login(self):
        """
        Check if we get the password reset form, after we send a SHA-Login
        for a user with a unusable password.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_UNUSABLE_USER,
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "No usable password was saved.",
                "You must reset your password.",
                "Reset your password:",
            )
        )

    def test_unusable_password_plaintext_login(self):
        """
        Check if we get the password reset form, after we send a plain text
        Login for a user with a unusable password.
        """
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_UNUSABLE_USER,
                "plaintext_login" : True
            }
        )
#        debug_response(response)
        self.assertResponse(response,
            must_contain=(
                "No usable password was saved.",
                "You must reset your password.",
                "Reset your password:",
            )
        )


    def test_pass_reset_form_errors1(self):
        """
        form validating test: Check with no username and no email.
        """
        response = self.client.post(self.pass_reset_url)
        self.assertResponse(
            response, must_contain=("Form data is not valid. Please correct.",)
        )


    def test_pass_reset_form_errors2(self):
        """
        form validating test: Check with not existing user.
        """
        response = self.client.post(self.pass_reset_url,
            {"username": "wrong_user"}
        )
        self.assertResponse(response, must_contain=("User does not exist.",))


    def test_pass_reset_form_errors3(self):
        """
        form validating test: Check with valid, but wrong email adress.
        """
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERNAME,
                "email": "wrong@email-adress.org"
            }
        )
        self.assertResponse(response,
            must_contain=("Wrong email address. Please correct.",)
        )


    def test_pass_reset(self):
        """
        form validating test: Check with wrong email adress.
        """
        RESET_URL = "/_command/1/auth/new_password/DEBUG_1234567890/"

        # Send username and email to get a "reset email"
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERNAME,
                "email": TEST_USER_EMAIL
            },
            extra={"REMOTE_ADDR": "unitest REMOTE_ADDR"}
        )
        from PyLucid.plugins_internal.auth.auth import DEBUG
        if DEBUG == True:
            self.assertResponse(response,
                must_contain=(
                    RESET_URL,
                    "Debug! No Email was sended!",
                    "A 'password reset' email was send to you.",
                )
            )
        else:
            self.assertResponse(response,
                must_contain=(
                    "A 'password reset' email was send to you.",
                ),
                must_not_contain = (
                    RESET_URL,
                    "Debug! No Email was sended!",
                )
            )
            from django.core import mail
            self.assertEqual(mail.outbox[0].subject, 'Password reset.')
            assert RESET_URL in mail.outbox[0].body


        # GET the new password input form
        # We need two differend salt values. So we turn debug mode off:
        crypt.DEBUG = False

        response = self.client.get(RESET_URL)
        self.assertResponse(response,
            must_contain=(
                'Set a new password',
                'SHA1 for django', 'SHA1 for PyLucid',
                'src="/media/PyLucid/sha.js"',
                'src="/media/PyLucid/shared_sha_tools.js"',
            )
        )

        js_data = _get_JS_data(response.content)
#        print js_data
        salt_1 = js_data["salt_1"]
        salt_2 = js_data["salt_2"]

        sha_1 = crypt.make_hash(TEST_PASSWORD, salt_1)
        sha_2 = crypt.make_hash(TEST_PASSWORD, salt_2)

        # Send a new password
        response = self.client.post(RESET_URL,
            {
                "username": TEST_USERNAME,
                "email": TEST_USER_EMAIL,
                "sha_1": sha_1,
                "sha_2": sha_2,
                "raw_password": "",
            },
            extra={"REMOTE_ADDR": "unitest REMOTE_ADDR"}
        )
#        debug_response(response)
        self.assertResponse(response, must_contain=("New password saved.",))
     
        user = User.objects.get(username = TEST_USERNAME)
        js_login_data = JS_LoginData.objects.get(user = user)
        
        test = "sha1$%s$%s" % (salt_1, sha_1)
        self.assertEqual(test, user.password)
        self.assertEqual(js_login_data.salt, salt_2)






def suite():
    # Check if the middlewares are on. Otherwise every unitest failed ;)
    middlewares = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    )
    for m in middlewares:
        if not m in settings.MIDDLEWARE_CLASSES:
            raise EnvironmentError, "Middleware class '%s' not installed!" % m

    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(TestCryptModul))
    suite.addTest(unittest.makeSuite(TestUserModels))
    suite.addTest(unittest.makeSuite(TestDjangoLogin))
    suite.addTest(unittest.makeSuite(TestPlaintextLogin))
    suite.addTest(unittest.makeSuite(TestSHALogin))
    suite.addTest(unittest.makeSuite(TestPasswordReset))

    return suite

if __name__ == "__main__":
    print
    print ">>> Unitest"
    print "_"*79
    runner = unittest.TextTestRunner()
    runner.run(suite())
