from md5 import new as md5_new


def md5(txt):
    return md5_new(txt).hexdigest()

def encrypt(txt, key): # Pseudo encrypt
    return "encrypted %s with %s" % (txt, key)

def decrypt(txt, key): # Pseudo decrypt
    txt, _, key2 = txt.split(" ", 3)[1:]
    assert key == key2
    return txt



print "\n\n------------ 1. Ein neuer User in der DB anlegen------------"
print "\n 1.1. Server sendet salt zum Client:",
salt = "s_123"
print "'%s'" % salt

print "\n 1.2. Eingabe des Passwortes auf dem Client:",
password = "Passwort"
print "'%s'" % password

print "\n 1.3. md5(password + salt):",
md5sum = md5(password + salt)
print "'%s'" % md5sum

print "\n 1.4. Übermittlung der MD5 Summe zum Server."



print "\n\n------------ 2. speichern des Users auf dem Server------------"

print "\n 2.1. Server trennt die MD5 in:",
md5_a = md5sum[:16]
md5_b = md5sum[16:]
print "md5_a: '%s' md5_b: '%s'" % (md5_a, md5_b)

print "\n 2.2. encrypt(md5_a, key=md5_b):",
md5checksum = encrypt(md5_a, key=md5_b)
print "'%s'" % md5checksum

print "\n 2.3. Speichern nur der verschlüsselten Checksum + salt\n"


print "_______________________________________________________________________"



print "\n\n------------ 3. Login eines Users------------"

print "\n 3.1. Server sendet salt '%s' + challenge zum client:" % salt,
challenge = "c_123"
print "'%s'" % challenge

print "\n 3.2. Eingabe des Passwortes auf dem Client:",
password = "Passwort"
print "'%s'" % password

print "\n 3.3. md5(password + salt):",
md5sum = md5(password + salt)
print "'%s'" % md5sum

print "\n 3.4. trennen der MD5 in:",
md5_a = md5sum[:16]
md5_b = md5sum[16:]
print "md5_a: '%s' md5_b: '%s'" % (md5_a, md5_b)

print "\n 3.5. md5_a2 = md5(md5_a + challenge):",
md5_a2 = md5(md5_a + challenge)
print "'%s'" % md5_a2

print "\n 3.6. Übermittlung von md5_a2 und md5_b."



print "\n\n------------ 4. check auf dem Server------------"

print "\n 4.1. aus der DB md5checksum: '%s'" % md5checksum

print "\n 4.2. decrypt(md5checksum, key=md5_b):",
md5checksum = decrypt(md5checksum, key=md5_b)
print "'%s'" % md5checksum

print "\n 4.3. md5(md5checksum + challenge):",
md5check = md5(md5checksum + challenge)
print "'%s'" % md5check

print "\n 4.4. Vergleich: %s == %s" % (md5check, md5_a2)