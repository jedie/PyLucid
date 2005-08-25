#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)


"""
Beispielmodul
-------------

Um dieses Modul zu benutzten einfach in einer CMS-Seite das folgende Tag einbauen:

<lucidTag:get_remote/>
"""


__version__="0.0.1"

__history__="""
v0.0.1
    - erste Version
"""


import urllib2



#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "get_remote" : {
            "lucidTag"      : "get_remote",
            "must_login"    : False,
            "must_admin"    : False,
        }
    }

#_______________________________________________________________________



class get_remote:
    def __init__( self, PyLucid ):
        #~ self.db = PyLucid["db"]
        self.config     = PyLucid["config"]
        #~ self.config.debug()
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()

    def action( self ):
        """ Die Eigentliche Aktion wird ausgeführt """
        if self.CGIdata.has_key("url"):
            # Das Formular wurde abgeschickt
            ## Ein zurück Link anzeigen
            sidecontent = '<a href="%s?page_id=%s">zurück</a>' % (
                self.config.system.real_self_url, self.CGIdata["page_id"]
            )
            sidecontent += "<h3>Seite '%s':</h3>" % self.CGIdata["url"]
            sidecontent += "<hr>"
            ## Die Daten der URL holen
            sidecontent += self.get_url( self.CGIdata["url"] )
            # Kompletten Inhalt zurückliefert, damit er in die CMS-Seite eingebaut wird
            return sidecontent
        else:
            # Liefert das Formular, zur Eingabe der URL zurück
            return self.get_form()

    def get_form( self, oldurl="http://" ):
        """
        Baut das Formular zusammen
        """
        form  = '<form name="login" method="post" action="%s?page_id=%s">' % (
            self.config.system.real_self_url, self.CGIdata["page_id"]
        )
        form += '<p>url: <input name="url" type="text" value="%s">' % oldurl
        form += '<input type="submit"></p>'
        form += '</form>'
        return form

    def get_url( self, URL ):
        """
        Ruft die URL ab, filtert ein paar Dinge raus und liefert die Daten zurück
        """
        try:
            f = urllib2.urlopen( URL )
            sidecontent = f.read()
            f.close()
        except Exception, e:
            return "<p>Can't get '%s'<br /> \
                error:'%s'</p>" % ( URL, e )

        try:
            # Stylesheets rausfiltern
            sidecontent = re.sub('(<link.*?rel.*?stylesheet.*?>)(?uism)',"",sidecontent)
        except:
            pass
        try:
            # JavaScripte rausfiltern
            sidecontent = re.sub('(<script.*?<\/script>)(?uism)',"",sidecontent)
        except:
            pass

        try:
            # Inhalt nach UTF-8 wandeln
            charset = re.findall('<meta.*?Content-Type.*?charset=(.*?)"', sidecontent)[0]
            sidecontent = sidecontent.decode( charset ).encode( "utf_8" )
        except:
            pass

        try:
            # Nur den eigentlichen HTML-Body zurückliefern
            return re.findall("<body.*?>(.*?)</body>(?uism)", sidecontent)[0]
        except:
            return sidecontent



#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten


def PyLucid_action( PyLucid ):
    # Aktion starten
    return get_remote( PyLucid ).action()






