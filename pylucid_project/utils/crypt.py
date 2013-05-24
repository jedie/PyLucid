# coding: utf-8

"""
    PyLucid.tools.crypt
    ~~~~~~~~~~~~~~~~~~~

    Routines for the PyLucid SHA-JS-Login.
    more info:
        http://www.pylucid.org/permalink/42/secure-login-without-https

    unittest: ./dev_scripts/unittests/unittest_crypt.py

    :copyleft: 2007-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import base64
import hashlib
import os
import random
import re
import sys
import time

if __name__ == "__main__":
    print "Local DocTest..."
    settings = type('Mock', (object,), {})()
    settings.SECRET_KEY = "DocTest"
    smart_str = str
else:
    from django.conf import settings
    from django.utils.encoding import smart_str


# Warning: Debug must always be False in productiv environment!
#DEBUG = True
DEBUG = False
if DEBUG:
    import warnings
    warnings.warn("Debugmode is on", UserWarning)

HASH_TYP = "sha1"

OLD_SALT_LEN = 5 # old length of the random salt value

# Django used 12 as default in hashers.SHA1PasswordHasher()
# number comes from django.utils.crypto.get_random_string()
SALT_LEN = 12 # new length of the random salt value

HASH_LEN = 40 # length of a SHA-1 hexdigest

# SHA-1 hexdigest + "sha1" + (2x "$") + salt length
SALT_HASH_LEN = HASH_LEN + 4 + 2 + SALT_LEN
OLD_SALT_HASH_LEN = HASH_LEN + 4 + 2 + OLD_SALT_LEN


class SaltHashError(Exception):
    pass

#______________________________________________________________________________

SHA1_RE = re.compile(r'[a-f0-9]{40}$')

def validate_sha_value(sha_value):
    """
    Check if the given >sha_value< is a possible SHA1 hexdigest ;)
    returned true or false

    Should we better use a RE method?
    http://www.python-forum.de/post-74657.html

    >>> validate_sha_value("wrong length")
    False
    >>> validate_sha_value(1234)
    False
    >>> validate_sha_value("right length but not a SHA1 hexdigest!!!")
    False
    >>> validate_sha_value("790f2ebcb902c966fb0e232515ec1319dc9118af")
    True
    """
    if not isinstance(sha_value, basestring):
        return False

    if SHA1_RE.match(sha_value):
        return True

    return False
#
#    if not (isinstance(sha_value, basestring) and len(sha_value) == HASH_LEN):
#        return False
#
#    try:
#        int(sha_value, 16)
#    except (ValueError, OverflowError), e:
#        return False
#    else:
#        return True

#______________________________________________________________________________


def get_new_seed(can_debug=True):
    """
    Generate a new, random seed value.

    >>> get_new_seed() # DEBUG is True in DocTest!
    'DEBUG_1234567890'
    >>> seed = get_new_seed(can_debug=False)
    >>> assert seed != 'DEBUG', "seed is: %s" % seed
    >>> assert len(seed) == HASH_LEN, "Wrong length: %s" % len(seed)
    """
    if can_debug and DEBUG:
        seed = "DEBUG_1234567890"
    else:
        raw_seed = "%s%s%s%s" % (
            random.randint(0, sys.maxint - 1), os.getpid(), time.time(),
            settings.SECRET_KEY
        )
        seed = hashlib.sha1(raw_seed).hexdigest()

    return seed


def get_new_salt(can_debug=True):
    """
    Generate a new, random salt value.

    >>> get_new_salt() # DEBUG is True in DocTest!
    'DEBUG_123456'
    >>> salt = get_new_salt(can_debug=False)
    >>> assert salt != 'DEBUG_1234567890', "salt is: %s" % salt
    >>> assert len(salt) == SALT_LEN, "Wrong length: %s" % len(salt)
    """
    seed = get_new_seed(can_debug)
    return seed[:SALT_LEN]

def get_pseudo_salt(*args):
    """
    generate a pseudo salt (used, if user is wrong)
    """
    temp = "".join([repr(arg) for arg in args])
    return hashlib.sha1(temp).hexdigest()[:SALT_LEN]


def make_hash(txt, salt):
    """
    make a SHA1 hexdigest from the given >txt< and >salt<.
    IMPORTANT:
        This routine must work like
        django.contrib.auth.models.User.set_password()!

    >>> make_hash(txt="test", salt='DEBUG')
    '790f2ebcb902c966fb0e232515ec1319dc9118af'
    """
    sha1hash = hashlib.sha1(salt + smart_str(txt)).hexdigest()
    return sha1hash


def get_salt_and_hash(txt):
    """
    Generate a hast value with a random salt
    returned salt and sha1hash as a tuple

    >>> get_salt_and_hash("test")
    ('sha1', 'DEBUG_123456', '9f5ee85f5c91adb5741d8f93483386989d5d49ae')
    """
    if not isinstance(txt, str):
        raise SaltHashError("Only string allowed!")

    salt = get_new_salt()
    sha1hash = make_hash(txt, salt)

    return (HASH_TYP, salt, sha1hash)


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value
    returned one string back

    >>> make_salt_hash("test")
    'sha1$DEBUG_123456$9f5ee85f5c91adb5741d8f93483386989d5d49ae'
    """
    salt_hash = "$".join(get_salt_and_hash(txt))
    return salt_hash


def check_salt_hash(txt, salt_hash):
    """
    compare txt with the salt-sha1hash.

    TODO: Should we used the django function for this?
        Look at: django.contrib.auth.models.check_password

    >>> salt_hash = make_salt_hash("test")
    >>> salt_hash
    'sha1$DEBUG_123456$9f5ee85f5c91adb5741d8f93483386989d5d49ae'
    >>> check_salt_hash("test", salt_hash)
    True
    """
#    if not (isinstance(txt, str) and isinstance(salt_hash, str)):
#        raise SaltHashError("Only string allowed!")

    if len(salt_hash) not in (SALT_HASH_LEN, OLD_SALT_HASH_LEN):
        raise SaltHashError("Wrong salt-sha1hash length.")

    try:
        hash_type, salt, sha1hash = salt_hash.split("$")
    except ValueError:
        raise SaltHashError("Wrong salt-sha1hash format.")

    if hash_type != "sha1":
        raise SaltHashError("Unsupported sha1hash method.")

    test_hash = make_hash(txt, salt)
#    raise
    if sha1hash != test_hash:
        msg = "salt-sha1hash compare failed."
        if DEBUG:
            msg += " (txt: '%s', salt: '%s', sha1hash: '%s', test_hash: '%s')" % (
                txt, salt, sha1hash, test_hash
            )
        raise SaltHashError(msg)

    return True


def salt_hash_to_dict(salt_hash):
    """
    >>> result = salt_hash_to_dict("sha$salt_value$the_SHA_value")
    >>> result == {'salt': 'salt_value', 'hash_type': 'sha', 'hash_value': 'the_SHA_value'}
    True
    """
    hash_type, salt, hash_value = salt_hash.split("$")
    return {
        "hash_type": hash_type,
        "salt": salt,
        "hash_value": hash_value
    }


#______________________________________________________________________________

class CryptLengthError(AssertionError):
    pass


def crypt(txt, key):
    """
    XOR ciphering
    >txt< and >key< should be unicode.

    >>> crypt("1234", "ABCD")
    u'pppp'
    """
    if len(txt) != len(key):
        raise CryptLengthError("XOR cipher error: %r and %r must have the same length!" % (txt, key))

    crypted = [unichr(ord(t) ^ ord(k)) for t, k in zip(txt, key)]
    return u"".join(crypted)


def encrypt(txt, key, use_base64=True, can_debug=True):
    """
    XOR ciphering with a SHA salt-hash checksum

    >>> encrypt(u"1234", u"ABCD") # DEBUG is True in DocTest!
    u'crypt 1234 with ABCD'

    >>> encrypt(u"1234", u"ABCD", can_debug=False)
    u'sha1$DEBUG_123456$91ca222581d9b8f61934d7bf25fb3625141cda91cHBwcA=='

    >>> encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    u'sha1$DEBUG_123456$91ca222581d9b8f61934d7bf25fb3625141cda91pppp'
    """
    if not (isinstance(txt, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    if can_debug and DEBUG:
        return "crypt %s with %s" % (txt, key)

    salt_hash = make_salt_hash(repr(txt))
    salt_hash = unicode(salt_hash)

    crypted = crypt(txt, key)
    if use_base64 == True:
        crypted = base64.b64encode(crypted)
    return salt_hash + crypted


def decrypt(crypted, key, use_base64=True, can_debug=True):
    """
    1. Decrypt a XOR crypted String.
    2. Compare the inserted sSHA salt-hash checksum.

    >>> decrypt('crypt 1234 with ABCD', "ABCD") # DEBUG is True in DocTest!
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", can_debug=False)
    >>> crypted
    u'sha1$DEBUG_123456$91ca222581d9b8f61934d7bf25fb3625141cda91cHBwcA=='
    >>> decrypt(crypted, u"ABCD", can_debug=False)
    u'1234'

    >>> decrypt(u'sha1$DEBUG$b323f546665b1f034742630133d1b489480a24e2cHBwcA==', u"ABCD", can_debug=False)
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    >>> decrypt(crypted, u"ABCD", use_base64=False, can_debug=False)
    u'1234'
    """
    crypted = unicode(crypted)
    key = unicode(key)

    if can_debug and DEBUG:
        txt, _, key2 = crypted.split(" ", 3)[1:]
        assert key == key2, "key: %s != key2: %s" % (key, key2)
        return txt

    salt_hash = str(crypted[:SALT_HASH_LEN])
    crypted1 = crypted[SALT_HASH_LEN:]
    if use_base64 == True:
        crypted1 = base64.b64decode(crypted1)
        crypted1 = unicode(crypted1)

    try:
        decrypted = crypt(crypted1, key)
    except CryptLengthError:
        # Try with the OLD_SALT_HASH_LEN
        salt_hash = str(crypted[:OLD_SALT_HASH_LEN])
        crypted2 = crypted[OLD_SALT_HASH_LEN:]
        if use_base64 == True:
            crypted2 = base64.b64decode(crypted2)
            crypted2 = unicode(crypted2)
        decrypted = crypt(crypted2, key)

    # raised a SaltHashError() if the checksum is wrong:
    check_salt_hash(repr(decrypted), salt_hash)

    return decrypted


#______________________________________________________________________________

def django_to_sha_checksum(django_salt_hash):
    """
    Create a JS-SHA-Checksum from the django user password.
    (For the unittest)

    The >django_salt_hash< is:
        user = User.objects.get(...)
        django_salt_hash = user.password

    >>> django_to_sha_checksum("sha1$DEBUG$50b412a7ef09f4035f2daca882a1f8bfbe263b62")
    ('DEBUG', u'crypt 50b412a7ef09f4035f2d with aca882a1f8bfbe263b62')
    """
    hash_typ, salt, hash_value = django_salt_hash.split("$")
    assert hash_typ == "sha1", "hash_value typ not supported!"
    assert len(hash_value) == HASH_LEN, "Wrong hash_value length! (Not a SHA1 hash_value?)"

    # Split the SHA1-Hash in two pieces
    sha_a = hash_value[:(HASH_LEN / 2)]
    sha_b = hash_value[(HASH_LEN / 2):]

    sha_a = unicode(sha_a)
    sha_b = unicode(sha_b)
    sha_checksum = encrypt(txt=sha_a, key=sha_b)

    return salt, sha_checksum

def make_sha_checksum2(raw_password):
    """
    Create a SHA1-JS-Login checksum from a plaintext password.

    >>> make_sha_checksum2("test")
    ('DEBUG_123456', u'crypt 9f5ee85f5c91adb5741d with 8f93483386989d5d49ae')
    """
    _, salt, hash_value = get_salt_and_hash(raw_password)

    return salt, make_sha_checksum(hash_value)

def make_sha_checksum(hash_value):
    """
    Made the needed sha_checksum for the SHA1-JS-Login.

    >>> make_sha_checksum("50b412a7ef09f4035f2daca882a1f8bfbe263b62")
    u'crypt 50b412a7ef09f4035f2d with aca882a1f8bfbe263b62'
    """
    # Split the SHA1-Hash in two pieces
    sha_a = hash_value[:(HASH_LEN / 2)]
    sha_b = hash_value[(HASH_LEN / 2):]

    sha_a = unicode(sha_a)
    sha_b = unicode(sha_b)
    sha_checksum = encrypt(txt=sha_a, key=sha_b)
    return sha_checksum


def check_js_sha_checksum(challenge, sha_a, sha_b, sha_checksum, loop_count, cnonce):
    """
    Check a PyLucid JS-SHA-Login

    >>> salt1 = "a salt value"
    >>> challenge = "debug"
    >>> loop_count = 5
    >>> cnonce = "0123456789abcdef0123456789abcdef01234567"
    >>> password = "test"
    >>>
    >>> hash_value = make_hash(password, salt1)
    >>> hash_value
    'f893fc3ebdfd886836822161b6bc2ccac955e014'
    >>> sha_checksum = make_sha_checksum(hash_value)
    >>> sha_checksum
    u'crypt f893fc3ebdfd88683682 with 2161b6bc2ccac955e014'
    >>>
    >>> sha_a = hash_value[:(HASH_LEN/2)]
    >>> sha_a
    'f893fc3ebdfd88683682'
    >>> sha_b = hash_value[(HASH_LEN/2):]
    >>> sha_b
    '2161b6bc2ccac955e014'
    >>> for i in range(loop_count):
    ...    sha_a
    ...    sha_a = hashlib.sha1("%s%s%s%s" % (sha_a, i, challenge, cnonce)).hexdigest()
    'f893fc3ebdfd88683682'
    '7416451ba99917ccd09cfb5168678308933ed82c'
    'ec569defb31299e6134ad8e0c03ff40ab37972da'
    'c8036fe582d777da7090a941e8405982b39a5a71'
    'a0a793881a87782364816ab3e433d02f4527acbb'
    >>> sha_a
    'fa5746d279f5be31fa031100837a6a6b0233467c'
    >>> check_js_sha_checksum(challenge, sha_a, sha_b, sha_checksum, loop_count, cnonce)
    True
    """
    local_sha_a = decrypt(sha_checksum, sha_b)

    for i in range(loop_count):
        local_sha_a = hashlib.sha1(
            "%s%s%s%s" % (local_sha_a, i, challenge, cnonce)
        ).hexdigest()

    if local_sha_a == sha_a:
        return True
    elif DEBUG:
        return "%r != %r" % (local_sha_a, sha_a)

    return False



if __name__ == "__main__":
    DEBUG = True

    import doctest
    print doctest.testmod(
        verbose=False
    )
