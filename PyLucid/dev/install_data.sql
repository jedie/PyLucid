-- ------------------------------------------------------
-- Dump created 10.01.2006, 09:23 with PyLucid's MySQLdump.py v0.3
--
-- Linux - PIII700 - 2.6.12-10-686 - #1 Thu Dec 22 11:55:07 UTC 2005 - i686
-- Python v2.4.2 (#2, Sep 30 2005, 21:19:01) [GCC 4.0.2 20050808 (prerelease) (Ubuntu 4.0.1-4ubuntu8)]
--
-- used:
-- mysqldump  Ver 10.9 Distrib 4.1.12, for pc-linux-gnu (i486)
--
-- This file should be encoded in utf8 !
-- ------------------------------------------------------
CREATE TABLE `lucid_archive` (
  `id` int(11) NOT NULL auto_increment,
  `userID` int(11) NOT NULL default '0',
  `type` varchar(50) NOT NULL default '',
  `date` datetime NOT NULL default '0000-00-00 00:00:00',
  `comment` varchar(255) NOT NULL default '',
  `content` text NOT NULL,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='Achive system, in common use';
CREATE TABLE `lucid_log` (
  `id` int(11) NOT NULL auto_increment,
  `timestamp` datetime default NULL,
  `sid` varchar(50) NOT NULL default '-1',
  `user_name` varchar(50) default NULL,
  `ip` varchar(50) default NULL,
  `domain` varchar(50) default NULL,
  `message` varchar(255) NOT NULL default '',
  `typ` varchar(50) NOT NULL default '',
  `status` varchar(12) NOT NULL default '-1',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='logging storage';
CREATE TABLE `lucid_md5users` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  `realname` varchar(50) NOT NULL default '',
  `email` varchar(50) NOT NULL default '',
  `pass1` varchar(32) NOT NULL default '',
  `pass2` varchar(32) NOT NULL default '',
  `admin` tinyint(4) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) TYPE=MyISAM COMMENT='User data';
CREATE TABLE `lucid_pages_internal` (
  `name` varchar(50) NOT NULL default '',
  `plugin_id` tinyint(4) default NULL,
  `category_id` tinyint(4) NOT NULL default '0',
  `template_engine` tinyint(1) default NULL,
  `markup` tinyint(4) default NULL,
  `lastupdatetime` datetime NOT NULL default '0000-00-00 00:00:00',
  `lastupdateby` int(11) NOT NULL default '0',
  `content` text NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY  (`name`)
) TYPE=MyISAM COMMENT='internal page storage';
CREATE TABLE `lucid_pages_internal_category` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  `position` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='internal page categories (linked with IDs)';
CREATE TABLE `lucid_plugindata` (
  `id` int(11) NOT NULL auto_increment,
  `plugin_id` int(11) NOT NULL default '0',
  `method_name` varchar(50) NOT NULL default '',
  `parent_method_id` int(11) default NULL,
  `CGI_laws` varchar(255) default NULL,
  `get_CGI_data` varchar(255) default NULL,
  `internal_page_info` varchar(255) default NULL,
  `menu_section` varchar(128) default NULL,
  `menu_description` varchar(255) default NULL,
  `must_admin` int(11) NOT NULL default '1',
  `must_login` int(11) NOT NULL default '1',
  `has_Tags` int(11) NOT NULL default '0',
  `no_rights_error` int(11) NOT NULL default '0',
  `direct_out` int(11) NOT NULL default '0',
  `sys_exit` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='Module/plugin methods configuration';
CREATE TABLE `lucid_plugins` (
  `id` int(11) NOT NULL auto_increment,
  `package_name` varchar(30) NOT NULL default '',
  `module_name` varchar(30) NOT NULL default '',
  `version` varchar(15) default NULL,
  `author` varchar(50) default NULL,
  `url` varchar(128) default NULL,
  `description` varchar(255) default NULL,
  `long_description` text,
  `active` int(1) NOT NULL default '0',
  `debug` int(1) NOT NULL default '0',
  `SQL_deinstall_commands` text,
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='global module/plugin configuration';
CREATE TABLE `lucid_session_data` (
  `session_id` varchar(32) NOT NULL default '',
  `timestamp` int(15) NOT NULL default '0',
  `ip` varchar(15) NOT NULL default '',
  `domain_name` varchar(50) NOT NULL default '',
  `session_data` text NOT NULL,
  PRIMARY KEY  (`session_id`),
  KEY `session_id` (`session_id`)
) TYPE=MyISAM COMMENT='session management data';
CREATE TABLE `lucid_appconfig` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(30) NOT NULL default '',
  `value` varchar(255) NOT NULL default '',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) TYPE=MyISAM COMMENT='not used yet!';
INSERT INTO `lucid_appconfig` VALUES (1,'version','1.0.11');
CREATE TABLE `lucid_groups` (
  `id` int(11) NOT NULL auto_increment,
  `pluginID` int(11) NOT NULL default '0',
  `name` varchar(50) NOT NULL default '',
  `section` varchar(50) NOT NULL default '',
  `description` varchar(50) NOT NULL default '',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) TYPE=MyISAM COMMENT='not used yet!';
INSERT INTO `lucid_groups` VALUES (1,0,'managePages','core','This group is able to add/edit/delete pages.');
INSERT INTO `lucid_groups` VALUES (2,0,'manageStyles','core','This group is able to add/edit/delete stylesheets.');
INSERT INTO `lucid_groups` VALUES (3,0,'manageTemplates','core','This group is able to add/edit/delete templates.');
INSERT INTO `lucid_groups` VALUES (4,0,'admin','user-Defined','Administratoren');
CREATE TABLE `lucid_markups` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='Liste of available markups (manually created!)';
INSERT INTO `lucid_markups` VALUES (1,'None');
INSERT INTO `lucid_markups` VALUES (2,'textile');
CREATE TABLE `lucid_pages` (
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
) TYPE=MyISAM COMMENT='CMS page storage';
INSERT INTO `lucid_pages` VALUES (1,'index','index',0,0,1,1,NULL,'2','h2. Welcome to your PyLucid CMS =;-)\r\n\r\nNote:\r\n\r\n* Do not delete this page: edit it!\r\n* check the right\'s of install_PyLucid.py!','','','2005-12-19 15:54:31',2,1,1,1,2,1);
CREATE TABLE `lucid_preferences` (
  `id` int(11) NOT NULL auto_increment,
  `pluginID` int(11) NOT NULL default '0',
  `section` varchar(30) NOT NULL default '',
  `varName` varchar(30) NOT NULL default '',
  `name` varchar(50) NOT NULL default '',
  `description` text NOT NULL,
  `value` varchar(100) NOT NULL default '',
  `type` varchar(30) NOT NULL default 'text',
  PRIMARY KEY  (`id`),
  KEY `section` (`section`)
) TYPE=MyISAM COMMENT='old cfg values, used partially';
INSERT INTO `lucid_preferences` VALUES (1,0,'core','defaultPageName','Default Page','This This is the default page that a site visitor will see if they arrive at your index.php without specifying a particular page.','1','pageSelect');
INSERT INTO `lucid_preferences` VALUES (2,0,'core','defaultMarkup','Preferred Text Markup','This specifies what the default text markup parser will be for new pages. You can set it to the name of a plugin markup parser (\"textile\" and \"markdown\" are currently available), or \"none\".','textile','markupSelect');
INSERT INTO `lucid_preferences` VALUES (3,0,'core','defaultTemplate','Default Template Name','This is the template that will be assigned to new pages when they are created.','1','templateSelect');
INSERT INTO `lucid_preferences` VALUES (4,0,'core','defaultStyle','Default Style Name','This is the stylesheet taht will be assigned to new pages when they are created.','1','styleSelect');
INSERT INTO `lucid_preferences` VALUES (5,0,'core','defaultShowLinks','Show Links default','This determines whether new pages are shown or hidden in navigation controls. Check to have pages shown, or leave unchecked to have new pages suppressed.','1','checkbox');
INSERT INTO `lucid_preferences` VALUES (6,0,'core','defaultPermitPublic','Permit Public default','This determines whether new pages are publicly accessible, or require login. Check to make new pages automatically accessible, or leave un-checked to have new pages require login.','1','checkbox');
INSERT INTO `lucid_preferences` VALUES (7,0,'core','siteOffline','Site Offline','If checked, whenever someone visits your site, rather then seeing the normal requested page, they will instead see the page that is specified in the \"Offline Page\" config item. If the user is currently logged in then they will see the requested page.','','checkbox');
INSERT INTO `lucid_preferences` VALUES (8,0,'core','offlinePage','Offline Page','This is the page that a user will see if the \"Offline Site\" config item is checked.','1','pageSelect');
INSERT INTO `lucid_preferences` VALUES (9,0,'core','formatDate','Date Format','Specify your preferred date display format (php time format).','%d.%m.%Y','text');
INSERT INTO `lucid_preferences` VALUES (10,0,'core','formatTime','Time Format','Specify your preferred time display format (php time format).','%H:%M','text');
INSERT INTO `lucid_preferences` VALUES (11,0,'core','formatDateTime','DateTime Format','Specify your preferred date + time display format (php time format).','%d.%m.%Y - %H:%M','text');
INSERT INTO `lucid_preferences` VALUES (12,0,'core','timezoneOffset','Timezone Offset','The number of hours difference between your server\'s time and the time you wish to have displayed (not necessarily offset from GMT).','0','text');
INSERT INTO `lucid_preferences` VALUES (13,0,'core','inactivityTimeout','Inactivitiy Timeout','The number of idle minutes before requiring user to log in again.','60','text');
INSERT INTO `lucid_preferences` VALUES (14,0,'core','rows','Editor - Rows','The number of rows to display in the editor.','25','text');
INSERT INTO `lucid_preferences` VALUES (15,0,'core','cols','Editor - Columns','The number of columns to display in the editor.','100','text');
INSERT INTO `lucid_preferences` VALUES (73,13,'MenuMaker','useTitles','Use Page Titles for Link Text','If this is checked, then page titles will be used for the text of links generated in menus. If there is no title, then the page name will be used for the link text.','1','checkbox');
INSERT INTO `lucid_preferences` VALUES (72,13,'MenuMaker','peerReplace','Peer Menu to replace Sub Menu','If this is checked, then when there are no items to display in the \"sub menu\" then the \"sub menu\" will be replaced with the \"peer menu\". This is usually the desired menu behaviour.','1','checkbox');
INSERT INTO `lucid_preferences` VALUES (71,13,'peerMenu','currentAfter','Peer Menu Current Page After','HTML placed after the currently displayed page link - if this is blank then \"Main Menu After\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (70,13,'peerMenu','currentBefore','Peer Menu Current Page Before','HTML placed before the currently displayed page link - if this is blank then \"Main Menu Before\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (69,13,'peerMenu','after','Peer Menu After','HTML placed after each individual menu item','</li>','text');
INSERT INTO `lucid_preferences` VALUES (68,13,'peerMenu','before','Peer Menu Before','HTML placed before each individual menu item','<li>','text');
INSERT INTO `lucid_preferences` VALUES (67,13,'peerMenu','finish','Peer Menu Finish','HTML placed at the end of the menu','</ul>','text');
INSERT INTO `lucid_preferences` VALUES (66,13,'peerMenu','begin','Peer Menu Begin','HTML placed at the beginning of the menu','<ul>','text');
INSERT INTO `lucid_preferences` VALUES (65,13,'subMenu','currentAfter','Sub Menu Current Page After','HTML placed after the currently displayed page link - if this is blank then \"Main Menu After\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (62,13,'subMenu','before','Sub Menu Before','HTML placed before each individual menu item','<li>','text');
INSERT INTO `lucid_preferences` VALUES (63,13,'subMenu','after','Sub Menu After','HTML placed after each individual menu item','</li>','text');
INSERT INTO `lucid_preferences` VALUES (64,13,'subMenu','currentBefore','Sub Menu Current Page Before','HTML placed before the currently displayed page link - if this is blank then \"Main Menu Before\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (60,13,'subMenu','begin','Sub Menu Begin','HTML placed at the beginning of the menu','<ul>','text');
INSERT INTO `lucid_preferences` VALUES (61,13,'subMenu','finish','Sub Menu Finish','HTML placed at the end of the menu','</ul>','text');
INSERT INTO `lucid_preferences` VALUES (39,6,'ImageManager','maxSize','Max Upload Size','Maximum size (in bytes) of an image you can upload','300000','text');
INSERT INTO `lucid_preferences` VALUES (38,6,'ImageManager','imageDir','Image Directory','This is the path to where the uploaded images will be stored. Please ensure that this directory exists and is writable by the web user.','./images/','text');
INSERT INTO `lucid_preferences` VALUES (59,13,'mainMenu','currentAfter','Main Menu Current Page After','HTML placed after the currently displayed page link - if this is blank then \"Main Menu After\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (58,13,'mainMenu','currentBefore','Main Menu Current Page Before','HTML placed before the currently displayed page link - if this is blank then \"Main Menu Before\" will be used.','','text');
INSERT INTO `lucid_preferences` VALUES (57,13,'mainMenu','after','Main Menu After','HTML placed after each individual menu item','</li>','text');
INSERT INTO `lucid_preferences` VALUES (55,13,'mainMenu','finish','Main Menu Finish','HTML placed at the end of the menu','</ul>','text');
INSERT INTO `lucid_preferences` VALUES (56,13,'mainMenu','before','Main Menu Before','HTML placed before each individual menu item','<li>','text');
INSERT INTO `lucid_preferences` VALUES (54,13,'mainMenu','begin','Main Menu Begin','HTML placed at the beginning of the menu','<ul>','text');
CREATE TABLE `lucid_styles` (
  `id` int(11) NOT NULL auto_increment,
  `plugin_id` tinyint(4) default NULL,
  `name` varchar(50) NOT NULL default '',
  `description` text,
  `content` text NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) TYPE=MyISAM COMMENT='CSS stylesheet storage';
INSERT INTO `lucid_styles` VALUES (1,NULL,'main','main Stylesheet','/* Farben:\r\n\r\n#C9C573;\r\n#B1B08B;\r\n#FFFFDB;\r\n\r\n*/\r\n\r\n* { color: #000000 }\r\nbody {\r\n  font-family: tahoma, arial, sans-serif;\r\n  color: #000000;\r\n  font-size: 0.9em;\r\n  background-color: #C9C573;\r\n}\r\nhtml, body {\r\n  margin: 5px;\r\n  padding: 0;\r\n}\r\ntextarea {\r\n  background-color: #FFFFF5;\r\n}\r\n#page_msg, pre, .code, .SourceCode, fieldset legend {\r\n  font-family: Courier New,Courier,monospace,mono;\r\n  background-color: #FAFAFD;\r\n  color: #000000;\r\n  padding: 10px;\r\n  border: 1px solid #C9C573;\r\n  font-size: 0.8em;\r\n}\r\n.SourceCode {\r\n  white-space:nowrap;\r\n}\r\nfieldset legend {\r\n  font-size: 1em;\r\n  padding: 3px;\r\n}\r\n#page_msg {\r\n  border-color: #FF0000;\r\n  color: #AA0000;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n Überschrift über die gesammte Seite\r\n----------------------------------------------------- */\r\n#headline h2 {\r\n  font-size: 2em;\r\n  margin: 0.5em;\r\n  padding-left: 1.5em;\r\n  color: #FFFFFF;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n Menu\r\n----------------------------------------------------- */\r\n#sidebar {\r\n  position:absolute;\r\n  top: 100px;\r\n  left: 3px;\r\n  width: 17em;\r\n  height: auto;\r\n  z-index: 10;\r\n  padding: 1em;\r\n  background-color: #FFFFDB;\r\n  border: 1px solid #B1B08B;\r\n  font-size: 0.9em;\r\n  color: #000000;\r\n  text-align:left;\r\n  padding: 0px;\r\n  margin: 0px;\r\n  padding-top: 10px;\r\n  padding-left: 5px;\r\n}\r\n#sidebar a {\r\n  text-decoration:none;\r\n  margin: 0px;\r\n  padding: 0px;\r\n  padding-left: 0.5em;\r\n  padding-right: 0.5em;\r\n}\r\n#sidebar a:hover, #sidebar a.current {\r\n  /* hover + Aktuell angeklickter Menüpunkt */\r\n  background-color: #C9C573;\r\n  color: #FFFFFF;\r\n  margin: 0px;\r\n  padding: 0px;\r\n  padding-left: 0.5em;\r\n  padding-right: 0.5em;\r\n}\r\n#sidebar ul {\r\n  margin: 1.5em;\r\n  margin-right: 0px;\r\n  margin-top: 0.2em;\r\n  margin-bottom: 1.5em;\r\n\r\n  padding: 0px;\r\n\r\n  list-style-type: none;\r\n  border:0px;\r\n}\r\n#sidebar li {\r\n  white-space: nowrap;\r\n  margin: 0px;\r\n  margin-right: 0px;\r\n  padding: 0px;\r\n}\r\n#sidebar img {\r\n  margin: 5px 0px 5px 5px;\r\n  padding: 5px 0px 5px 5px;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n CMS Page\r\n----------------------------------------------------- */\r\n#main-content {\r\n  /* Rahmen für main-content + footer_nav */\r\n  position:absolute;\r\n  top: 55px;\r\n  left: 10em;\r\n  width: 70%;\r\n  min-height: 600px;\r\n  z-index: 1;\r\n  margin: 0px;\r\n  padding: 5px;\r\n  padding-left: 6em;\r\n  background-color: #FFFFE5;\r\n  border:15px solid #FFFFE5;\r\n}\r\n#main-content h2 {\r\n  border-bottom: 1px solid #000000;\r\n}\r\n#nav_footer, #nav_link {\r\n  font-size: 0.6em;\r\n}\r\n#nav_footer, #nav_footer a, #nav_link, #nav_link a {\r\n  border-top: 1px solid #B1B08B;\r\n  color: #B1B08B;\r\n  text-decoration:none;\r\n  text-align: right;\r\n}\r\n#nav_link, #nav_link a {\r\n  text-align: left;\r\n  border: 0px;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n Admin Menu\r\n----------------------------------------------------- */\r\n.adminmenu {\r\n  padding: 5px;\r\n  background-color: #C9C573;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n Links aus dem breadcrumbs-Plugin\r\n----------------------------------------------------- */\r\n#breadcrumbs {\r\n  width: 80%;\r\n  margin:1em auto;\r\n  text-align:left;\r\n  max-width: 1024px;\r\n}\r\n\r\n/* -----------------------------------------------------\r\nZusatzmodule\r\n----------------------------------------------------- */\r\n.Gallery ul {\r\n  text-align: center;\r\n  margin: 0px;\r\n  padding: 0px;\r\n}\r\n.Gallery li {\r\n  float: left;\r\n  border: 1px solid #EAECFF;\r\n  height: 150px;\r\n  width: auto;\r\n  text-align: center;\r\n  margin: 5px;\r\n  padding: 5px;\r\n  list-style-type: none;\r\n  background-color: #EDF1FF;\r\n}\r\n.clear {\r\n  clear: both;\r\n  margin: 5px;\r\n  padding: 5px;\r\n  border: none;\r\n}\r\n\r\n/* -----------------------------------------------------\r\n  Edit Look\r\n----------------------------------------------------- */\r\n#edit_style_select, #edit_template_select {\r\n  border-spacing: 0.5em;\r\n}\r\n#edit_style_select .name, #edit_template_select .name {\r\n  font-weight:bold\r\n\r\n}\r\n#edit_style_select .description, #edit_template_select .description {\r\n  font-style:italic;\r\n}\r\n#page_edit_preview {\r\n  border: 1px solid #C9C573;\r\n}\r\n.resize_buttons a {\r\n  text-decoration:none;\r\n}\r\n\r\n/* -----------------------------------------------------\r\nPage Edit\r\n----------------------------------------------------- */\r\n#page_content {\r\n    width: 100%;\r\n}\r\n\r\n/* -----------------------------------------------------\r\nSite Map\r\n----------------------------------------------------- */\r\n\r\n#SiteMap ul {\r\n  margin-top: 5px;\r\n  margin-bottom: 5px;\r\n  list-style-type: none;\r\n}\r\n#SiteMap li {\r\n  margin-top: 2px;\r\n  margin-bottom: 2px;\r\n}\r\n#SiteMap a {\r\n  text-decoration:underline;\r\n}\r\n#SiteMap li.deep_0 {\r\n  margin-top: 4em;\r\n  font-size: 1.2em;\r\n  border-bottom: 1px solid #C9C573;\r\n}\r\n#SiteMap li.deep_0 a {\r\n  text-decoration:none;\r\n}\r\n#SiteMap .deep_1 {\r\n  margin-top: 1em;\r\n}\r\n\r\n\r\n/* -----------------------------------------------------\r\nsearch\r\n----------------------------------------------------- */\r\n#search_form input, #search_form button {\r\n  font-size: 0.9em;\r\n  border: 1px solid #44444;\r\n  padding: 1px;\r\n}\r\n\r\n/* -----------------------------------------------------\r\nlucidFunction:RSS\r\n----------------------------------------------------- */\r\n.RSS {\r\n  margin: 1em;\r\n  padding: 1em;\r\n  border: 1px solid;\r\n}\r\n.RSS li {\r\n  list-style-type: none;\r\n}\r\n.RSS h1 {\r\n  font-size: 1em;\r\n  font-style: strong;\r\n  margin: 0px;\r\n}');
INSERT INTO `lucid_styles` VALUES (2,NULL,'none','This is a blank stylesheet.','');
INSERT INTO `lucid_styles` VALUES (34,127,'PyBB','PyBB module styles','#forum_summary {\n    width:100%;\n    background-color:#DDDDDD;\n}\n#forum_summary .headline {\n    background-color:#EEEEEE;\n}\n#forum_summary .cat_header {\n    background-color:#CCCCFF;\n}\n#forum_summary .forums {\n    background-color:#EEEEEE;\n}\n.color0 {\n    background-color:#EEEEEE;\n}\n.color1 {\n    background-color:#DDDDDD;\n}\n.nav {\n    background-color:#DDDDDD;\n}');
CREATE TABLE `lucid_template_engines` (
  `id` tinyint(1) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  PRIMARY KEY  (`id`)
) TYPE=MyISAM COMMENT='Liste of available template engines (manually created!)';
INSERT INTO `lucid_template_engines` VALUES (1,'None');
INSERT INTO `lucid_template_engines` VALUES (2,'string formatting');
INSERT INTO `lucid_template_engines` VALUES (3,'TAL');
CREATE TABLE `lucid_templates` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL default '',
  `description` text NOT NULL,
  `content` text NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) TYPE=MyISAM COMMENT='page template storage';
INSERT INTO `lucid_templates` VALUES (1,'basic','default template','<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"xhtml1-strict.dtd\">\r\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\r\n<head>\r\n<title>PyLucid - <lucidTag:page_title/></title>\r\n<meta name=\"robots\"                    content=\"<lucidTag:robots/>\" />\r\n<meta name=\"keywords\"                  content=\"<lucidTag:page_keywords/>\" />\r\n<meta name=\"description\"               content=\"<lucidTag:page_description/>\" />\r\n<meta name=\"Author\"                    content=\"PyLucidCMS\" />\r\n<meta name=\"DC.Date\"                   content=\"<lucidTag:page_last_modified/>\" />\r\n<meta name=\"DC.Date.created\"           content=\"<lucidTag:page_datetime/>\" />\r\n<meta http-equiv=\"Content-Type\"        content=\"text/html; charset=utf-8\" />\r\n<meta name=\"MSSmartTagsPreventParsing\" content=\"TRUE\" />\r\n<meta http-equiv=\"imagetoolbar\"        content=\"no\" />\r\n<link rel=\"contents\" title=\"Inhaltsverzeichnis\" href=\"?p=/SiteMap\" />\r\n<lucidTag:page_style/>\r\n</head>\r\n<body>\r\n<div id=\"headline\"><h2>PyLucid CMS</h2></div>\r\n<div id=\"sidebar\">\r\n<lucidTag:main_menu/>\r\n<ul>\r\n  <li>\r\n    <a href=\"http://sourceforge.net/projects/pylucid/\" id=\"logo\"><img src=\"http://sourceforge.net/sflogo.php?group_id=146328&amp;type=1\" width=\"88\" height=\"31\" border=\"0\" alt=\"SourceForge.net\" /></a>\r\n  </li>\r\n  <li>\r\n    <a href=\"http://sourceforge.net/donate/index.php?group_id=146328\"><img src=\"http://images.sourceforge.net/images/project-support.jpg\" width=\"88\" height=\"32\" border=\"0\" alt=\"Support This Project\" /></a>\r\n  </li>\r\n  <li>\r\n    <lucidTag:search/>\r\n  </li>\r\n</ul>\r\n</div>\r\n\r\n<div id=\"main-content\">\r\n  <h2><lucidTag:page_title/></h2>\r\n  <lucidTag:page_msg/><lucidTag:admin_menu/>\r\n  <p id=\"nav_link\">\r\n    <lucidTag:back_links/>\r\n  </p>\r\n  <lucidTag:page_body/>\r\n  <p id=\"nav_footer\">\r\n    <lucidTag:page_last_modified/> | <lucidTag:script_login/> | Rendered in <lucidTag:script_duration/> sec. | <lucidTag:powered_by/>\r\n  </p>\r\n</div>\r\n</body>\r\n</html>');
CREATE TABLE `lucid_user_group` (
  `id` int(11) NOT NULL auto_increment,
  `userID` int(11) NOT NULL default '0',
  `groupID` int(11) NOT NULL default '0',
  PRIMARY KEY  (`id`),
  KEY `groupID` (`groupID`),
  KEY `userID` (`userID`)
) TYPE=MyISAM COMMENT='not used yet!';
