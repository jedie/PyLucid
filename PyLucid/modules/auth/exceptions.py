#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Abwicklung von Login/Logout


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""


class AuthError(Exception):
    pass

class LogInError(AuthError):
    pass

class PasswordError(AuthError):
    pass

class SetNewPassError(AuthError):
    pass