#!/usr/bin/env python
# coding: utf-8

"""
    Pseudo code of the JS-SHA-Login.
    (output is in creole markup)
    more info:
    http://www.pylucid.org/permalink/42/secure-login-without-https
"""

try:
    from hashlib import sha1 as sha_constructor
except ImportError:
    from sha import new as sha_constructor

def sha1(txt):
    return sha_constructor(txt).hexdigest()

def encrypt(txt, key): # Pseudo encrypt
    return "encrypted %s with %s" % (txt, key)

def decrypt(txt, key): # Pseudo decrypt
    txt, _, key2 = txt.split(" ", 3)[1:]
    assert key == key2
    return txt



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

print "# encrypt(sha1_a, key=sha1_b):",
sha1checksum = encrypt(sha1_a, key=sha1_b)
print "'//%s//'" % sha1checksum

print "# Save only encrypted **checksum** + **user salt**\n"



print "----"



print "\n\n=== 3. Login ===\n"

print "# Client request login and get's a random **challenge** from server:",
challenge = "c_123"
print "'//%s//'" % challenge

print "# User enters username and password: '//%s//'" % password

print "# Client send username and get's **user salt** from server via AJAX: '//%s//'" % salt

print "# on the client: sha1(password + salt):",
sha1sum = sha1(password + salt)
print "'//%s//'" % sha1sum

print "# on the client: split sha1 in:",
sha1_a = sha1sum[:16]
sha1_b = sha1sum[16:]
print "**sha1_a**: '//%s//' **sha1_b**: '//%s//'" % (sha1_a, sha1_b)

print "# on the client: **sha1_a2** = sha1(sha1_a + challenge):",
sha1_a2 = sha1(sha1_a + challenge)
print "'//%s//'" % sha1_a2

print "# Client send username, **sha1_a2** and **sha1_b** to the server."



print "\n\n==== 4. validation on the server ====\n"

print "# get encrypted **checksum** for user: '//%s//'" % sha1checksum

print "# decrypt(sha1checksum, key=sha1_b):",
sha1checksum = decrypt(sha1checksum, key=sha1_b)
print "'//%s//'" % sha1checksum

print "# sha1(sha1checksum + challenge):",
sha1check = sha1(sha1checksum + challenge)
print "'//%s//'" % sha1check

print "# compare: //%s// == //%s//" % (sha1check, sha1_a2)
