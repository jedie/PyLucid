#-*- coding: utf-8 -*-

"""
    PyLucid.models
    ~~~~~~~~~~~~~~
    
    The new v0.9 models. Contains only the page model!

    This is only a playground for developers.


    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: $

    :copyleft: 2007-2008 by the PyLucid team, see AUTHORS for more details.
"""


class Page(models.Model):
    """
    All cms page data how are language independent.
    """
    # Explicite id field, so we can insert a help_text ;)
    id = models.AutoField(primary_key=True, help_text="The internal page ID.")

    parent = models.ForeignKey(
        "self", null=True, blank=True,
        to_field="id", help_text="the higher-ranking father page",
    )
    position = models.IntegerField(
        default = 0,
        help_text = "ordering weight for sorting the pages in the menu."
    )

    name = models.CharField(
        max_length=150, help_text="A short page name (language independent)"
    )
    shortcut = models.CharField(
        unique=True, max_length=150, help_text="shortcut to built the URLs"
    )

    template = models.ForeignKey(
        "Template", to_field="id", help_text="the used template for this page"
    )
    style = models.ForeignKey(
        "Style", to_field="id", help_text="the used stylesheet for this page"
    )
    markup = models.IntegerField(
        db_column="markup_id", # Use the old column name.
        max_length=1, choices=MARKUPS,
        help_text="the used markup language for this page",
    )


class Language(models.Model):
    """
    All available Languages
    """
    lang_code = models.CharField(
        unique=True, max_length=5,
        help_text="lang code like 'en', 'de' or 'es-ar'"
    )


class PageContent(models.Model):
    """
    language specific page data.
    """
    page = models.ForeignKey(Page)
    lang = models.ForeignKey(Language)

    title = models.CharField(
        blank=True, max_length=150, help_text="A long page title"
    )
    content = models.TextField(blank=True, help_text="The CMS page content.")

    keywords = models.CharField(
        blank=True, max_length=255,
        help_text="Keywords for the html header. (separated by commas)"
    )
    description = models.CharField(
        blank=True, max_length=255,
        help_text="Short description of the contents. (for the html header)"
    )

