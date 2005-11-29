#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Blendet eine andere Webseite von einem anderen Server in die CMS-Seite ein.
Bsp.:
<lucidFunction:IncludeRemote>http://...</lucidFunction>
"""

__version__="0.0.2"

__history__="""
v0.0.2
    - Bug 1315600: ModuleManager änderung: "lucidFunction" Parameter übergabe erfolgt immer mit function_info!
v0.0.1
    - Source aus dem alten pagerender.py übernommen und angepasst
    - re-Filter verbessert
    - socket.setdefaulttimeout(5) hinzugefügt
"""


import socket, urllib2, re


class IncludeRemote:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidFunction" : {
            "must_login"    : False,
            "must_admin"    : False,
        }
    }

    #_______________________________________________________________________

    def __init__( self, PyLucid ):
        # Es werden keine PyLucid-Objekte ben�tigt...
        pass

    def lucidFunction( self, function_info ):
        """
        Unterscheidet zwischen Lokalen PyLucid-Skripten und echten URL-Abfragen
        """
        URL = function_info # Inhalt der <lucidFunction>-Tag
        try:
            socket.setdefaulttimeout(5)
        except AttributeError:
            # Geht erst ab Python 2.3 :(
            pass

        try:
            f = urllib2.urlopen( URL )
            sidecontent = f.read()
            f.close()
        except Exception, e:
            return "<p>IncludeRemote error! Can't get '%s'<br /> \
                error:'%s'</p>" % ( URL, e )

        try:
            # Stylesheets rausfiltern
            sidecontent = re.sub('(<link.*?rel.*?stylesheet.*?>)(?is)',"",sidecontent)
        except:
            pass

        try:
            # JavaScripte rausfiltern
            sidecontent = re.sub('(<script.*?</script>)(?is)',"",sidecontent)
        except:
            pass

        try:
            # Inhalt nach UTF-8 wandeln
            charset = re.findall('<meta.*?Content-Type.*?charset=(.*?)"', sidecontent)[0]
            sidecontent = sidecontent.decode( charset ).encode( "utf_8" )
        except:
            pass

        try:
            print re.findall("<body.*?>(.*?)</body>(?is)", sidecontent)[0]
        except:
            print sidecontent