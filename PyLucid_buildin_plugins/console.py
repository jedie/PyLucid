#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__version__ = "0.0.7"



## Revisions-History
# v0.0.7
#   - Anpassungen an das menu-Modul und inetd-Aufruf
# v0.0.6
#   - Das Ausführen von Befehlen ist nun mit einem Timeout versehen




#~ import cgitb ; cgitb.enable()
#~ import os, sys, locale, subprocess, re
#~ import xml.sax.saxutils, base64, bz2


# Eigene Module
#~ import ansi2html, CompressedOut, CGIdata, config, menu
#~ import thread_subprocess




#_______________________________________________________________________
# Module-Manager Daten

class module_info:
    """Pseudo Klasse: Daten für den Module-Manager"""
    data = {
        "console" : {
            "txt_menu"      : "console",
            "txt_long"      : "web shell console",
            #~ "section"       : "admin sub menu",
            #"category"      : "misc",
            "must_login"    : True,
            "must_admin"    : True,
        }
    }

#_______________________________________________________________________




#~ ansi2html_normalColor=('black', '#EEEEEE')


#~ menu.cfg.headings = '''<script type="text/javascript">
#~ window.scrollBy(0,9999999);
#~ function setFocus() {
    #~ document.form.cmd.focus();
    #~ window.scrollBy(0,30);
#~ }
#~ </script>
#~ <style type="text/css">
#~ #cmd {
   #~ background-color:#FFEEEE;
#~ }
#~ #cmd:focus {
   #~ background-color:#EEFFEE;
#~ }
#~ </style>
#~ '''

#~ menu.cfg.body = '<body onLoad="setFocus();">'

#~ console_form = '''<form name="form" id="form" method="post" action="%(self)s">
    #~ <input type="hidden" name="stdout" value="%(stdout_raw)s">
    #~ <input type="hidden" name="current_dir" value="%(current_dir)s">
    #~ <p>
    #~ <select name="timeout" alt="TimeOut in Sek">
        #~ <option value="1">1s</option>
        #~ <option value="%(process_timeout)s" selected="selected">%(process_timeout)ss</option>
        #~ <option value="10">10s</option>
        #~ <option value="30">30s</option>
        #~ <option value="60">60s</option>
    #~ </select>
    #~ <input name="cmd" type="text" id="cmd" size="%(input_size)s" /></p>
#~ </form>'''





## Nur zur Testzwecken, sollte man die compression der History-Daten ausschalten!
usecompression = False
#~ usecompression = True

def compress( txt ):
    "Kompression der History-Daten"
    if usecompression:
        txt = bz2.compress( txt, 9 )
        return base64.urlsafe_b64encode( txt ).replace("\n","")
    else:
        return xml.sax.saxutils.escape( txt )

def decompress( txt ):
    "Dekompression der History-Daten"
    if usecompression:
        try:
            txt = base64.urlsafe_b64decode( txt )
        except TypeError:
            return "<h3>decompress error (1)!</h3>"
        try:
            txt = bz2.decompress( txt )
        except IOError:
            return "<h3>decompress error (2)!</h3>"
        return txt
    else:
        return txt

def cutLines( txt, maxLines ):
    "Schneidet aus dem String >txt< >maxLines<-Anzahl Zeilen von unten ab"
    return '\n'.join( txt.splitlines()[-maxLines:] )













class OutConverter:
    """
    Klasse zum speichern und erweitern der History-Daten
    """
    def __init__( self ):
        self.data = ""

    #~ def escape( self, txt ):
        #~ # Evtl. vorhandene Escape Sequenzen rausfiltern
        #~ txt = re.sub(r"\033\[.*?m","",txt)
        #~ # Für Anzeige im Browser escapen
        #~ txt = xml.sax.saxutils.escape( txt )
        #~ return txt

    def put_data( self, txt ):
        # Evtl. vorhandene Escape Sequenzen rausfiltern
        txt = re.sub(r"\033\[.*?m","",txt)
        self.data += txt

    def get_data( self ):
        return self.data

    #~ def flush( self ):
        #~ pass


#~ MyOutConverter = OutConverter()




class subprocessIO:
    def __init__( self ):
        self.ansi2htmlWriter = ansi2html.Writer( sys.stdout, ansi2html_normalColor )

    def write(self, line):
        # Für das verstecke History-Form.Feld abspeichern
        MyOutConverter.put_data( line )
        # Setzt evtl. vorhandene Escape Sequenzen um
        # und schickt das Ergebnis an sys.stdout
        self.ansi2htmlWriter.write( line )

    def flush( self ):
        self.ansi2htmlWriter.close()


def cmd( command, current_dir, process_timeout ):
    MySubprocess = thread_subprocess.subprocess2( command,
                                            current_dir,
                                            subprocessIO()
                                            )
    MySubprocess.start()                    # thread starten
    MySubprocess.join(process_timeout)      # ...laufen lassen...
    MySubprocess.stop()                     # Prozess evtl. abbrechen
    MySubprocess.stdoutObj.flush()






def start_module( selfURL ):
    menu.cfg.title = "console@" + str( os.uname() )
    menu.Menu()

    #~ # HTML-Pre Ausgeben
    #~ print htmlPre % {
        #~ "charset"       : locale.getdefaultlocale()[1],
        #~ "uname"         : os.uname()
    #~ }

    ## Konfiguration lesen
    cfg = config.Parser()
    cfg.set_section("console")
    maxHistoryLines         = cfg.get( "maxHistoryLines", "int" )
    forceHTMLCompression    = cfg.get( "forceCompression" )

    # Breite der Eingabe Zeile
    input_size              = cfg.get( "input size", "int" )

    # Standartd Timeout in sek für jeden Befehl
    process_timeout         = cfg.get( "process timeout", "int" )

    # ZusatzInfornationen Anzeigen
    verbose                 = cfg.get( "verbose", "boolean" )



    #~ MyOut = CompressedOut.AutoCompressedOut( forceHTMLCompression )
    #~ print "<!-- Out-Compression:'%s' -->" % MyOut.get_mode()
    #~ for i in os.environ: print i,os.environ[i],"<br>"



    if CGIdata.has_key("stdout"):
        # Alte Ausgaben wieder anzeigen
        txt = CGIdata["stdout"]
        compressLen = len( txt )
        txt = decompress( txt )  # Ausgaben dekomprimieren

        decompressLen = len( txt )
        MyOutConverter.put_data( txt )
        print txt.replace( "\n", "<br>\n" )
    else:
        compressLen = 0
        decompressLen = 0
        txt = ""


    ## Alte Verzeichnis wieder herstellen
    if CGIdata.has_key("current_dir") and os.path.isdir( CGIdata["current_dir"] ):
        current_dir = CGIdata["current_dir"]
        # Ins alte Verzeichnis wechseln
        os.chdir( current_dir )
    else:
        current_dir = os.getcwd()


    ## Process Timeout Lesen und Anzeigen
    if CGIdata.has_key("timeout"):
        process_timeout = int( CGIdata["timeout"] )


    ## Befehl Ausführen
    if CGIdata.has_key("cmd"):
        command = CGIdata["cmd"]
        # Prompt mit Befehl anzeigen
        prompt = "<p><strong>%s>%s</strong></p>\n" % (current_dir, command)
        print prompt
        # Prompt auch in die History speichern
        MyOutConverter.put_data( prompt )

        print "<p><small>Process Timeout: %dsec.</small></p>" % process_timeout

        if command.startswith("cd "):
            # Verzeichnis wechsel
            destination_dir = command[3:]
            destination_dir = os.path.join( current_dir, destination_dir )
            destination_dir = os.path.normpath( destination_dir )
            if os.path.isdir( destination_dir ):
                # Neuer Zielpfad existiert
                current_dir = destination_dir
            else:
                print "Directory [%s] does not exists<br>" % destination_dir
        else:
            # Befehl ausführen
            cmd( command, current_dir, process_timeout )

    # Neues, aktuelles Prompt anzeigen
    print "<strong>%s&gt;</strong>" % current_dir

    # Ausgaben kürzen und Komprimieren, damit der Client weniger Daten wieder zurück senden muß
    # Die Kompression zahlt sich nach zwei, drei Befehlen i.d.R. aus...
    stdout_raw = compress( cutLines( MyOutConverter.get_data(), maxHistoryLines ) )
    #~ stdout_raw = MyOutConverter.get_data()

    if verbose:
        print "<p><small>compress: %d  decompress: %d<br />" % (compressLen, decompressLen)
        print "(console - 'verbose mode')</small></p>"


    print console_form % {
        "self"              : selfURL,
        "stdout_raw"        : stdout_raw,
        "current_dir"       : current_dir,
        "input_size"        : input_size,
        "process_timeout"   : str( process_timeout )
        }

    menu.print_footer()




#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    #~ selfURL = "console"
    #~ start_module( selfURL )
    print "Console"




