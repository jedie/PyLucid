#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid unittest
    ~~~~~~~~~~~~~~~~

    Test PyLucid.tools.crypt

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyright: 2007 by Jens Diemer.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

#______________________________________________________________________________
# Test:

import tests

from PyLucid.tools.crypt import SALT_HASH_LEN, SaltHashError, make_salt_hash, \
                        check_salt_hash, salt_hash_to_dict, encrypt, decrypt


class TestSaltHash(tests.TestCase):
    """
    Test for make_salt_hash, check_salt_hash and salt_hash_to_dict.

    Class is inherited directly from unittest.TestCase as PyLucid database is
    not needed for tests.
    """
    ascii_string = "".join([chr(i) for i in xrange(128)])

    def test_ascii(self):
        salt_hash = make_salt_hash(self.ascii_string)
        self.assertEqual(len(salt_hash), SALT_HASH_LEN)

        check_salt_hash(self.ascii_string, salt_hash)

        self.assertRaises(SaltHashError, check_salt_hash, "wrong!", salt_hash)

    def test_unicode(self):
        """
        Only Strings, not unicode are accepted.
        """
        self.assertRaises(SaltHashError, make_salt_hash, u"")

        self.assertRaises(SaltHashError, check_salt_hash, u"", "")
        self.assertRaises(SaltHashError, check_salt_hash, "", u"")

    def test_modified(self):
        """
        Test a changed salt hash checksum
        """
        salt_hash = make_salt_hash(self.ascii_string)
        for i in xrange(len(self.ascii_string)):
            if self.ascii_string[i] == "_":
                wrong_char = " "
            else:
                wrong_char = "_"

            invalid_checksum = "".join([
                self.ascii_string[:i], wrong_char, self.ascii_string[i+1:]
            ])
            self.assertRaises(
                SaltHashError, check_salt_hash, invalid_checksum, salt_hash
            )

    def test_salt_hash_to_dict(self):
        salt_hash = "sha$3863$d894911422c320e2f656f08fe32c13219537221d"
        check = {
            'type': 'sha',
            'salt': '3863',
            'hash': 'd894911422c320e2f656f08fe32c13219537221d'
        }

        salt_hash_dict = salt_hash_to_dict(salt_hash)
        self.assertEqual(salt_hash_dict, check)


class TestCrypt(tests.TestCase):
    """
    Test for "encrypt"
     and "decrypt"
    """
    def _assert_tests(self, txt, key, crypted, decrypted):
        self.assertNotEqual(crypted, txt)
        self.assertNotEqual(crypted, key)
        self.assertNotEqual(decrypted, crypted)
        self.assertNotEqual(decrypted, key)
        self.assertEqual(decrypted, txt)

    def test_latin1(self):
        """
        Test with the first 256 unicode characerts
        """
        txt = u"".join([unichr(i) for i in xrange(0, 256)])
        key = u"".join([unichr(i) for i in xrange(256, 0, -1)])
        crypted = encrypt(txt, key, use_base64=False)
        decrypted = decrypt(crypted, key, use_base64=False)
        self._assert_tests(txt, key, crypted, decrypted)

    def test_unicode(self):
        """
        Test with 10.000 unicode characerts
        """
        txt = u"".join([unichr(i) for i in xrange(0, 65535, 65535 / 9999)])
        key = u"".join([unichr(i) for i in xrange(2, 65535, 65535 / 9999)])
        crypted = encrypt(txt, key, use_base64=False)
        decrypted = decrypt(crypted, key, use_base64=False)
        self._assert_tests(txt, key, crypted, decrypted)

    def test_is_unicode(self):
        """
        txt and key must always be unicode
        """
        self.assertRaises(UnicodeError, encrypt, "a string", u"")
        self.assertRaises(UnicodeError, decrypt, "a string", u"")
        self.assertRaises(UnicodeError, encrypt, u"", "a string")
        self.assertRaises(UnicodeError, decrypt, u"", "a string")

    def test_diff_length(self):
        """
        txt and key must have the same length
        """
        self.assertRaises(AssertionError, encrypt, u"123", u"")
        self.assertRaises(AssertionError, encrypt, u"", u"123")

    def test_modified(self):
        """
        Test a changed crypted data
        """
        txt = u"".join([unichr(i) for i in xrange(0, 256)])
        key = u"".join([unichr(i) for i in xrange(256, 0, -1)])
        original_crypted = encrypt(txt, key, use_base64=False)

        for i in xrange(len(original_crypted)):
            if original_crypted[i] == u"\x00":
                wrong_char = u"\x01"
            else:
                wrong_char = u"\x00"

            invalid_crypted = u"".join([
                original_crypted[:i], wrong_char, original_crypted[i+1:]
            ])
            try:
                decrypt(invalid_crypted, key, use_base64=False)
            except SaltHashError:
                # OK
                pass
            else:
                msg = "SaltHashError not raised"
                print "_"*80
                print msg
                print "position:", i
                print "-"*80
                raise AssertionError(msg)

