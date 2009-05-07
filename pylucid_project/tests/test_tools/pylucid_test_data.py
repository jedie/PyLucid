# coding:utf-8

from django.http import HttpRequest
from django.contrib.auth.models import User#, AnonymousUser
from django.contrib.sites.models import Site#


from dbtemplates.models import Template

from pylucid.models import PageTree, PageMeta, PageContent, Design, EditableHtmlHeadFile


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

TEST_TEMPLATES = {
    "site_template/mini1.html": {
        "content": \
"""<html><head><title>{{ page_title }}</title>
<meta name="robots"          content="{{ robots }}" />
<meta name="keywords"        content="{{ page_keywords }}" />
<meta name="description"     content="{{ page_description }}" />
<meta name="DC.Date"         content="{{ page_lastupdatetime|date:_("DATETIME_FORMAT") }}" />
<meta name="DC.Date.created" content="{{ page_createtime|date:_("DATETIME_FORMAT") }}" />
<link rel="canonical" href="{{ page_get_permalink }}" />
{% lucidTag head_files %}
</head>
<body>
{% lucidTag main_menu %}
{% lucidTag search %}
<!-- page_messages -->
{% lucidTag admin_menu %}
<!-- ContextMiddleware breadcrumb -->
{% lucidTag language %}
{% block content %}
    {{ page_content }}
{% endblock content %}
<a href="{{ page_get_permalink }}" title="permalink to this page">permalink</a>

powered by {{ powered_by }}
{{ login_link }}
<!-- script_duration -->
last modified: {{ page_lastupdatetime|date:_("DATETIME_FORMAT") }}
</body></html>"""
        }
}
TEST_HEADFILES = {
    "unittest/test.css": {
        "description": "CSS file for unittests.",
        "content": ".test { color:red;}",
    }
}
TEST_DESIGNS = {
    "unittest_design1": {
        "template_name": "site_template/mini1.html",
        "headfiles": ("unittest/test.css",),
    }
}



def get_user(usertype):
    return User.objects.get(username=TEST_USERS[usertype]["username"])

def create_testusers():
    """
    Create all available testusers.
    """
    def create_user(username, password, email, is_staff, is_superuser):
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
        
    for usertype, userdata in TEST_USERS.iteritems():
        create_user(**userdata)


def create_templates(template_dict, site):
    """ create templates in dbtemplates model """
    template_map = {}
    for template_name, data in template_dict.iteritems():
        template, created = Template.objects.get_or_create(
            name = template_name, defaults = data
        )
        template.save()
        template.sites.add(site)
        template_map[template_name] = template
        if created:
            print("template '%s' created." % template_name)
        else:
            print("template '%s' exist." % template_name)
    return template_map


def create_headfiles(headfile_dict, request):
    headfile_map = {}
    for filename, data in headfile_dict.iteritems():    
        headfile, created = EditableHtmlHeadFile.objects.get_or_create(
            request, filename = filename, defaults = data
        )
        headfile.save(request)
        headfile_map[filename] = headfile
        if created:
            print("EditableStaticFile '%s' created." % filename)
        else:
            print("EditableStaticFile '%s' exist." % filename)
    return headfile_map


def create_design(design_dict, request, template_map, headfile_map):   
    design_map = {}
    for design_name, data in design_dict.iteritems():
        template_name = data["template_name"]
        assert template_name in template_map
        design, created = Design.objects.get_or_create(request,
            name = design_name, defaults = {"template": template_name,}
        )
        if created:
            print("design '%s' created." % design_name)
            # Add headfiles
            for filename in data["headfiles"]:
                headfile = headfile_map[filename]
                design.headfiles.add(headfile)
                print("Add headfile '%s'." % headfile)
            design.save(request)
        else:
            print("Design '%s' exist." % design_name)
            
        
        design_map[design_name] = design
    return design_map



def create_pylucid_test_data(site=None):
    """ create complete test data for "running" PyLucid """
    create_testusers()
    
    request = HttpRequest()
    request.user = get_user(usertype="superuser")
    
    if site==None:
        site = Site.objects.get_current()
           
    template_map = create_templates(TEST_TEMPLATES, site)
    headfile_map = create_headfiles(TEST_HEADFILES, request)
    design_map = create_design(TEST_DESIGNS, request, template_map, headfile_map)
