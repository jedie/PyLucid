#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.8"

__history__ = """
v0.0.8
    - Fehler in is_cgi() behoben
v0.0.7
    - subprocess unnötig, da have_fork, have_popen2 und have_popen3 unnötigerweise
        auf False im RequestHandler gesetzt wurden. Das bedeutetet das die CGI
        Skripte immer mit der Notlösung execfile() ausgeführt wurden.
v0.0.6
    - Überschreiben der CGIHTTPServer.execfile() damit Skripte nicht per
        execfile() sondern per subprocess ausgeführt werden. Damit alle
        "Sub"-Module immer neu geladen werden.
v0.0.5
    - os.environ["QUERY_STRING"] wird richtig übergeben
"""

import CGIHTTPServer, SocketServer
import BaseHTTPServer
import os, sys, socket, webbrowser


class MyRequestHandler( CGIHTTPServer.CGIHTTPRequestHandler ):
    """Modifizieren des Standart RequestHandlers"""

    def is_cgi(self):
        """
        Einfachere Variante, sodas alle Python-Skripte überall ausgeführt werden#
        """
        if ".py" in self.path:
            os.environ['DOCUMENT_ROOT'] = os.getcwd()
            if "?" in self.path:
                filepath, getparam = self.path.split("?",1)
                base, filename = os.path.split(filepath)
                self.cgi_info = base, filename + "?" + getparam
            else:
                base, filename = os.path.split(self.path)
                self.cgi_info = base, filename
            os.environ["SCRIPT_FILENAME"] = filename
            return True


#~ class MyThreadingServer( BaseHTTPServer.HTTPServer ):
class MyThreadingServer( SocketServer.ThreadingTCPServer ):
    """
    Verbesserung des Standart Servers:
     - ermöglicht das abarbeiten mehrere Anfragen parallel (z.B. Download mehrere Dateien gleichzeitig)
     - Ermöglicht das einschränken des IP-Bereiches aus denen der Server Anfragen behandelt
    """
    allow_reuse_address = 1    # Seems to make sense in testing environment


    def __init__(self, server_address, request_handler, AllowIPs):
        SocketServer.ThreadingTCPServer.__init__(self, server_address, request_handler)
        #~ BaseHTTPServer.HTTPServer.__init__(self, server_address, request_handler)

        self.AllowIPs = [mask.split('.') for mask in AllowIPs]

    def server_bind(self):
        """Override server_bind to store the server name. (Parallele Anfragen)"""
        SocketServer.ThreadingTCPServer.server_bind(self)
        host, self.server_port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)

    def verify_request(self, dummy, client_address):
        """Checkt ob die IP-Adresse der Anfrage in 'AllowIPs' vorhanden ist"""
        def check_ip(mask):
            for mask_part, ip_part in zip(mask, ip):
                if mask_part != ip_part and mask_part != '*':
                    return False
            return True

        ip = client_address[0].split('.')

        for mask in self.AllowIPs:
            if check_ip(mask):
                return True

        print "IP [%s] not allowed!" % client_address

        return False




def ServerStart( ListenPort, AllowIPs ):
    print "="*80
    print "ROOT-Pfad .......................:", os.getcwd()
    print "Starte CGI-HTTP-Server auf Port .:", ListenPort
    print "Zugelassener IP-Bereich .........:", AllowIPs
    print
    print "Seiten sind nun unter [http://localhost:%s] erreichbar!\n" % ListenPort

    #~ httpd = MyThreadingServer( ("", ListenPort), CGIHTTPServer.CGIHTTPRequestHandler, AllowIPs )
    httpd = MyThreadingServer( ("", ListenPort), MyRequestHandler, AllowIPs )

    # Öffne Browser
    webbrowser.open_new("http://localhost/index.py")

    httpd.serve_forever()

if __name__=="__main__":
    ServerStart(
        ListenPort  = 80,
        AllowIPs    = ('127.0.0.1', '192.168.*.*')
    )