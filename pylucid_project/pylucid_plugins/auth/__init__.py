# -*- coding: utf-8 -*-

from django.contrib.admin import AdminSite

# Change the template for django's normal login.
# So we can insert a link to JS-SHA-Login.
AdminSite.login_template = "auth/django_login.html"
