#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    PyLucid SHA JS Login - Test
    ~~~~~~~~~~~~~~~~

    Pseudo test code
    It's good for documentation ;)

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyright: 2007 by Jens Diemer
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

from sha import new as sha_new

def sha(txt):
    return sha_new(txt).hexdigest()

def encrypt(txt, key): # Pseudo encrypt
    return "encrypted %s with %s" % (txt, key)

def decrypt(txt, key): # Pseudo decrypt
    txt, _, key2 = txt.split(" ", 3)[1:]
    assert key == key2
    return txt

print "\n\n------------ 1. Ein neuer User in der DB anlegen------------"
print "\n 1.1. Server sendet salt zum Client:",
salt = "salt_123"
print "'%s'" % salt

print "\n 1.2. Eingabe des Passwortes auf dem Client:",
password = "Passwort"
print "'%s'" % password

print "\n 1.3. sha(password + salt):",
sha_hash = sha(password + salt)
#test = "sha$1234$" + sha_hash
#print
#print test
#print len(test)
print "'%s'" % sha_hash

print "\n 1.4. Übermittlung der SHA-1 Summe zum Server."

print "\n\n------------ 2. speichern des Users auf dem Server------------"

print "\n 2.1. Server trennt die SHA-1 in:",
sha_a = sha_hash[:20]
sha_b = sha_hash[20:]
print "sha_a: '%s' sha_b: '%s'" % (sha_a, sha_b)

print "\n 2.2. encrypt(sha_a, key=sha_b):",
sha_checksum = encrypt(sha_a, key=sha_b)
print "'%s'" % sha_checksum

print "\n 2.3. Speichern nur der verschlüsselten Checksum + salt\n"

print "_______________________________________________________________________"

print "\n\n------------ 3. Login eines Users------------"

print "\n 3.1. Server sendet salt '%s' + challenge zum client:" % salt,
challenge = "c_123"
print "'%s'" % challenge

print "\n 3.2. Eingabe des Passwortes auf dem Client:",
password = "Passwort"
print "'%s'" % password

print "\n 3.3. sha(password + salt):",
sha_hash = sha(password + salt)
print "'%s'" % sha_hash

print "\n 3.4. trennen der SHA-1 in:",
sha_a = sha_hash[:20]
sha_b = sha_hash[20:]
print "sha_a: '%s' sha_b: '%s'" % (sha_a, sha_b)

print "\n 3.5. sha_a2 = sha(sha_a + challenge):",
sha_a2 = sha(sha_a + challenge)
print "'%s'" % sha_a2

print "\n 3.6. Übermittlung von sha_a2 und sha_b."

print "\n\n------------ 4. check auf dem Server------------"

print "\n 4.1. aus der DB sha_checksum: '%s'" % sha_checksum

print "\n 4.2. decrypt(sha_checksum, key=sha_b):",
sha_checksum = decrypt(sha_checksum, key=sha_b)
print "'%s'" % sha_checksum

print "\n 4.3. sha(sha_checksum + challenge):",
sha_check = sha(sha_checksum + challenge)
print "'%s'" % sha_check
print "\n 4.4. Vergleich: %s == %s" % (sha_check, sha_a2)
