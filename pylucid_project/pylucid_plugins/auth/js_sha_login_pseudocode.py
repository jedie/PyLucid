#!/usr/bin/env python
# coding: utf-8

"""
    Pseudo code of the JS-SHA-Login.
    (output is in creole markup)
    more info:
    http://www.pylucid.org/permalink/42/secure-login-without-https
"""

import hashlib


def sha1(txt):
    return hashlib.sha1(txt).hexdigest()

def encrypt(txt, key): # Pseudo encrypt
    return "encrypted %s with %s" % (txt, key)

def decrypt(txt, key): # Pseudo decrypt
    txt, _, key2 = txt.split(" ", 3)[1:]
    assert key == key2
    return txt

LOOP_COUNT = 2


print "\n\n=== 1. Create a new User ===\n"
print "# Client get's new, random **user salt** from server:",
salt = "s_123"
print "'//%s//'" % salt

print "# Password input on the client:",
password = "client_password"
print "'//%s//'" % password

print "# sha1(password + salt):",
sha1sum = sha1(password + salt)
print "'//%s//'" % sha1sum

print "# Client send **sha1** hash to the server."



print "\n\n==== 2. Save user data ====\n"

print "# Server split sha1 values:",
sha1_a = sha1sum[:16]
sha1_b = sha1sum[16:]
print "**sha1_a**: '//%s//' **sha1_b**: '//%s//'" % (sha1_a, sha1_b)

print "# {{{encrypt(sha1_a, key=sha1_b)}}}:",
sha1checksum = encrypt(sha1_a, key=sha1_b)
print "'//%s//'" % sha1checksum

print "# Save only the **encrypted string** + **user salt**\n"



print "----"



print "\n\n=== 3. Login ===\n"

print "# Client request login and get's a random **challenge** from server:",
challenge = "c_123"
print "'//%s//'" % challenge

print "# User enters username and password: '//%s//'" % password

print "# Client send username and get's **user salt** from server via AJAX: '//%s//'" % salt

print "# on the client: {{{sha1(password + salt)}}}:",
sha1sum = sha1(password + salt)
print "'//%s//'" % sha1sum

print "# on the client: split sha1 in:",
sha1_a = sha1sum[:16]
sha1_b = sha1sum[16:]
print "**sha1_a**: '//%s//' **sha1_b**: '//%s//'" % (sha1_a, sha1_b)

print "# client generate a **cnonce** e.g.: {{{cnonce = sha_hexdigest(new Date().getTime() + Math.random() + ...)}}}"
cnonce = "client_SHA1_nonce"

print "# client generate **sha1_a** with e.g.: {{{sha1(sha_a, i, challenge, cnonce) x loop count}}}: \\\\",
for i in range(LOOP_COUNT):
    sha1_a = hashlib.sha1("%s%s%s%s" % (sha1_a, i, challenge, cnonce)).hexdigest()
print "'//%s//'" % sha1_a

print "# Client send **username**, **sha1_a2**, **sha1_b** and **cnonce** to the server."



print "\n\n==== 4. validation on the server ====\n"

print "# get encrypted **checksum** for user: '//%s//'" % sha1checksum

print "# {{{decrypt(sha1checksum, key=sha1_b)}}}:",
sha1checksum = decrypt(sha1checksum, key=sha1_b)
print "'//%s//'" % sha1checksum

print "# server-site {{{sha1(sha1checksum, i, challenge, cnonce) x loop count}}}:",
for i in range(LOOP_COUNT):
    sha1checksum = hashlib.sha1("%s%s%s%s" % (sha1checksum, i, challenge, cnonce)).hexdigest()
print "'//%s//'" % sha1checksum

print "# compare **client site generated** SHA1 with the **server site generated**: \\\\",
print "//%s// == //%s//" % (sha1checksum, sha1_a)
