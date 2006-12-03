#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
encryption for userpassword

based on http://www.python-forum.de/viewtopic.php?p=7127#7127

Created by Jens Diemer
Modified by Christopher Grebs


ToDo:
    Better handling unicode and not unicode data
"""



import md5, random, base64, bz2, time



CHARSET = "utf-8"



def crypten(txt, password):
    """
    einfache XOR Verschlüsselung
    """
    password = md5.new(password).digest()
    maxSeedLen  = len(password)

    i = 0
    crypted = []
    for a in txt:
        if i >= maxSeedLen:
            i = 0

        rnd=random.Random(password[i]).randint(0, 127)
        crypted.append(chr(ord(a) ^ rnd))
        i += 1

    return "".join(crypted)


#_____________________________________________________________________________


def encrypt(txt, password, use_base64=True, use_bz2=False):
    """
    String >txt< mit >password< verschlüsseln
    use_base64  - verschlüsselter String wird mit base64 encodiert
    use_bz2     - die Daten werden mit bz2 komprimiert
    """
    # ''txt'' in utf-8 umwandeln --> BugFix (http://pylucid.net/trac/ticket/52)
    if isinstance(txt, unicode):
        txt = txt.encode(CHARSET)
    if isinstance(password, unicode):
        password = password.encode(CHARSET)

    # Hash-Wert hinzufügen
    checksum = md5.new(txt).digest()
    #~ print "encrypt checksum:", checksum

    txt = "".join([checksum, txt])

    if use_bz2:
        #~ print len(txt), txt
        txt = bz2.compress(txt, 9)
        #~ print len(txt), txt

    txt = crypten(txt, password)

    if use_base64:
        txt=base64.encodestring(txt).replace("\n","")

    return txt


#_____________________________________________________________________________


def __md5sum_test(txt):
    """
    md5 checksum testen und value ohne md5sum zurück liefern
    """
    try:
        checksum = txt[:16]
        txt = txt[16:]
    except Exception, e:
        raise WrongChecksum("checksum split failed (%s)" % e)

    try:
        hast_test = checksum == md5.new(txt).digest()
    except Exception, e:
        raise WrongChecksum("checksum test failed (%s)" % e)
    else:
        if hast_test != True:
            #~ print checksum, "-", md5.new(txt).digest()
            raise WrongChecksum("checksum incorrect")

    return txt


def __old_hast_test(txt):
    """
    Testet den veralteten hast() test
    """
    try:
        hash_value, txt = txt.split("_", 1)
    except Exception, e:
        raise WrongChecksum("hash value split failed (%s)" % e)

    try:
        if hash_value != str(hash(txt)):
            raise WrongChecksum("hash-test incorrect")
    except Exception, e:
        raise WrongChecksum("hash test failed (%s)" % e)

    return txt


def decrypt(txt, password, use_base64=True, use_bz2=False):
    """
    String >txt< mittels password entschlüsseln
    """
    if use_base64:
        try:
            txt=base64.decodestring(txt)
        except Exception, e:
            raise WrongChecksum("base64 decoding error: %s" % e)

    txt = crypten(txt, password)

    if use_bz2:
        try:
            txt = bz2.decompress(txt)
        except IOError, e:
            raise WrongChecksum("bz2 decompress error: %s" % e)

    try:
        txt = __md5sum_test(txt)
    except:
        # Pass passwort ist entweder falsch, oder die Daten wurde noch mit dem
        # alten hast() verfahren gespeichert.
        txt = __old_hast_test(txt)
        #~ print "Note: old hash() implementation used!"

    return txt


#_____________________________________________________________________________


class WrongChecksum(Exception):
    pass





#_____________________________________________________________________________
# TESTS:





def __get_ascii_testdata__():
    test_string    = "".join([chr(i) for i in xrange(128)])
    password       = "".join([chr(i) for i in xrange(0, 128, 128 / 19)])
    return test_string, password

def __test_old_decrypt__():
    print "__________________________________________________________________"
    print "\told decrypt implementation test:"

    test_string, password = __get_ascii_testdata__()

    # Bei alten encrypteten Strings wurde hash() zur Überprüfung genommen.
    old_crypt_value = (
        "aAsQBAlzDisjZ3w2JXU3G0A/Iz43SDYVH18sJjVlJwtQLzMuJ1gmBQ9PPBYFVRc7YB8D"
        "HhdoFjU/fwwGFUUHK3APEw4HeAYlL28cdmU1d1sAf2N+dwh2VV8fbGZ1JWdLEG9zbmcY"
        "ZkVPD3xWRRVXeyBfQ15XKFZ1fz9MRlUFR2swT1NORzhGZW8vXA=="
    )
    print "Test Data ok:", \
    "e0ef6a55ff0742bc88cc4631c88a8998" == md5.new(old_crypt_value).hexdigest()

    d = decrypt(old_crypt_value, password, use_bz2=False)
    print "encrypt test:", d == test_string



def __test_ascii__(use_base64, use_bz2):
    print "__________________________________________________________________"
    print "\tASCII-test (use_base64=%s, use_bz2=%s):" % (
        use_base64, use_bz2
    )

    test_string, password = __get_ascii_testdata__()

    e = encrypt(test_string, password, use_base64, use_bz2)
    d = decrypt(e, password, use_base64, use_bz2)
    print "test:", d == test_string



def __test_utf8__():
    """
    Test mit UTF-8 Daten
    """
    print "__________________________________________________________________"
    print "\tunicode test:"

    # ein 60 Zeichen langes passwort erstellen:
    password = u"".join([unichr(i) for i in xrange(0, 65535, 65535 / 59)])
    password = password.encode("UTF-8")
    # unicode String aus allen Zeichen erstellen
    test_string = u"".join([unichr(i) for i in xrange(65535)])
    test_string = test_string.encode("UTF-8")

    print "Testing a %0.2f KBytes UFT-8 String..." % (len(test_string)/1024.0)

    start_time = time.time()

    e = encrypt(test_string, password, use_base64=False, use_bz2=False)
    print "encrypt test 1:",
    print "be4544ddd25e1068e697062d169790fd" == md5.new(e).hexdigest()
    d = decrypt(e, password, use_base64=False, use_bz2=False)
    print "decrypt test 1:", d == test_string

    print "duration: %0.1fSec." % (time.time()-start_time)


def __test_checksum__(use_base64, use_bz2):
    print "__________________________________________________________________"
    print "\tchecksum test (use_base64=%s, use_bz2=%s):" % (
        use_base64, use_bz2
    )

    test_string, password = __get_ascii_testdata__()

    encrypted = encrypt(test_string, password, use_base64, use_bz2)


    class TestFailed(Exception):
        pass


    def test(encrypted, password):
        try:
            d = decrypt(encrypted, password, use_base64, use_bz2)
        except WrongChecksum:
            # OK, die Checksumme ist falsch.
            return

        print "Fail, the checksum is ok?!?!?"

        if d == test_string:
            # Die Daten stimmen, obwohl das Passwort falsch ist???
            print "The data encypted ok!!!"

        raise TestFailed()


    # Falsches Passwort
    print "invalid password test:",
    try:
        for i in xrange(len(password)):
            invalid_pass = password[:i] + "_" + password[i+1:]
            test(encrypted, invalid_pass)
    except TestFailed:
        print "failed!"
    else:
        print "OK"

    # Falsche Daten
    print "invalid data test:",
    try:
        for i in xrange(len(encrypted)):
            invalid_data = encrypted[:i] + "_" + encrypted[i+1:]
            test(invalid_data, password)
    except TestFailed:
        print "failed!"
    else:
        print "OK"



def __test__(method):
    "Methode in allen Varianten testen"
    method(use_base64=False, use_bz2=False)
    method(use_base64=True , use_bz2=False)
    method(use_base64=False, use_bz2=True )
    method(use_base64=True , use_bz2=True )


def __test_all__():
    __test_old_decrypt__()
    __test__(__test_ascii__)
    __test_utf8__()
    __test__(__test_checksum__)


def __profile__():
	import profile
	#~ profile.run('__test_all__()')
	profile.run('__test_utf8__()')


if __name__=="__main__":
    print "-=== Local Test ===-"

    password       = "".join([chr(i) for i in xrange(0, 128, 128 / 19)])
    test_string    = "".join([chr(i) for i in xrange(128)])

    __test_all__()
    #~ __profile__()









