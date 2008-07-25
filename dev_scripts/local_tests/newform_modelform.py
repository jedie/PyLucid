#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A local django test with synced database but empty tables.
"""

from setup import setup
setup(
    path_info=False, extra_verbose=False,
    syncdb=True, insert_dump=False
)

#______________________________________________________________________________
# Test:


from django import newforms as forms
from django.contrib.auth.models import User

# Create some test users:
for i in xrange(1,6):
    new_user = User(username="test%s" % i, email="test%s@invalid.org" % i)
    new_user.save()

print User.objects.all()

print "-"*80

class UsersForm(forms.Form):
    user_list = forms.ChoiceField()

    def __init__(self, users):
        super(UsersForm,self).__init__()

        choices = []
        for user in users:
            id = user.pop("id")
            user_info = ["%s: %s" % (k,v) for k,v in user.iteritems()]
            user_info = ", ".join(user_info)
            choices.append((id, user_info))

        self.fields['user_list'].widget=forms.CheckboxSelectMultiple(
            choices=choices
        )

users = User.objects.values(
    "id", "username", "first_name", "last_name", "email"
)

users_form = UsersForm(users)

for field in users_form:
    for i in dir(field):
        print i
    print field.auto_id
    print field.html_name

html = users_form.as_p()
print html

