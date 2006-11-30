#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
encryption for userpassword

based on http://www.python-forum.de/viewtopic.php?p=7127#7127
"""



import md5, random, base64, bz2


# Soll verschlüsselten Daten mit base64 encodiert werden?
USE_BASE64 = True
#~ USE_BASE64 = False

# Sollen die zu verschlüsselde Daten komprimiert werden?
# Info: Macht in kombination mit base64 keinen Sinn, wenn Textdaten vorliegen!
#~ USE_BZ2 = True
USE_BZ2 = False


def crypten(txt, password):
    password = md5.new(password).digest()

    maxSeedLen  = len(password)
    crypted     = ""
    i           = 0

    for a in txt:
        if i >= maxSeedLen: i = 0

        rnd=random.Random(password[i]).randint(0, 127)

        crypted += chr(ord(a) ^ rnd)
        i += 1

    return crypted



def encrypt(txt, password):
    "String >txt< mit >password< verschlüsseln"
    txt=str(txt)

    # Hash-Wert hinzufügen
    checksum = md5.new(txt).digest()
    txt = checksum + txt

    if USE_BZ2:
        #~ print len(txt), txt
        txt = bz2.compress(txt, 9)
        #~ print len(txt), txt

    txt = crypten(txt, password)

    if USE_BASE64:
        txt=base64.encodestring(txt).replace("\n","")

    return txt

def decrypt(txt, password):
    "String >txt< mittels password entschlüsseln"
    if USE_BASE64:
        txt=base64.decodestring(txt)

    txt = crypten(txt, password)

    if USE_BZ2:
        txt = bz2.decompress(txt)

    # Hashwert testen
    try:
        checksum = txt[:16]
        txt = txt[16:]
    except Exception, e:
        raise ValueError("checksum split failed (%s)" % e)

    try:
        hast_test = checksum == md5.new(txt).digest()
    except Exception, e:
        raise ValueError("checksum test failed (%s)" % e)
    else:
        if hast_test != True:
            raise ValueError("checksum incorrect")

    return txt




if __name__=="__main__":

    print "-===Lokaler Test===-"

    import time

    password = str(time.time())

    asciitest = "".join([chr(i) for i in xrange(0,255)])

    print "ASCII-test:"

    encryptedString = encrypt(asciitest, password)
    print "encryptedString:",encryptedString
    print "encryptedString len:", len(encryptedString)

    if decrypt(encryptedString, password) == asciitest:
        print "Test OK!"
    else:
        print "Test failt!!!"


    print "-"*80
    print "fail test:"

    failedString = encryptedString[:1]
    try:
        decrypt(failedString, password)
    except Exception, e:
        print "Test OK! (%s)" % e
    else:
        print "Test failt!!!"


    print "-"*80

    teststring = "Das Modul funktioniert wohl! :) time:" + str(time.time())
    encryptedString = encrypt(teststring, password)
    print "encryptedString:",encryptedString
    print "encryptedString len:", len(encryptedString)
    print "decrypteddtring:",decrypt(encryptedString, password)








