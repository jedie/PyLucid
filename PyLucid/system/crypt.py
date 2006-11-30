#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
encryption for userpassword
"""

__version__ = "v0.0.1"

__history__ = """
v0.0.1
    - erste Version
"""



import md5, random, base64


# Soll verschlüsselten Daten mit base64 encodiert werden?
USE_BASE64 = True


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
    txt=str(hash(txt))+"_"+txt

    txt = crypten(txt, password)

    if USE_BASE64:
        txt=base64.encodestring(txt).replace("\n","")

    return txt

def decrypt(txt, password):
    "String >txt< mittels password entschlüsseln"
    if USE_BASE64:
        txt=base64.decodestring(txt)

    txt = crypten(txt, password)

    # Hashwert testen
    try:
        hash_value, txt = txt.split("_", 1)
        if hash_value != str(hash(txt)):
            raise ValueError("hash-test incorrect")
    except:
        raise ValueError("hash-test failed")

    return txt




if __name__=="__main__":

    print "-===Lokaler Test===-"

    import time

    password = str(time.time())

    asciitest = "".join([chr(i) for i in xrange(0,255)])

    print "ASCII-test:"

    encryptedString = encrypt(asciitest, password)
    print "encryptedString:",encryptedString

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
    print "decrypteddtring:",decrypt(encryptedString, password)








