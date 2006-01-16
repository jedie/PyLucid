#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verschiedene Tools für den Umgang mit PyLucid
"""

__version__="0.2.1"

__history__ = """
v0.2.1
    - html_option_maker.build_from_list hat nun den zusätzlichen Parameter "select_value", damit
        kann entweder "value" oder "txt" für selected-Item herrangezogen werden. (s. Beispiel)
v0.2
    - NEU: Find_StringOperators
v0.1
    - NEU: make_table_from_sql_select()
v0.0.6
    - subprocess2(): Feststellen des self.killed (Ob der Timeout erreicht wurde) über den
        vergleich der Ausführungszeit mit der Timeout-Zeit
v0.0.5
    - Änderungen an subprocess2(): zusätzliche Exception's abgefangen
    - out_buffer() fügt kein sep mehr ein
v0.0.4
    - NEU: out_buffer()
v0.0.3
    - Komplettumbau
v0.0.2
    - einbindung der preferences
v0.0.1
    - erste Version
"""

import os, sys, cgi, time, re, htmlentitydefs, threading, signal

from PyLucid_python_backports.utils import *

# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"


PyLucid = {} # Dieses dict wird von index.py mit den Objekt-Klassen "gefüllt"


#________________________________________________________________________________________________

def convert_date_from_sql( RAWsqlDate, format="preferences" ):
    """
    Wandelt ein Datum aus der SQL-Datenbank in ein Format, welches
    in den preferences festgelegt wurde.
    """

    date = str( RAWsqlDate )
    try:
        # SQL Datum in das Python time-Format wandeln
        date = time.strptime( date, PyLucid["config"].dbconf["dbdatetime_format"] )
    except ValueError:
        # Datumsformat stimmt nicht, aber besser das was schon da
        # ist, mit einem Hinweis, zurück liefern, als garnichts ;)
        return "ERROR: convert '%s'" % date

    if format == "preferences":
        # Python-time-Format zu einem String laut preferences wandeln
        return time.strftime( PyLucid["preferences"]["core"]["formatDateTime"], date )
    elif format == "DCTERMS.W3CDTF":
        return time.strftime( "%Y-%m-%d", date )
    else:
        return time.strftime( "%x", date )

def convert_time_to_sql( time_value ):
    """
    Formatiert einen Python-time-Wert zu einem SQL-datetime-String
    """
    if type( time_value ) != time.struct_time:
        try:
            time_value = time.localtime( time_value )
        except:
            return "ERROR: convert '%s'" % time_value

    return time.strftime( PyLucid["config"].dbconf["dbdatetime_format"], time_value )

#________________________________________________________________________________________________



def formatter( number, format="%0.2f", comma=",", thousand=".", grouplength=3):
    """
    Formatierung für Zahlen
    s. http://www.python-forum.de/viewtopic.php?t=371
    Ist schneller als: locale.format("%.2f",number,1)
    und funktioniert auch, wenn die locales auf dem Betriebssystem nicht
    richtig installiert/konfiguriert sind.
    """
    if abs(number) < 10**grouplength:
        return (format % (number)).replace(".", comma)
    if format[-1]=="f":
        vor_komma,hinter_komma=(format % number).split(".",-1)
    else:
        vor_komma=format % number
        comma=""
        hinter_komma=""
    #Hier
    anz_leer=0
    for i in vor_komma:
        if i==" ":
            anz_leer+=1
        else:
            break
    vor_komma=vor_komma[anz_leer:]
    #bis hier

    len_vor_komma=len(vor_komma)
    for i in range(grouplength,len_vor_komma+(len_vor_komma-1)/(grouplength+1)-(number<0),grouplength+1):
        vor_komma=vor_komma[0:-(i)]+thousand+vor_komma[-(i):]
    return anz_leer*" "+vor_komma+comma+hinter_komma



#________________________________________________________________________________________________


class forms:
    def siteOptionList( self, with_id = False, select = 0 ):
        """
        Kombiniert html_option_maker und parent_tree_maker und erstellt eine
        HTML-Auswahlliste in der eine Seiten-ID anhand des Seitennamens ausgewählt werden kann.
        Wird u.a. beim editieren und beim löschen einer Seite verwendet
        """
        return html_option_maker().build_from_list(
            data        = parent_tree_maker().make_parent_option(),
            select_item = select
        )



class parent_tree_maker:
    """
    Generiert eine Auswahlliste aller Seiten
    Wird beim editieren für die parent-Seiten-Auswahl benötigt
    """
    def __init__( self ):
        self.db = PyLucid["db"]

    def make_parent_option( self ):
        # Daten aus der DB holen
        data = self.db.select(
            select_items    = ["id", "name", "parent"],
            from_table      = "pages",
            order           = ("position","ASC"),
        )

        # Daten umformen
        tmp = {}
        for line in data:
            parent  = line["parent"]
            id_name = ( line["id"], line["name"] )
            if tmp.has_key( line["parent"] ):
                tmp[parent].append( id_name )
            else:
                tmp[parent] = [ id_name ]

        self.tree = [ (0, "_| root") ]
        self.build( tmp, tmp.keys() )
        return self.tree

    def build( self, tmp, keys, parent=0, deep=1 ):
        "Bildet aus den Aufbereiteten Daten"
        if not tmp.has_key( parent ):
            # Seite hat keine Unterseiten
            return deep-1

        for id, name in tmp[parent]:
            # Aktuelle Seite vermerken
            self.tree.append( (id, "%s| %s" % ("_"*(deep*3),name) ) )
            #~ print "_"*(deep*3) + name
            deep = self.build( tmp, keys, id, deep+1 )

        return deep-1

#~ if __name__ == "__main__":
    #~ testdaten = {
        #~ 0: [(1, "eins"), (13, "zwei"), (9, "drei")],
        #~ 13: [(14, "zwei 1"), (15, "zwei 2")],
        #~ 14: [(16, "zwei 2 drunter")]
    #~ }
    #~ pt = parent_tree("")
    #~ pt.tree = []
    #~ pt.build( testdaten, testdaten.keys() )
    #~ for id,name in pt.tree:
        #~ print "%2s - %s" % (id,name)
    #~ sys.exit()






class html_option_maker:
    """
    Generiert eine HTML <option> 'Liste'
    """

    def build_from_dict( self, data, value_name, txt_name, select_item ):
        """

        """
        data_list = []
        for line in data:
            data_list.append(
                ( line[value_name], line[txt_name] )
            )

        return self.build_from_list( data_list, select_item )


    def build_from_list(self, data, select_item="", select_value=True):
        """
        Generiert aus >data< html-option-zeilen

        data als liste
        --------------
        data = ["eins","zwei"]
        selected_item = "zwei"
        ==>
        <option value="eins">eins</option>
        <option value="zwei" selected="selected">zwei</option>

        data als tupel-Liste
        --------------------
        data = [ (1,"eins"), (2,"zwei") ]
        selected_item = 1
        ==>
        <option value="1" selected="selected">eins</option>
        <option value="2">zwei</option>

        data als tupel-Liste und select_value=False
        -------------------------------------------
        data = [ (1,"eins"), (2,"zwei") ]
        selected_item = "zwei"
        ==>
        <option value="1">eins</option>
        <option value="2" selected="selected">zwei</option>
        """

        try:
            test1,test2 = data[0]
        except ValueError:
            # data hat kein Wertepaar, also wird eins erzeugt ;)
            data = [(i,i) for i in data]

        result = ""
        for value, txt in data:

            if (select_value==True and value==select_item) or (select_value==False and txt==select_item):
                selected = ' selected="selected"'
            else:
                selected = ""

            result += '\t<option value="%s"%s>%s</option>\n' % (
                cgi.escape( str(value) ), selected, cgi.escape( str(txt) )
            )

        return result


#~ if __name__ == "__main__":
    #~ data = ["eins","zwei"]
    #~ selected_item = "zwei"
    #~ print html_option_maker().build_from_list( data, selected_item )
    #~ print "-"*80
    #~ data = [ (1,"eins"), (2,"zwei") ]
    #~ selected_item = 1
    #~ print html_option_maker().build_from_list( data, selected_item )
    #~ print "-"*80
    #~ data = [ (1,"eins"), (2,"zwei") ]
    #~ selected_item = "zwei"
    #~ print html_option_maker().build_from_list( data, selected_item, select_value=False )
    #~ sys.exit()




#________________________________________________________________________________________________


class out_buffer:
    """
    Hilfsklasse um Ausgaben erst zwischen zu speichern und dann gesammelt zu erhalten
    """
    def __init__( self ):
        self.data = ""
        self.sep = "\n"

    def set_sep( self, sep ):
        self.sep = sep

    def write( self, *txt ):
        txt = [str(i) for i in txt]
        #~ self.data += self.sep + " ".join( txt )
        self.data += " ".join( txt )

    def __call__( self, *txt ):
        self.write( *txt )

    def get( self ):
        return self.data

    def flush( self ):
        return

class redirector:
    def __init__( self ):
        self.oldout = sys.stdout
        self.olderr = sys.stderr

        self.out_buffer = out_buffer()
        sys.stdout = self.out_buffer
        sys.stderr = self.out_buffer

    def get( self ):
        sys.stdout = self.oldout
        sys.stderr = self.olderr
        return self.out_buffer.get()

class stdout_marker:
    """
    Debug Anzeige, woher print-Ausgaben kommen
    """
    def __init__(self):
        self.org_stdout = sys.stdout
        sys.stdout = self

    def write( self, *txt ):
        import inspect
        for stack in inspect.stack():
            filename = stack[1].replace("\\","/").split("/")[-1]
            if filename=="tools.py": continue
            self.org_stdout.write( "%-20s line %3s %s\n" % (
                    filename, stack[2], stack[3]
                )
            )
            #~ self.org_stdout.write( str(stack) )
        self.org_stdout.write( " ".join([str(i) for i in txt]) + "\n" )

#~ print "redirector test:"
#~ r = redirector()
#~ print "1"
#~ out = r.get()
#~ print "2"
#~ print "out:", out
#~ sys.exit()

#________________________________________________________________________________________________


class subprocess2(threading.Thread):
    """
    Allgemeine Klasse um subprocess mit einem Timeout zu vesehen.

    Da os.kill() nur unter Linux und Mac verfügbar ist, funktioniert das
    ganze nicht unter Windows :(

    Beispiel Aufruf:
    ---------------------------------------------------------
    import os, subprocess, threading, signal

    process = subprocess2( "top", "/", timeout = 2 )

    if process.killed == True:
        print "Timout erreicht! Prozess wurde gekillt."
    print "Exit-Status:", process.returncode
    print "Ausgaben:", process.out_data
    ---------------------------------------------------------
    """
    def __init__( self, command, cwd, timeout ):
        self.command    = command
        self.cwd        = cwd
        self.timeout    = timeout

        self.killed = False # Wird True, wenn der Process gekillt wurde
        self.out_data = "" # Darin werden die Ausgaben gespeichert

        threading.Thread.__init__(self)

        start_time = time.time()
        self.start()
        self.join( self.timeout )
        self.stop()
        duration_time = time.time() - start_time

        if duration_time >= timeout:
            # Die Ausführung brauchte zu lange, also wurde der Process
            # wahrscheinlich gekillt...
            self.killed = True

        # Rückgabewert verfügbar machen
        try:
            self.returncode = self.process.returncode
        except:
            self.returncode = -1

    def run(self):
        "Führt per subprocess den Befehl 'self.command' aus."

        try:
            import subprocess
        except ImportError:
            # subprocess gibt's erst mit Python 2.4
            from PyLucid_python_backports import subprocess

        self.process = subprocess.Popen(
                self.command,
                cwd     = self.cwd,
                shell   = True,
                stdout  = subprocess.PIPE,
                stderr  = subprocess.STDOUT
            )

        # Ausgaben speichern
        self.out_data = self.process.stdout.read()

    def stop( self ):
        """
        Testet ob der Prozess noch läuft, wenn ja, wird er mit
        os.kill() (nur unter UNIX verfügbar!) abgebrochen.
        """
        #~ poll = self.process.poll()
        #~ except:
            #~ pass
        #~ else:
        #~ if poll != None:
            # Prozess ist schon beendet
            #~ return
        #~ self.killed = True

        try:
            os.kill( self.process.pid, signal.SIGQUIT )
        except Exception:
            # Process war schon beendet, oder os.kill() ist nicht verfügbar
            pass
        #~ else:
            #~ # Process mußte beendet werden
            #~ self.killed = True



#________________________________________________________________________________________________


class email:
    def send(self, to, subject, text):
        import time, smtplib
        from email.MIMEText import MIMEText

        msg = MIMEText(
            _text = text,
            _subtype = "plain",
            _charset = "UTF-8"
        )
        msg['From'] = "auto_mailer@jensdiemer.de"
        msg['To'] = to
        msg['Subject'] = subject
        # Datum nach RFC 2822 Internet email standard.
        msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        msg['User-Agent'] = "PyLucid (Python v%s)" % sys.version

        s = smtplib.SMTP()
        s.connect()
        s.sendmail(msg['From'], [msg['To']], msg.as_string())
        s.close()


#________________________________________________________________________________________________


def make_table_from_sql_select(select_results, id, css_class):
    """ Allgemeine Information um SQL-SELECT Ergebnisse als Tabelle zu erhalten """
    result = '<table id="%s" class="%s">\n' % (id,css_class)

    # Tabellen überschriften generieren
    result += "<tr>\n"
    for key in select_results[0].keys():
        result += "\t<th>%s</th>\n" % key
    result += "</tr>\n"

    # eigentlichen Tabellen Daten erzeugen
    for line in select_results:
        result += "<tr>\n"
        for value in line.values():
            result += "\t<td>%s</td>\n" % value
        result += "</tr>\n"

    result += "</table>\n"
    return result


#________________________________________________________________________________________________

#~ class convertdateformat:
    #~ """
    #~ !!!OBSOLETE!!!

    #~ Wandelt das PHP-date Format in's Python-Format
    #~ z.B. PHP-date "j.m.Y G:i" -> "%d.%m.%Y - %H:%M"

    #~ PHP-Format:
    #~ selfphp.info/funktionsreferenz/datums_und_zeit_funktionen/date.php#beschreibung

    #~ Python-Format:
    #~ docs.python.org/lib/module-time.html#l2h-1941

    #~ nicht eingebaute PHP-Formate:
    #~ --------------------------------------------------------------------
    #~ B - Tage bis Jahresende
    #~ I - (großes i) 1 bei Sommerzeit, 0 bei Winterzeit
    #~ L - Schaltjahr = 1, kein Schaltjahr = 0
    #~ O - Zeitunterschied gegenüber Greenwich (GMT) in Stunden (z.B.: +0100)
    #~ r - Formatiertes Datum (z.B.: Tue, 6 Jul 2004 22:58:15 +0200)
    #~ S - Englische Aufzählung (th für 2(second))
    #~ t - Anzahl der Tage des Monats (28 – 31)
    #~ T - Zeitzoneneinstellung des Rechners (z.B. CEST)
    #~ U - Sekunden seit Beginn der UNIX-Epoche (1.1.1970)
    #~ Z - Offset der Zeitzone gegenüber GTM (-43200 – 43200) in Minuten

    #~ nicht eingebaute Python-Formate:
    #~ --------------------------------------------------------------------
    #~ %c 	Locale's appropriate date and time representation.
    #~ %x 	Locale's appropriate date representation.
    #~ %X 	Locale's appropriate time representation.
    #~ %Z 	Time zone name (no characters if no time zone exists).
    #~ """
    #~ def __init__( self ):
        #~ self.PHP2Python_date = {
            #~ "d" : "%d", # Tag des Monats *( 01 – 31 )
            #~ "j" : "%d", # Tag des Monats (1-31)
            #~ "D" : "%a", # Tag der Woche (3stellig:Mon)
            #~ "l" : "%A", # Tag der Woche (ausgeschrieben:Monday)

            #~ "m" : "%m", # Monat *(01-12)
            #~ "n" : "%m", # Monat (1-12)
            #~ "F" : "%B", # Monatsangabe (December – ganzes Wort)
            #~ "M" : "%b", # Monatsangabe (Feb – 3stellig)

            #~ "y" : "%y", # Jahreszahl, zweistellig (01)
            #~ "Y" : "%Y", # Jahreszahl, vierstellig (2001)

            #~ "g" : "%I", # Stunde im 12-Stunden-Format (1-12 )
            #~ "G" : "%H", # Stunde im 24-Stunden-Format (0-23 )
            #~ "h" : "%I", # Stunde im 12-Stunden-Format *(01-12 )
            #~ "H" : "%H", # Stunde im 24-Stunden-Format *(00-23 )
            #~ "i" : "%M", # Minuten *(00-59)
            #~ "s" : "%S", # Sekunden *(00 – 59)

            #~ "a" : "%p", # "am" oder "pm"
            #~ "A" : "%p", # "AM" oder "PM"

            #~ "w" : "%w", # Wochentag als Zahl (0(Sonntag) bis 6(Samstag))
            #~ "W" : "%W", # Wochennummer des Jahres (z.B. 28)
            #~ "z" : "%j"  # Tag des Jahres als Zahl (z.B. 148 (entspricht 29.05.2001))
        #~ }

    #~ def convert( self, formatDateTime ):
        #~ "PHP-date Format in Python-Format umwandeln"

        #~ for item in re.findall(r"\w", formatDateTime ):
            #~ formatDateTime = formatDateTime.replace( item, self.PHP2Python_date[item] )

        #~ return formatDateTime

#~ formatDateTime = "j.m.Y G:i"
#~ print formatDateTime
#~ formatDateTime = convertdateformat().convert( formatDateTime )
#~ print formatDateTime
#~ sys.exit()



#________________________________________________________________________________________

def build_menu(module_manager_data, action_url):
    """
    Generiert automatisch aus den module_manager_data ein "Action"-Menü.
    Wird zur aufgerufenden Klasse übertragen.
    """
    menu_data = {}
    for method, data in module_manager_data.iteritems():
        #~ self.page_msg( method, data )
        try:
            data = data["menu_info"]
        except:
            #~ self.page_msg( "No menu_info for %s" % method )
            continue

        try:
            section     = data["section"]
            description = data["description"]
        except Exception, e:
            self.page_msg( "Error in menu_info:", e )
            continue

        if not menu_data.has_key( section ):
            menu_data[section] = []

        menu_data[section].append(
            [ method, description ]
        )

    #~ self.page_msg( "Debug:", menu_data )

    print "<ul>"
    for section, data in menu_data.iteritems():
        print "\t<li><h5>%s</h5>" % section
        print "\t<ul>"
        for item in data:
            print '\t\t<li><a href="%s%s">%s</a></li>' % (
                action_url, item[0], item[1]
            )
        print "\t</ul>"
        print "\t</li>"
    print "</ul>"

#________________________________________________________________________________________



class Find_StringOperators:
    """
    Sucht in einem String nach %-StringOperatoren.
    Dabei wird zwischen richtigen und falschen unterschieden.

    Dient zur besseren Fehlerausgabe, bei String Operationen.

    Test-Text:
    ----------
    Hier ist ein Beispieltext mit %(richtigen)s Platzhaltern.
    Aber auch mit %(falschen, da die hier Klammer nicht geschlossen ist.
    Außerdem müßen einzelne %-Zeichen, immer escaped werden. Das wird
    mit doppelten %% Zeichen gemacht, die nach dem String-Operation,
    bei dem die %(Platzhalter)s durch Daten aus einem Dict ersetzt werden,
    wieder zu einfachen %-Zeichen umgewandelt werden.
    """

    cutout = 20

    def __init__(self, txt):
        self.correct_hit_pos = []
        self.correct_tags = []
        self.incorrect_hit_pos = []
        self.txt = txt

        # alle %-Zeichen, die nicht mit %%-Escaped sind
        pattern = re.compile(r"([^%]%[^%])")
        pattern.sub(self._incorrect_hit, txt)

        # Richtig %(formatierte)s String
        pattern = re.compile(r"([^%]%\((.*?)\)s)")
        pattern.sub(self._correct_hit, txt)

    def _incorrect_hit(self, matchobj):
        self.incorrect_hit_pos.append(matchobj.start())

    def _correct_hit(self, matchobj):
        self.incorrect_hit_pos.remove(matchobj.start())
        self.correct_hit_pos.append(matchobj.start())
        self.correct_tags.append(matchobj.group(2))

    #_______________________________________________________________________
    # Zugriff auf die Daten

    def get_incorrect_pos(self):
        "Start- & End-Liste der falschen %-Operatoren"
        return self.get_pos(self.incorrect_hit_pos)

    def get_correct_pos(self):
        "Start- & End-Liste der richtigen %-Operatoren"
        return self.get_pos(self.correct_hit_pos)

    def get_incorrect_text_summeries(self):
        "Textstellen mit falschen %-Operatoren"
        return self.slice_pos_list(self.get_incorrect_pos())

    def get_correct_text_summeries(self):
        "Textstellen mit richtigen %-Operatoren"
        return self.slice_pos_list(self.get_correct_pos())

    def get_pos(self, poslist):
        """
        Wandelt aus der Positionsliste eine Liste mit
        Start- und End-Positionen für einen Text-Slice
        """
        results = []
        for pos in poslist:
            start = pos - self.cutout
            end = pos + self.cutout
            if start<0:
                start = 0
            if end>len(self.txt):
                end = len(self.txt)

            results.append((start, end))
        return results

    def slice_pos_list(self, pos_list):
        """
        Liefert eine Liste der Textstellen zurück.
        """
        result = []
        for start,end in pos_list:
            result.append(
                "...%s..." % self.txt[start:end].encode("String_Escape")
            )
        return result

    #_______________________________________________________________________
    # Debug

    def debug_results(self):
        print "self.incorrect_hit_pos:", self.incorrect_hit_pos
        print "incorrect_pos:", self.get_incorrect_pos()
        print ">>> Textstellen mit falsche %-Zeichen im Text:"
        for i in self.get_incorrect_text_summeries():
            print i

        print
        print "self.correct_hit_pos:", self.correct_hit_pos
        print "correct_pos:", self.get_correct_pos()
        print ">>> Textstellen mit richtige %-StringOperatoren:"
        for i in self.get_correct_text_summeries():
            print i

#~ doc = Find_StringOperators.__doc__
#~ print doc
#~ print "-"*80
#~ s = Find_StringOperators(doc)
#~ print "incorrect_pos:", s.get_incorrect_pos()
#~ print "correct_pos:", s.get_correct_pos()
#~ print "-"*80
#~ s.debug_results()


#________________________________________________________________________________________

def get_codecs():
    """
    Liefert eine Liste aller unterstützter Codecs zurück
    Wird im pageadmin verwendet, für "encode from db"
    """
    from encodings import aliases
    return sorted(list(set(aliases.aliases.values())))


#~ print get_codecs()

