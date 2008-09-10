#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test the PyLucid SHA1-JS-Login

    TODO: Test "superuser" and "staff" users, too.

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""
import unittest, sys, re, os, time

import tests
from tests import TEST_USERS, TEST_UNUSABLE_USER

from PyLucid import models, settings
from PyLucid.plugins_internal.auth.auth import auth
from PyLucid.models.JS_LoginData import User, JS_LoginData
from PyLucid.install.install import _create_or_update_superuser
from PyLucid.tools import crypt

from django.contrib.auth.models import UNUSABLE_PASSWORD

# Open only one traceback in a browser (=True) ?
#ONE_BROWSER_TRACEBACK = False
ONE_BROWSER_TRACEBACK = True

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


class TestBase(tests.TestCase):

    one_browser_traceback = ONE_BROWSER_TRACEBACK
    _open = []

    def setUp(self):
        url_base = "/%s/1/auth/%%s/" % settings.COMMAND_URL_PREFIX
        self.login_url = url_base % "login"
        self.pass_reset_url = url_base % "pass_reset"



class TestUnittestUser(TestBase):
    """
    Test the unittest user
    """
    def test_login(self):
        """
        Login every test user, and check if the username is in the admin panel.
        """
        for usertype in TEST_USERS:
            self.login(usertype)

            response = self.client.get("/")
            self.failUnlessEqual(response.status_code, 200)
            self.assertResponse(
                response,
                must_contain=(
                    ">Log out [%s]<" % TEST_USERS[usertype]["username"],
                ),
            )

    def test_normal_user(self):
        """
        Test if all testuser exists
        """
        for user in User.objects.all():
            if user.username == TEST_UNUSABLE_USER["username"]:
                # User with a unusable password
                assert user.password == UNUSABLE_PASSWORD
                self.assertRaises(
                    JS_LoginData.DoesNotExist,
                    JS_LoginData.objects.get,
                    user = user
                )
            else:
                # User with normal password
                assert user.password.startswith("sha1$")
                js_login_data = JS_LoginData.objects.get(user = user)
                assert js_login_data.sha_checksum.startswith("sha1$")



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
        # FIX ME
        #assert len(sha_checksum) == DEBUG_HASH_LEN, "%s %s" % (
        #    sha_checksum, len(sha_checksum)
        #)
        #assert len(js_login_data.sha_checksum) == DEBUG_HASH_LEN, "%s %s" % (
        #    js_login_data.sha_checksum, len(js_login_data.sha_checksum)
        #)

    def test_normal_test_user(self):
        """
        Test the "normal test user"
        """
        # Check the
        self._check_userpassword(username = TEST_USERS["normal"]["username"])

    def test_unusable_test_user(self):
        """
        Test the "unusable test user"
        """
        user = User.objects.get(username = TEST_UNUSABLE_USER["username"])
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
        user = User.objects.get(username = TEST_USERS["normal"]["username"])
        js_login_data = JS_LoginData.objects.get(user = user)

        old_id = js_login_data.id

        # Delete the user object. The JS_LoginData entry should be deleted, too.
        user.delete()

        try:
            user = User.objects.get(username = TEST_USERS["normal"]["username"])
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
            "username": TEST_USERS["normal"]["username"],
            "password": TEST_USERS["normal"]["password"],
            "email": TEST_USERS["normal"]["email"],
            "first_name": "", "last_name": ""
        }
        _create_or_update_superuser(user_data)

        self._check_userpassword(username = TEST_USERS["normal"]["username"])

        user = User.objects.get(username = TEST_USERS["normal"]["username"])
        self.failUnless(user.email == TEST_USERS["normal"]["email"])


#______________________________________________________________________________

class TestDjangoLogin(TestBase):
    """
    Test the django admin panel login
    """
    def test_django_login(self):
        response = self.client.get("/%s/" % settings.ADMIN_URL_PREFIX)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(
            response, must_contain=("Log in", "site admin")
        )
        # login with the "is_staff" test user
        self.login("staff")
        response = self.client.get("/%s/" % settings.ADMIN_URL_PREFIX)
        self.assertResponse(
            response, must_contain=("",), must_not_contain=("Log in",)
        )

    def test_send_wrong_username(self):
        response = self.client.post(
            self.login_url, {"username": "not exists"}
        )
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response, must_contain=("User does not exist.",))

#______________________________________________________________________________

class TestPlaintextLogin(TestBase):

    def test_send_username(self):
        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERS["normal"]["username"],
                "plaintext_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "password": "a-wrong-password",
                "plaintext_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "password": TEST_USERS["normal"]["password"],
                "plaintext_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Password ok.",
                "Log out [%s]" % TEST_USERS["normal"]["username"]
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
                "username": TEST_UNUSABLE_USER["username"],
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
                "username": TEST_USERS["normal"]["username"],
                "sha_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "sha_a2": "wrong", "sha_b": "wrong",
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "sha_a2": "x234567890123456789012345678901234567890",
                "sha_b": "x2345678901234567890",
                "sha_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "sha_a2": "1234567890123456789012345678901234567890",
                "sha_b": "12345678901234567890",
                "sha_login" : True
            }
        )
        self.failUnlessEqual(response.status_code, 200)
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
                "username": TEST_USERS["normal"]["username"],
                "sha_login" : True
            }
        )

        JS_data = _get_JS_data(response.content)
        sha_a2, sha_b = _build_sha_data(JS_data, TEST_USERS["normal"]["password"])

        response = self.client.post(
            self.login_url,
            {
                "username": TEST_USERS["normal"]["username"],
                "sha_a2": sha_a2,
                "sha_b": sha_b,
                "sha_login" : True
            }
        )
#        debug_response(response)
        self.failUnlessEqual(response.status_code, 200)
        self.assertResponse(response,
            must_contain=(
                "Password ok.",
                "Log out [%s]" % TEST_USERS["normal"]["username"]
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
                "username": TEST_UNUSABLE_USER["username"],
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
                "username": TEST_UNUSABLE_USER["username"],
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
            {
                "username": "wrong_user",
                "email": "wrong@email-adress.org"
            }
        )
        self.assertResponse(response, must_contain=("User does not exist.",))


    def test_pass_reset_form_errors3(self):
        """
        form validating test: Check with valid, but wrong email adress.
        """
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERS["normal"]["username"],
                "email": "wrong@email-adress.org"
            }
        )
        self.assertResponse(response,
            must_contain=("Wrong email address. Please correct.",)
        )

    def test_pass_reset_form_errors4(self):
        """
        form validating test: Check with not existing user.
        """
        response = self.client.post(self.pass_reset_url,
            {"username": "no_email_send"}
        )
        self.assertResponse(response,
            must_contain=(
                "Form data is not valid. Please correct.",
                "This field is required.",
            )
        )

    def test_pass_reset(self):
        """
        form validating test: Check with wrong email adress.
        """
        RESET_URL = "/_command/1/auth/new_password/DEBUG_1234567890/"
        crypt.DEBUG = True
        # Send username and email to get a "reset email"
        response = self.client.post(self.pass_reset_url,
            {
                "username": TEST_USERS["normal"]["username"],
                "email": TEST_USERS["normal"]["email"]
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

        sha_1 = crypt.make_hash(TEST_USERS["normal"]["password"], salt_1)
        sha_2 = crypt.make_hash(TEST_USERS["normal"]["password"], salt_2)

        # Send a new password
        response = self.client.post(RESET_URL,
            {
                "username": TEST_USERS["normal"]["username"],
                "email": TEST_USERS["normal"]["email"],
                "sha_1": sha_1,
                "sha_2": sha_2,
                "raw_password": "",
            },
            extra={"REMOTE_ADDR": "unitest REMOTE_ADDR"}
        )
#        debug_response(response)
        self.assertResponse(response, must_contain=("New password saved.",))

        user = User.objects.get(username = TEST_USERS["normal"]["username"])
        js_login_data = JS_LoginData.objects.get(user = user)

        test = "sha1$%s$%s" % (salt_1, sha_1)
        self.assertEqual(test, user.password)
        self.assertEqual(js_login_data.salt, salt_2)


if __name__ == "__main__":
    # Run this unitest directly
    import os
    os.chdir("../")
    filename = os.path.splitext(os.path.basename(__file__))[0]
    tests.run_tests(test_labels=[filename])
