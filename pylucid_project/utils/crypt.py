# -*- coding: utf-8 -*-

"""
    PyLucid.tools.crypt
    ~~~~~~~~~~~~~~~~~~~

    -Two usefull salt hash functions. (Used in the _install section for login.)
    -A one-time-pad XOR crypter. (Used for the SHA-JS-Login)

    unittest: ./dev_scripts/unittests/unittest_crypt.py

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2007-2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os, sys, time, random, base64, re
try:
    import hashlib
    sha_constructor = hashlib.sha1
except ImportError:
    import sha
    sha_constructor = sha.new

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

SALT_LEN = 5 # length of the random salt value
HASH_LEN = 40 # length of a SHA-1 hexdigest

# SHA-1 hexdigest + "sha1" + (2x "$") + salt length
SALT_HASH_LEN = HASH_LEN + 4 + 2 + SALT_LEN


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
        seed = sha_constructor(raw_seed).hexdigest()

    return seed


def get_new_salt(can_debug=True):
    """
    Generate a new, random salt value.

    >>> get_new_salt() # DEBUG is True in DocTest!
    'DEBUG'
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
    return sha_constructor(temp).hexdigest()[:SALT_LEN]


def make_hash(txt, salt):
    """
    make a SHA1 hexdigest from the given >txt< and >salt<.
    IMPORTANT:
        This routine must work like
        django.contrib.auth.models.User.set_password()!

    >>> make_hash(txt="test", salt='DEBUG')
    '790f2ebcb902c966fb0e232515ec1319dc9118af'
    """
    hash = sha_constructor(salt + smart_str(txt)).hexdigest()
    return hash


def get_salt_and_hash(txt):
    """
    Generate a hast value with a random salt
    returned salt and hash as a tuple

    >>> get_salt_and_hash("test")
    ('sha1', 'DEBUG', '790f2ebcb902c966fb0e232515ec1319dc9118af')
    """
    if not isinstance(txt, str):
        raise SaltHashError("Only string allowed!")

    salt = get_new_salt()
    hash = make_hash(txt, salt)

    return (HASH_TYP, salt, hash)


def make_salt_hash(txt):
    """
    make from the given string a hash with a salt value
    returned one string back

    >>> make_salt_hash("test")
    'sha1$DEBUG$790f2ebcb902c966fb0e232515ec1319dc9118af'
    """
    salt_hash = "$".join(get_salt_and_hash(txt))
    return salt_hash


def check_salt_hash(txt, salt_hash):
    """
    compare txt with the salt-hash.

    TODO: Should we used the django function for this?
        Look at: django.contrib.auth.models.check_password

    >>> salt_hash = make_salt_hash("test")
    >>> salt_hash
    'sha1$DEBUG$790f2ebcb902c966fb0e232515ec1319dc9118af'
    >>> check_salt_hash("test", salt_hash)
    True
    """
#    if not (isinstance(txt, str) and isinstance(salt_hash, str)):
#        raise SaltHashError("Only string allowed!")

    if len(salt_hash) != SALT_HASH_LEN:
        raise SaltHashError("Wrong salt-hash length.")

    try:
        type, salt, hash = salt_hash.split("$")
    except ValueError:
        raise SaltHashError("Wrong salt-hash format.")

    if type != "sha1":
        raise SaltHashError("Unsupported hash method.")

    test_hash = make_hash(txt, salt)
#    raise
    if hash != test_hash:
        msg = "salt-hash compare failed."
        if DEBUG:
            msg += " (txt: '%s', salt: '%s', hash: '%s', test_hash: '%s')" % (
                txt, salt, hash, test_hash
            )
        raise SaltHashError(msg)

    return True


def salt_hash_to_dict(salt_hash):
    """
    >>> salt_hash_to_dict("sha$salt_value$the_SHA_value")
    {'salt': 'salt_value', 'type': 'sha', 'hash': 'the_SHA_value'}
    """
    type, salt, hash = salt_hash.split("$")
    return {
        "type": type,
        "salt": salt,
        "hash": hash
    }


#______________________________________________________________________________


def crypt(txt, key):
    """
    XOR ciphering
    >txt< and >key< should be unicode.

    >>> crypt("1234", "ABCD")
    u'pppp'
    """
    assert len(txt) == len(key), "Error: txt and key must have the same length!"

    crypted = [unichr(ord(t) ^ ord(k)) for t, k in zip(txt, key)]
    return u"".join(crypted)


def encrypt(txt, key, use_base64=True, can_debug=True):
    """
    XOR ciphering with a SHA salt-hash checksum

    >>> encrypt(u"1234", u"ABCD") # DEBUG is True in DocTest!
    u'crypt 1234 with ABCD'

    >>> encrypt(u"1234", u"ABCD", can_debug=False)
    u'sha1$DEBUG$b323f546665b1f034742630133d1b489480a24e2cHBwcA=='

    >>> encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    u'sha1$DEBUG$b323f546665b1f034742630133d1b489480a24e2pppp'
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

    >>> decrypt(u'crypt 1234 with ABCD', u"ABCD") # DEBUG is True in DocTest!
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", can_debug=False)
    >>> crypted
    u'sha1$DEBUG$b323f546665b1f034742630133d1b489480a24e2cHBwcA=='
    >>> decrypt(crypted, u"ABCD", can_debug=False)
    u'1234'

    >>> crypted = encrypt(u"1234", u"ABCD", use_base64=False, can_debug=False)
    >>> decrypt(crypted, u"ABCD", use_base64=False, can_debug=False)
    u'1234'
    """
    if not (isinstance(crypted, unicode) and isinstance(key, unicode)):
        raise UnicodeError("Only unicode allowed!")

    if can_debug and DEBUG:
        txt, _, key2 = crypted.split(" ", 3)[1:]
        assert key == key2, "key: %s != key2: %s" % (key, key2)
        return txt

    salt_hash = str(crypted[:SALT_HASH_LEN])
    crypted = crypted[SALT_HASH_LEN:]
    if use_base64 == True:
        crypted = base64.b64decode(crypted)
        crypted = unicode(crypted)

    decrypted = crypt(crypted, key)

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
    hash_typ, salt, hash = django_salt_hash.split("$")
    assert hash_typ == "sha1", "hash typ not supported!"
    assert len(hash) == HASH_LEN, "Wrong hash length! (Not a SHA1 hash?)"

    # Split the SHA1-Hash in two pieces
    sha_a = hash[:(HASH_LEN / 2)]
    sha_b = hash[(HASH_LEN / 2):]

    sha_a = unicode(sha_a)
    sha_b = unicode(sha_b)
    sha_checksum = encrypt(txt=sha_a, key=sha_b)

    return salt, sha_checksum

def make_sha_checksum2(raw_password):
    """
    Create a SHA1-JS-Login checksum from a plaintext password.

    >>> make_sha_checksum2("test")
    ('DEBUG', u'crypt 790f2ebcb902c966fb0e with 232515ec1319dc9118af')
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


def check_js_sha_checksum(challenge, sha_a2, sha_b, sha_checksum):
    """
    Check a PyLucid JS-SHA-Login

    >>> salt1 = "a salt value"
    >>> challenge = "debug"
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
    >>> sha_a2 = make_hash(sha_a, challenge)
    >>> sha_a2
    '0d96f2fdda9c6f633ba0f5c2619aa7706abc492d'
    >>>
    >>> check_js_sha_checksum(challenge, sha_a2, sha_b, sha_checksum)
    True
    """
    sha_checksum = unicode(sha_checksum)
    sha_b = unicode(sha_b)

    encrypted_checksum = decrypt(sha_checksum, sha_b)
    client_checksum = make_hash(encrypted_checksum, challenge)

    if client_checksum == sha_a2:
        return True

    return False




def _doc_test(verbose):
    global DEBUG
    DEBUG = True

    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == "__main__":
    _doc_test(verbose=False)
#    _doc_test(verbose=True)
    print "DocTest end."
