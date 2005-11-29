#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
<lucidTag:PyBB/>
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""

import sys

from PyLucid_simpleTAL import simpleTAL, simpleTALES

#~ print "Content-type: text/html; charset=utf-8\r\n" # Debugging
from PyLucid_plugins import PyBB





style = """
<style type="text/css">
#forum_summary {
    width:100%;
    background-color:#DDDDDD;
}
#forum_summary .headline {
    background-color:#EEEEEE;
}
#forum_summary .cat_header {
    background-color:#CCCCFF;
}
#forum_summary .forums {
    background-color:#EEEEEE;
}
.color0 {
    background-color:#EEEEEE;
}
.color1 {
    background-color:#DDDDDD;
}
.nav {
    background-color:#DDDDDD;
}
</style>
"""



view_forum_template = """
<p class="nav" ><a tal:attributes="href back_link/url;title back_link/name" tal:content="back_link/name"></a></p>
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
</table>""" + style

summary_template = """
<table id="forum_summary">
<tr class="headline">
    <th>Forum</th>
    <th>Themen</th>
    <th>Beiträge</th>
    <th>Letzter Beitrag</th>
</tr>
<tr tal:repeat="data forum_data">
<td class="cat_header"><h3 tal:content="data/cat_title"></h3></td>
    <tr tal:repeat="sub_data data/sub_data" class="forums">
        <td>
            <p>
            <a tal:attributes="href sub_data/link;title sub_data/forum_name" tal:content="sub_data/forum_name"></a>
            <br />
            <small tal:content="sub_data/forum_desc"></small>
            </p>
        </td>
        <td tal:content="sub_data/forum_topics"></td>
        <td tal:content="sub_data/forum_posts"></td>
        <td tal:condition="exists:sub_data/post_time">
            <p>
            <span tal:replace="sub_data/post_time">post_time</span>
            <br />
            <small tal:content="sub_data/username"></small>
            </p>
        </td>
        <td tal:condition="not:exists:sub_data/post_time">kein Beitrag</td>
    </tr>
</tr>
</table>
""" + style









class PyBB_forum:

    #_______________________________________________________________________
    # Module-Manager Daten
    global_rights = {
        "must_login"    : False,
        "must_admin"    : False,
    }

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : global_rights,
        "print_summary" : global_rights,

        "view_forum": {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"forum_id": int},
        }
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db             = PyLucid["db"]
        self.session        = PyLucid["session"]
        #~ self.session.debug()
        self.config         = PyLucid["config"]
        self.preferences    = PyLucid["preferences"]

        self.PyBB = PyBB.PyBB_routines.PyBB(PyLucid, "PyBB_RSS")

        self.bb_table_prefix = "phpbb_"

    def lucidTag(self):
        self.print_summary()

    def print_summary(self):
        """
        Übersichtsseite des Forums
        """
        categories = self.PyBB.categories()
        forums = self.PyBB.forums()
        forums = self.db.decode_sql_results(forums, codec="latin-1")

        # SQL Ergebnisse verschachteln, für die Ausgabe
        data = []
        for category in categories:
            cat_data = {
                "cat_title" : category["cat_title"],
                "sub_data" : [],
            }
            for forum in forums:
                if forum["cat_id"] == category["cat_id"]:
                    forum["link"] = "%sview_forum&forum_id=%s" % (
                        self.action_url, forum["forum_id"]
                    )
                    if not forum["forum_posts"] == 0:
                        # Es gibt Beiträge im Forum
                        forum.update(self.PyBB.post_data(forum["forum_last_post_id"]))

                    cat_data["sub_data"].append(forum)

            data.append(cat_data)

        context = simpleTALES.Context()
        context.addGlobal("forum_data", data)

        template = simpleTAL.compileHTMLTemplate(summary_template, inputEncoding="UTF-8")
        template.expand(context, sys.stdout, outputEncoding="UTF-8")


    def view_forum(self, forum_id):
        """
        Ein Forum mit Beiträge anzeigen
        """
        # Daten des Forums aus DB holen
        topics = self.PyBB.topics(forum_id)
        topics = self.db.decode_sql_results(topics, codec="UTF-8")

        # Daten für Darstellung aufgebreiten
        for topic in topics:
            #~ topic["topic_title"] = topic["topic_title"].decode("UTF-8")
            topic["name"] = self.PyBB.username_by_id(topic["topic_poster"])
            topic["link"] = self.PyBB.user_profile_link(topic["topic_poster"])
            #~ topic["last_post_time"] = self.last_post(topic["topic_last_post_id"])["post_time"]

        context = simpleTALES.Context()
        context.addGlobal("back_link", {
            "url" : "%sprint_summary" % self.action_url,
            "name" : u"Übersicht",
        })
        context.addGlobal("table", topics)

        template = simpleTAL.compileHTMLTemplate(view_forum_template, inputEncoding="UTF-8")
        template.expand(context, sys.stdout, outputEncoding="UTF-8")




