===============
 about PyLucid
===============

PyLucid is a Open Source web content management system written in Python using `Django, jQuery and many more external software... <http://www.pylucid.org/permalink/41/dependencies-and-copyrights>`_

Some PyLucid Features are:

- Open Source (GPL v3 or later)

- `fully customizable output <http://www.pylucid.org/permalink/69/customise-PyLucid/>`_

  - templates/styles/JS code online editable with CodeMirror highlighting
  - `easy overwrite templates <http://www.pylucid.org/permalink/279/how-to-change-a-plugin-template>`_

- Multi site support (Allows a single installation to serve multiple websites.)
- internationalization and localization support (Multilingual content)
- Revision controlled content
- WYSIWYG html Editor / markups: Creole, textile, markdown, ReStructuredText
- expandable with plugins
- some built in plugins:

  - `secure JS-SHA Login <http://www.pylucid.org/permalink/42/secure-login-without-https>`_

  - content:

    - `weblog <http://www.pylucid.org/permalink/141/blog>`_ (Complete blogging solution)
    - `comments / guestbook <http://www.pylucid.org/permalink/351/the-comments-plugin-also-usefull-as-guestbook>`_ (comments for pages, blog articles, lexicon entries)
    - `StreetMap <http://www.pylucid.org/permalink/295/the-streetmap-plugin>`_ (insert google maps or OpenStreetMaps)
    - `lexicon <http://www.pylucid.org/permalink/301/the-lexicon-plugin>`_ (explane words in content)
    - `RSS <http://www.pylucid.org/permalink/123/includes-rss-newsfeeds>`_ (include external feeds into a page)
    - `source code <http://www.pylucid.org/permalink/309/highlight-source-code>`_ (include highlighted source code into content)
    - `simple picture gallery <http://www.pylucid.org/permalink/340/pylucid-screenshots>`_

  - navigation:

    - basics: main menu (split able), sub menu and sitemap
    - `search engine <http://www.pylucid.org/permalink/43/about-pylucid-integrated-search-engine>`_ (search in page content, blog articles, lexicon entries)
    - `update journal <http://www.pylucid.org/permalink/311/the-update-journal-plugin>`_ (List of all page updates)
    - `page tag based navigation <http://www.pylucid.org/permalink/131/the-tag-navigation-plugin>`_
    - `breadcrumb <http://www.pylucid.org/permalink/294/the-breadcrumb-plugin>`_
    - `Table of contens <http://www.pylucid.org/permalink/303/table-of-contens-plugin>`_ (TOC from page headlines)

  - content helpers:

    - `bulk editor <http://www.pylucid.org/permalink/357/bulk_editor>`_
    - `find and replace <http://www.pylucid.org/permalink/129/the-find-and-replace-plugin>`_ (replace strings different contents)
    - translation dialogue, used google translation service (optional)

- hierarchy tree page organization
- support many database engines (PostgreSQL, MySQL, Oracle and SQLite)
- WSGI conform: CGI, fastCGI, mod_Python and others
- and many more features... :)

=========
 install
=========

You can choose between a easy `"standalone package" <http://www.pylucid.org/permalink/331/install-pylucid-standalone-package>`_ or create a own `virtual environment
<http://www.pylucid.org/permalink/135/install-pylucid-in-a-virtual-environment>`_.

Pros and cons about the two installation kinds, read: `How to install PyLucid. <http://www.pylucid.org/permalink/70/how-to-install-pylucid>`_

=====================
 virtual environment
=====================

To create a PyLucid virtual environment, use our bootstrap script:

::

  ~$ wget http://github.com/jedie/PyLucid-boot/raw/master/pylucid_boot/pylucid-boot.py
  ~$ python pylucid-boot.py ~/PyLucid_env

Please read instructions here: `install PyLucid in a virtual environment
<http://www.pylucid.org/permalink/135/install-pylucid-in-a-virtual-environment>`_


====================
 Standalone package
====================

You can download the standalone package here:

- `sourceforge.net/projects/pylucid/files/ <http://sourceforge.net/projects/pylucid/files/>`_
- `github.com/jedie/PyLucid/downloads <http://github.com/jedie/PyLucid/downloads>`_

Please read instructions here: `install PyLucid standalone package <http://www.pylucid.org/permalink/331/install-pylucid-standalone-package>`_

=======
 links
=======

Homepage
  http://www.pylucid.org
Forum
  http://forum.pylucid.org/
IRC
  `#pylucid on freenode.net <http://www.pylucid.org/permalink/304/join-pylucid-irc-channel-via-webchat>`_
Sourcode and bug tracker
  http://github.com/jedie/PyLucid
Sourceforge
  http://sourceforge.net/projects/pylucid/