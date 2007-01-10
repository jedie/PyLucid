#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""


import time, random


class AuthData(object):
    def __init__(self, seed=None):
        self.seed = seed
        self.reset()

    def _get_a_rnd_number(self):
        seed = "%s%s" % (time.clock(), self.seed)
        return random.Random(seed).randint(10000,99999)

    def make_new_salt(self):
        self.salt = self._get_a_rnd_number()

    def make_new_challenge(self):
        self.challenge = self._get_a_rnd_number()

    def reset(self):
        """
        Alle Werte auf default setzen
        """
        self.md5username = None
        self.salt = None
        self.challenge = None