#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Verschiedene Tools für den Umgang mit PyLucid


Last commit info:
----------------------------------
$LastChangedDate$
$Rev$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev$"


import os, sys, cgi, time, re, htmlentitydefs, threading, signal, datetime


#~ from PyLucid.python_backports.utils import *

# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"

# Die response und request Objekte werden von der App hier eingepflanzt und
# können so von allen Tools benutzt werden
response = None
request = None


#_____________________________________________________________________________
def locale_datetime(t):
    """
    Aus der DB kommt ein datetime Objekt, welches wir hier als lokalisierten
    String zurück liefern
    t kann entweder direkt ein datetime-Objekt sein oder ein timestamp
    """
    if not isinstance(t, datetime.datetime):
        if isinstance(t, basestring):
            # Vielleicht ein timestamp als String?!?!
            t = float(t)
        t = datetime.datetime.fromtimestamp(t)

    datetime_format = request.l10n.get("datetime")
    datetime_format = str(datetime_format) # Darf kein unicode sein!
    return t.strftime(datetime_format)

def W3CDTF_datetime(datetime_obj):
    """
    Liefert das Datum als DCTERMS.W3CDTF zurück
    """
    assert isinstance(datetime_obj, datetime.datetime)
    return datetime_obj.strftime("%Y-%m-%d")


#_____________________________________________________________________________
def filterDict(source_dict, strKeys=[], intKeys=[], defaults={}):
    result = {}
    for key in strKeys:
        result[key] = str(source_dict[key])
    for key in intKeys:
        result[key] = int(source_dict[key])
    for key, default in defaults.iteritems():
        result[key] = source_dict.get(key, default)
    return result

#_____________________________________________________________________________
def writeDictListTable(dictlist, outobj, primaryKey = None, keyfilter=[]):
    """
    Erstellt aus einer dict-cursor-SQL-Abfrage eine einfache Tabelle und
    schreibt direkt in's outobj, was ja gut "response" sein kann ;)

    - primaryKey gibt die Spalte an, die als erstes angezeigt werden soll.

    - keyfilter ist eine liste mit keys die nicht angezeigt werden sollen
    """
    keys = dictlist[0].keys()
    keys.sort()

    # keys die in keyfilter sind "löschen":
    keys = [i for i in keys if not i in keyfilter]

    if primaryKey != None and primaryKey in keys:
        # Den primaryKey als ersten key setzten
        del(keys[keys.index(primaryKey)])   # key löschen
        keys.insert(0, primaryKey)          # an erster Stelle einfügen

    #~ db.indexResult()

    outobj.write("<table><tr>\n")
    for key in keys:
        outobj.write("\t<th>%s</th>\n" % key)
    outobj.write("</tr>\n")

    for line in dictlist:
        outobj.write("<tr>\n")
        for key in keys:
            outobj.write("\t<td>%s</td>\n" % line[key])
        outobj.write("</tr>\n")

    outobj.write("</table>\n")

#_____________________________________________________________________________
class echo:
    def __call__(self, *msg):
        response.write(
            "%s <br />\n" % " ".join([cgi.escape(str(i)) for i in msg])
        )
#_____________________________________________________________________________

def page_msg_debug(obj):
    try:
        response.page_msg("Debug:", obj.__name__)
    except AttributeError:
        pass
    result = []
    if isinstance(obj, dict):
        keys = obj.keys()
        keys.sort()
        for key in keys:
            result.append("%-25s: '%s'" % (key,obj[key]))
    result = "\n".join(result)
    response.page_msg("<pre>%s</pre>" % result)

#_____________________________________________________________________________

def getUniqueShortcut(item_name, nameList, strip=True):
    """
    Liefert einen eindeutige Abkürzung von pageName zurück.
    pageName wird von Sonderzeichen gesäubert und evtl. eine
    Zahl angehanden, wenn der Kurzname schon in nameList vorkommt.
    """
    if strip:
        import string
        ascii = string.ascii_letters + string.digits

        # Nur ASCII Zeichen erlauben und gleichzeitig trennen
        parts = [""]
        for char in item_name:
            if not char in ascii:
                parts.append("")
            else:
                parts[-1] += char

        # Erster Buchstabe immer groß geschrieben
        parts = [i[0].upper() + i[1:] for i in parts if i!=""]
        item_name = "".join(parts)

    # doppelte Namen mit Zahlen eindeutig machen
    if item_name in nameList:
        for i in xrange(1, 1000):
            testname = "%s%i" % (item_name, i)
            if testname not in nameList:
                item_name = testname
                break

    return item_name

#~ nameList = ["GibtsSchon","UndAuchDas","UndAuchDas1","UndAuchDas2"]

#~ print getUniqueShortcut("Ich bin neu!", nameList)
#~ print getUniqueShortcut("gibts schon", nameList)
#~ print getUniqueShortcut("#und!auch(das)", nameList)
#~ sys.exit()



#_____________________________________________________________________________


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
        Wird benötigt bei:
            -parent Auswahl beim editieren einer CMS Seite
            -select page to edit/delete
    """
    def __init__( self ):
        self.db = request.db

    def make_parent_option( self ):
        # Daten aus der DB holen
        data = self.db.select(
            select_items    = ["id", "name", "title", "parent"],
            from_table      = "pages",
            order           = ("position","ASC"),
        )

        # Daten umformen
        tmp = {}
        for line in data:
            parent  = line["parent"]
            id_name = (line["id"], line["name"])
            if line["parent"] in tmp:
                tmp[parent].append(id_name)
            else:
                tmp[parent] = [id_name]

        self.tree = [{"id": 0, "name":"_| root"}]
        self.build( tmp, tmp.keys() )
        return self.tree

    def build( self, tmp, keys, parent=0, deep=1 ):
        "Bildet aus den Aufbereiteten Daten"
        if not parent in tmp:
            # Seite hat keine Unterseiten
            return deep-1

        for id, name in tmp[parent]:
            # Aktuelle Seite vermerken
            self.tree.append({
                "id": id,
                "name": "%s| %s" % ("_"*(deep*3),name)
            })
            #~ print "_"*(deep*3) + name
            deep = self.build( tmp, keys, id, deep+1 )

        return deep-1






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

        result = u""
        for value, txt in data:

            if (select_value==True and value==select_item) or \
                                    (select_value==False and txt==select_item):
                selected = u' selected="selected"'
            else:
                selected = u""


            result += u'\t<option value="%s"%s>%s</option>\n' % (
                cgi.escape(str(value)), selected, cgi.escape(txt)
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




#_____________________________________________________________________________


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

#_____________________________________________________________________________


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

        #Debug:
        #~ response.page_msg("subprocess Debug:")
        #~ response.page_msg("command: '%s'" % command)
        #~ response.page_msg("cwd: '%s'" % cwd)
        #~ response.page_msg("timeout: '%s'" % timeout)

        self.killed = False # Wird True, wenn der Process gekillt wurde
        self.out_data = ""  # Darin werden die Ausgaben gespeichert

        threading.Thread.__init__(self)

        start_time = time.time()
        self.start()
        self.join(self.timeout)
        self.stop()
        duration_time = time.time() - start_time

        if duration_time >= timeout:
            # Die Ausführung brauchte zu lange, also wurde der Process
            # wahrscheinlich gekillt...
            self.killed = True

        if not hasattr(self, "process"):
            # irgendwas ist schief gelaufen :(
            self.returncode = -1
            self.out_data = "subprocess2 Error!"
            return

        # Rückgabewert verfügbar machen
        try:
            self.returncode = self.process.returncode
        except:
            self.returncode = -1

        if hasattr(sys.stdin, "encoding"):
            encoding = sys.stdin.encoding or sys.getdefaultencoding()
        else:
            encoding = sys.getdefaultencoding()

        # Da >encoding< oft auf ASCII steht schauen wir mal ob das nicht auch
        # mit einem anderen Codec geht:
        encodings = [encoding, "utf8", "latin1"]
        for encoding in encodings:
            try:
                self.out_data = unicode(
                    self.out_data, encoding, errors="strict"
                )
            except UnicodeError:
                continue
            else:
                return

        response.page_msg("Subprocess Error: No encoding found!")
        self.out_data = unicode(self.out_data, encoding, errors="replace")

    def run(self):
        "Führt per subprocess den Befehl 'self.command' aus."
        import subprocess

        try:
            self.process = subprocess.Popen(
                self.command,
                cwd     = self.cwd,
                shell   = True,
                stdout  = subprocess.PIPE,
                stderr  = subprocess.STDOUT
            )
        except Exception, e:
            msg = "subprocess2 Error: %s" % e
            response.page_msg(msg)
            self.out_data = "[%s]" % msg
        else:
            # Ausgabe
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
            os.kill(self.process.pid, signal.SIGQUIT)
        except Exception:
            # Process war schon beendet, oder os.kill() ist nicht verfügbar
            pass
        #~ else:
            #~ # Process mußte beendet werden
            #~ self.killed = True


#_____________________________________________________________________________


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


#_____________________________________________________________________________

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



#_____________________________________________________________________________

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

        if not section in menu_data:
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

#_____________________________________________________________________________



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
            sliced = self.txt[start:end]
            if isinstance(sliced, unicode):
                sliced = str(sliced)
            result.append(
                "...%s..." % sliced.encode("String_Escape")
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


#_____________________________________________________________________________

def get_codecs():
    """
    Liefert eine Liste aller unterstützter Codecs zurück
    Wird im pageadmin verwendet, für "encode from db"

    sorted and set not available in Python 2.2 ;)
    """
    from encodings import aliases

    codec_list = []
    for codec in aliases.aliases.values():
        if not codec in codec_list:
            codec_list.append(codec)

    codec_list.sort()

    return codec_list

#~ print get_codecs()




#_____________________________________________________________________________

class StringIOzipper(object):
    """
    A StringIO ZIP file maker.
    """
    def __init__(self, out_err):
        """
        out_err kann z.B. sys.stdout sein :)
        """
        import StringIO, zipfile

        self.out_err = out_err

        self._buffer = StringIO.StringIO()
        self.zip = zipfile.ZipFile(self._buffer, "w", zipfile.ZIP_DEFLATED)

    def add_file(self, arcname, data):
        """
        Fügt Dateien in's ZIP Archiv hinzu.
        """
        if not isinstance(arcname, unicode):
            self.out_err.write("Warning arcname is not unicode!")
        else:
            # Namen in ZIP-Dateien werden immer mit dem codepage 437
            # gespeichert, siehe Kommentare im Python-Bug 878120:
            #https://sourceforge.net/tracker/?func=detail&atid=105470&aid=878120&group_id=5470
            try:
                arcname = arcname.encode("cp437", "strict")
            except UnicodeError, e:
                self.out_err.write(
                    "arcname encode error: %s (Use replace error handling)" % e
                )
                arcname = arcname.encode("cp437", "replace")

        if isinstance(data, unicode):
            try:
                data = data.encode("UTF8", "strict")
            except UnicodeError, e:
                self.out_err.write(
                    "data encode error: %s (Use replace error handling)" % e
                )
                data = data.encode("UTF8", "replace")

        self.zip.writestr(arcname, data)

    def close(self):
        """
        Schließen der ZIP Datei.

        Wenn alle Dateien in die ZIP Datei geschrieben wurden, müssen wir
        die Datei schließen ist ganz wichtig, das erst dann der ZIP Header
        geschrieben wird!
        """
        self.zip.close()

        # Größe feststellen:
        self._buffer.seek(0,2) # Am Ende der Daten springen
        self._buffer_len = self._buffer.tell() # Aktuelle Position
        self._buffer.seek(0) # An den Anfang springen

    def get_StringIO(self):
        return self._buffer
    def get_len(self):
        return self._buffer_len

    def block_write(self, out_object, block_size=8192):
        """
        Schreibt die ZIP Datei blockweise in's out-Objekt
        """
        while True:
            block = self._buffer.read(block_size)
            if not block:
                break
            out_object.write(block)

        # Aufräumen:
        del(self._buffer)

    def debug(self, out):
        """
        out kann z.B. sys.stdout sein
        """
        def calc_ratio(file_size, compress_size):
            try:
                return float(compress_size)/file_size*100
            except ZeroDivisionError:
                return 100.0

        out.write("_"*79)
        out.write("StringIOzipper Debug:")
        out.write("-"*79)
        total_compress_size = 0
        for fileinfo in self.zip.infolist():
            filename = fileinfo.filename
            if filename.endswith("/"):
                # Ist ein Verzeichniss
                out.write("dir: %s" % filename)
                continue

            out.write("file: %s" % fileinfo.filename)

            total_compress_size += fileinfo.compress_size
            ratio = calc_ratio(fileinfo.file_size, fileinfo.compress_size)

            out.write(
                "compress size: %s - file_size: %s (ratio: %.2f%%)" % (
                    fileinfo.compress_size, fileinfo.file_size, ratio
                )
            )

            d = fileinfo.date_time
            out.write(
                "file date: %0.2i.%0.2i.%i %0.2i:%0.2i:%0.2i" % (
                    d[2],d[1],d[0],d[3],d[4],d[5]
                )
            )
            out.write("-"*79)

        out.write("zip len: %s" % self._buffer_len)
        out.write("total compress size: %s" % total_compress_size)

        ratio = calc_ratio(self._buffer_len, total_compress_size)
        out.write("total ratio: %.2f%%" % ratio)

        out.write("-"*79)