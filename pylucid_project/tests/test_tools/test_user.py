# coding:utf-8

from django.contrib.auth.models import User

TEST_USERS = {
    "superuser": {
        "username": "superuser",
        "email": "superuser@example.org",
        "password": "superuser_password",
        "is_staff": True,
        "is_superuser": True,
    },
    "staff": {
        "username": "staff test user",
        "email": "staff_test_user@example.org",
        "password": "staff_test_user_password",
        "is_staff": True,
        "is_superuser": False,
    },
    "normal": {
        "username": "normal test user",
        "email": "normal_test_user@example.org",
        "password": "normal_test_user_password",
        "is_staff": False,
        "is_superuser": False,
    },
}

def get_user(usertype):
    return User.objects.get(username=TEST_USERS[usertype]["username"])

def create_user(verbosity, username, password, email, is_staff, is_superuser):
    """
    Create a user and return the instance.
    """
    defaults = {'password':password, 'email':email}
    user, created = User.objects.get_or_create(
        username=username, defaults=defaults
    )
    if not created:
        user.email = email
    user.set_password(password)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.save()
    if verbosity >= 2:
        print "Test user %r created." % user
    return user

def create_testusers(verbosity):
    """
    Create all available testusers and UserProfiles
    """
    for usertype, userdata in TEST_USERS.iteritems():
        user = create_user(verbosity, **userdata)
