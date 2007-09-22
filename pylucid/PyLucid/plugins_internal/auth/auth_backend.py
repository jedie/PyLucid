

from PyLucid.tools import crypt
from django.contrib.auth.backends import ModelBackend

class JS_SHA_Backend(ModelBackend):
    def authenticate(self, user=None, challenge=None, sha_a2=None, sha_b=None,
                                                            sha_checksum=None):
        if user == None:
            # Nothing to do: Normal auth?
            return None

        check = crypt.check_js_sha_checksum(
            challenge, sha_a2, sha_b, sha_checksum
        )
        if check == True:
            return user