#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Routinen zum zugriff auf die phpBB2 Daten
"""

__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""

import sys, time
#~ print "Content-type: text/html; charset=utf-8\r\n" # Debugging
from PyLucid_simpleTAL import simpleTAL, simpleTALES


class PyBB:
    def __init__( self, PyLucid, current_module_name ):
        self.page_msg       = PyLucid["page_msg"]
        self.CGIdata        = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db             = PyLucid["db"]
        #~ self.session        = PyLucid["session"]
        #~ self.session.debug()
        self.config         = PyLucid["config"]
        #~ self.preferences    = PyLucid["preferences"]

        self.bb_table_prefix = "phpbb_"
        self.action_url = "%s?page_id=%s&command=%s&action=" % (
            self.config.system.real_self_url, self.CGIdata["page_id"], current_module_name
        )

    #___________________________________________________________________________________________________________
    # Allgemeine Methoden

    def categories(self):
        return self.db.select(
            select_items    = ["cat_id","cat_title"],
            from_table      = "categories",
            table_prefix    = self.bb_table_prefix,
            order           = ("cat_order","ASC")
        )

    def forums(self):
        return self.db.select(
            select_items    = [
                "forum_id","cat_id","forum_name","forum_desc","forum_topics","forum_posts","forum_last_post_id"
            ],
            from_table      = "forums",
            table_prefix    = self.bb_table_prefix,
            where           = [("forum_status",0)],
            order           = ("forum_order","ASC")
        )

    def post_data(self, post_id):
        """
        Daten über ein Beitrag:
        "post_time","poster_id" und "username"
        """
        post_data = self.db.select(
            select_items    = ["post_time","poster_id"],
            from_table      = "posts",
            table_prefix    = self.bb_table_prefix,
            where           = [("post_id", post_id)],
        )[0]
        post_data["username"] = self.username_by_id(post_data["poster_id"])
        return post_data

    def topics(self, forum_id):
        return self.db.select(
            select_items    = ["topic_title","topic_poster","topic_time","topic_views","topic_replies","topic_last_post_id"],
            from_table      = "topics",
            table_prefix    = self.bb_table_prefix,
            where           = [("forum_id",forum_id)],
            order           = ("topic_time","DESC"),
            #~ limit
        )

    def user_profile_link(self, user_id):
        return "%sviewprofile&amp;user=%s" % (self.action_url, user_id)

    def username_by_id(self, id):
        return self.db.select(
            select_items    = ["username"],
            from_table      = "users",
            table_prefix    = self.bb_table_prefix,
            where           = [("user_id", id)],
        )[0]["username"]















