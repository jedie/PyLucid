#!/usr/bin/python
# -*- coding: UTF-8 -*-

#___________________________________________________________________________________________________
# Meta-Angaben

__author__      = "Jens Diemer"
__url__         = "http://www.PyLucid.org"
__description__ = "PyBB a phpBB clone"
__long_description__ = """
This is just an experiment ;)
And not a complete Forumsoft...
"""

#___________________________________________________________________________________________________

internal_pages = [
{
    "name"          : "summary",
    "description"   : "The summary of the Forum",
    "category"      : "PyBB",
    "markup"        : "TAL",
    "content"       : """<p class="nav">
<a tal:attributes="href back_link/url;title back_link/name" tal:content="back_link/name"></a></p>
<table id="forum_summary">
<tr class="headline">
    <th>Nr</th>
    <th>Themen</th>
    <th>Antworten</th>
    <th>Author</th>
    <th>Aufrufe</th>
    <th>Letzter Beitrag</th>
</tr>
<tr tal:repeat="topics table">
    <td tal:content="repeat/topics/number"></td>
    <td tal:content="topics/topic_title"></td>
    <td tal:content="topics/topic_replies"></td>
    <td><a tal:attributes="href topics/link;title topics/name" tal:content="topics/name"></a></td>
    <td tal:content="topics/topic_views"></td>
    <td>
        <p>
            <b tal:replace="topics/last_post_time"></b><br />
            <a tal:attributes="href topics/link;title topics/name" tal:content="topics/name"></a>
        </p>
    </td>
</tr>
</table>"""
},
{
    "name"          : "view_forum",
    "description"   : "View posts from one forum.",
    "category"      : "PyBB",
    "markup"        : "TAL",
}]

#___________________________________________________________________________________________________

styles = [
{
    "name"          : "PyBB",
    "description"   : "PyBB module styles",
}]

#___________________________________________________________________________________________________

SQL_install_commands = [
"""CREATE TABLE `$tableprefix$_test1` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  `realname` varchar(50) NOT NULL default '',
  `email` varchar(50) NOT NULL default '',
  `pass1` varchar(32) NOT NULL default '',
  `pass2` varchar(32) NOT NULL default '',
  `admin` tinyint(4) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
);""",
"""CREATE TABLE `test2` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  `title` varchar(50) default NULL,
  `parent` int(11) NOT NULL default '0',
  `position` int(11) NOT NULL default '0',
  `template` int(11) NOT NULL default '0',
  `style` int(11) NOT NULL default '0',
  `datetime` datetime default NULL,
  `markup` varchar(50) default NULL,
  `content` text,
  `keywords` varchar(255) default NULL,
  `description` varchar(255) default NULL,
  `lastupdatetime` datetime default NULL,
  `lastupdateby` int(11) default NULL,
  `showlinks` tinyint(4) NOT NULL default '1',
  `permitViewPublic` tinyint(4) NOT NULL default '1',
  `permitViewGroupID` int(11) default NULL,
  `ownerID` int(11) NOT NULL default '0',
  `permitEditGroupID` int(11) default NULL,
  PRIMARY KEY  (`id`)
);"""
]

#___________________________________________________________________________________________________

SQL_deinstall_commands = [
    "DROP TABLE `$tableprefix$_test1`;",
    "DROP TABLE `test2`;",
]

#___________________________________________________________________________________________________
# Module-Manager Daten

#~ module_manager_debug = True
module_manager_debug = False

module_manager_data = {
    "lucidTag" : {
        "must_login"    : False,
        "must_admin"    : False,
    },
    "print_summary" :{
        "must_login"    : False,
        "must_admin"    : False,
    },
    "view_forum": {
        "must_login"    : False,
        "must_admin"    : False,
        "get_CGI_data"  : {"forum_id": int},
    },
}

#_______________________________________________________________________

