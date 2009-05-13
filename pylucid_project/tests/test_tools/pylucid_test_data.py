# coding:utf-8

from django.http import HttpRequest
from django.contrib.auth.models import User#, AnonymousUser
from django.contrib.sites.models import Site#


from dbtemplates.models import Template

from pylucid.models import PageTree, PageMeta, PageContent, Design, \
                                            EditableHtmlHeadFile, Language


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
TEST_PAGETREE = {
    1: {
        "parent": None,
        "slug": "firstpage",
        "description": "unittest page",
        "type": PageTree.PAGE_TYPE,
        "design": "unittest_design1",
    }
}
TEST_PAGEMETA = {
    1: {
        "en": {
            "title": "1. en page",
            "keywords": "keywords 1. en page",
            "description": "description 1. en page",
        },
        "de": {
            "title": "1. de Seite",
            "keywords": "keywords 1. de Seite",
            "description": "description 1. de Seite",
        },
    },
}
TEST_PAGECONTENT = {
    1: {
        "en": {
            "content": "<h1>1. en test page!</h1>",
            "markup": PageContent.MARKUP_HTML,
        },
        "de": {
            "content": "<h1>1. de test Seite!</h1>",
            "markup": PageContent.MARKUP_HTML,
        }
    }
}

def get_user(usertype):
    return User.objects.get(username=TEST_USERS[usertype]["username"])

def get_or_create_lang(lang_code):
    language, created = Language.objects.get_or_create(
        code=lang_code, defaults={"description": "%s - description" % lang_code}
    )
    if created:
        print("Language '%s' created." % lang_code)
    return language

def create_testusers(verbosity):
    """
    Create all available testusers.
    """
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
        if verbosity:
            print "Test user %r created." % user
        
    for usertype, userdata in TEST_USERS.iteritems():
        create_user(verbosity, **userdata)


def create_templates(verbosity, template_dict, site):
    """ create templates in dbtemplates model """
    template_map = {}
    for template_name, data in template_dict.iteritems():
        template, created = Template.objects.get_or_create(
            name = template_name, defaults = data
        )
        template.save()
        template.sites.add(site)
        template_map[template_name] = template
        if verbosity:
            if created:
                print("template '%s' created." % template_name)
            else:
                print("template '%s' exist." % template_name)
    return template_map


def create_headfiles(verbosity, headfile_dict, request):
    headfile_map = {}
    for filename, data in headfile_dict.iteritems():    
        headfile, created = EditableHtmlHeadFile.objects.get_or_create(
            request, filename = filename, defaults = data
        )
        headfile.save(request)
        headfile_map[filename] = headfile
        if verbosity:
            if created:
                print("EditableStaticFile '%s' created." % filename)
            else:
                print("EditableStaticFile '%s' exist." % filename)
    return headfile_map


def create_design(verbosity, design_dict, request, template_map, headfile_map):   
    design_map = {}
    for design_name, data in design_dict.iteritems():
        template_name = data["template_name"]
        assert template_name in template_map
        design, created = Design.objects.get_or_create(request,
            name = design_name, defaults = {"template": template_name,}
        )
        if created:
            if verbosity:
                print("design '%s' created." % design_name)
            # Add headfiles
            for filename in data["headfiles"]:
                headfile = headfile_map[filename]
                design.headfiles.add(headfile)
                if verbosity:
                    print("Add headfile '%s'." % headfile)
            design.save(request)
        else:
            if verbosity:
                print("Design '%s' exist." % design_name)
        
        design_map[design_name] = design
    return design_map


def create_pagetree(verbosity, pagetree_dict, request, site, design_map):
    pagetree_map = {}
    for id, defaults in pagetree_dict.iteritems():
        defaults["site"] = site
        design_name = defaults["design"]
        defaults["design"] = design_map[design_name]
        tree_entry, created = PageTree.objects.get_or_create(
            request, id = id, defaults = defaults
        )
        tree_entry.save(request)
        if verbosity:
            if created:
                print("PageTree '%s' created." % tree_entry.slug)
            else:
                print("PageTree '%s' exist." % tree_entry.slug)
        pagetree_map[id] = tree_entry
    return pagetree_map


def create_pagemeta(verbosity, pagemeta_dict, request, pagetree_map):
    pagemeta_map = {}
    for id, lang_data in pagemeta_dict.iteritems():
        tree_entry = pagetree_map[id]
        
        for lang_code, metadata in lang_data.iteritems():
            language = get_or_create_lang(lang_code)
            
            pagemeta_entry, created = PageMeta.objects.get_or_create(
                request, page = tree_entry, lang = language, defaults = metadata
            )
            pagemeta_entry.save(request)
            if verbosity:
                if created:
                    print("PageMeta '%s' - '%s' created." % (language, tree_entry.slug))
                else:
                    print("PageMeta '%s' - '%s' exist." % (language, tree_entry.slug))
            pagemeta_map["%s-%s" % (id, lang_code)] = pagemeta_entry
    return pagemeta_map


def create_pagecontent(verbosity, pagecontent_dict, request, pagetree_map, pagemeta_map):
    pagecontent_map = {}
    for id, lang_data in pagecontent_dict.iteritems():
        tree_entry = pagetree_map[id]
        
        for lang_code, pagecontent_data in lang_data.iteritems():
            language = get_or_create_lang(lang_code)
            pagemeta_entry = pagemeta_map["%s-%s" % (id, lang_code)]
            
            content_entry, created = PageContent.objects.get_or_create(request,
                page = tree_entry,
                lang = language,
                pagemeta = pagemeta_entry,
                defaults = pagecontent_data
            )
            content_entry.save(request)
            if verbosity:
                if created:
                    print("PageContent '%s' created." % content_entry)
                else:
                    print("PageContent '%s' exist." % content_entry)
            pagecontent_map["%s-%s" % (id, lang_code)] = content_entry
    return pagecontent_map


def create_pylucid_test_data(site=None, verbosity=True):
    """ create complete test data for "running" PyLucid """
    if verbosity:
        print "\nCreate complete test data for 'running' PyLucid"
        
    create_testusers(verbosity)
    
    request = HttpRequest()
    request.user = get_user(usertype="superuser")
    
    if site==None:
        site = Site.objects.get_current()
    if verbosity:
        print "use site: %r" % site
           
    template_map = create_templates(verbosity, TEST_TEMPLATES, site)
    headfile_map = create_headfiles(verbosity, TEST_HEADFILES, request)
    design_map = create_design(verbosity, TEST_DESIGNS, request, template_map, headfile_map)
    pagetree_map = create_pagetree(verbosity, TEST_PAGETREE, request, site, design_map)
    pagemeta_map = create_pagemeta(verbosity, TEST_PAGEMETA, request, pagetree_map)
    pagecontent_map = create_pagecontent(verbosity, TEST_PAGECONTENT, request, pagetree_map, pagemeta_map)

    if verbosity:
        print "Test database filled with test data."
        print