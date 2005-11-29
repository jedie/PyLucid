#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" <lucidTag:createRSSFeed /> """

__version__="0.0.1"
__history__=""" v0.0.1 - erste Version """

#~ import cgitb;cgitb.enable()
import sys, os



class createRSSFeed:
    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
            "direct_out"    : True,
            "sys_exit"      : True,
        },
    }


    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        #self.CGIdata.debug()
        self.db             = PyLucid["db"]
        self.config         = PyLucid["config"]
        self.tools          = PyLucid["tools"]
        self.page_msg       = PyLucid["page_msg"]

    def lucidTag(self):
        print "Content-type: application/xml; charset=utf-8\r\n" # Debugging
        HTTP_HOST = os.environ["HTTP_HOST"]
        feed = ""
        feed += "<?xml version='1.0' encoding='utf-8' ?>\n"
        feed += "<rss version='2.0'>\n"
        feed += '<channel>\n'

        feed += " <title>%s Newsfeed RSS 2.0</title>\n" % HTTP_HOST
        feed += " <link>%s</link>\n" % self.base_url
        feed += " <description>This is the News Feed of %s</description>\n" % HTTP_HOST
        #~ feed += " <language>de-de</language>\n"
        feed += " <image>\n"
        feed += "  <title>Title of the Image</title>\n"
        feed += "  <url>http://%s/favicon.png</url>\n" % HTTP_HOST
        feed += "  <link>http://%s/</link>\n" % HTTP_HOST
        feed += " </image>\n"


        SQLresult = self.db.select(
            select_items    = ["id", "name", "title", "lastupdatetime"],
            from_table      = "pages",
            where           = ("permitViewPublic", 1),
            order           = ("lastupdatetime", "DESC"),
            limit           = (0, 5)
        )

        for item in SQLresult:
          upd_date = self.tools.convert_date_from_sql( item["lastupdatetime"] )

          feed += "<item>\n"
          feed += " <title>%s %s</title>\n" % (upd_date, item["title"])
          feed += ' <link>%s?page_id=%s</link>\n' % (self.config.system.poormans_url, item["id"])

          feed += " <description>%s</description>\n" % item["title"]
          feed += "</item>\n"

        feed += '</channel>\n'
        feed += '</rss>\n'

        sys.stdout.write(feed)
        sys.exit()

        #~ f=open("RSS.xml", 'w')
        #~ f.write(feed)
        #~ f.close()


def test(url):
    import urllib, xml.dom.minidom
    print "\n\nURL:", url
    rss = urllib.urlopen( url )
    rss_data = rss.read()
    print "test:", rss_data.encode("String_Escape")

    rssDocument = xml.dom.minidom.parseString(rss_data)

    print rssDocument.getElementsByTagName("item")

if __name__ == "__main__":
    #~ test("http://sourceforge.net/export/rss2_projnews.php?group_id=146328")
    test("http://www.pythonware.com/daily/rss.xml")
    test("http://www.jensdiemer.de/index.py?p=/RSS")