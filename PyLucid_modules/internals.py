#!/usr/bin/python
# -*- coding: UTF-8 -*-

# by jensdiemer.de (steht unter GPL-License)

"""
Administration Sub-Menü : "show internals"
"""

__author__ = "Jens Diemer (www.jensdiemer.de)"

__version__="0.0.4"

__history__="""
v0.0.4
    - Andere Handhabung von tools
v0.0.3
    - verweinfachung in SQL_table_status() und optimize_sql_table() durch MySQLdb.cursors.DictCursor
v0.0.2
    - NEU SQL-Tabellen übersicht + Optimieren
v0.0.1
    - erste Version
"""

__todo__ = """
"""

# Python-Basis Module einbinden
import os, sys, cgi

# Dynamisch geladene Module
## import locale - internals.system_info()



# Für Debug-print-Ausgaben
#~ print "Content-type: text/html\n\n<pre>%s</pre>" % __file__
#~ print "<pre>"



#_______________________________________________________________________
# Module-Manager Daten


class module_info:
    """Pseudo Klasse: Daten f���den Module-Manager"""
    data = {
        "internals" : {
            "txt_menu"      : "show internals",
            "txt_long"      : "show PyLucid's internal data v" + __version__,
            "section"       : "admin sub menu",
            "category"      : "misc",
            "must_login"    : True,
            "must_admin"    : True,
        },
    }



#_______________________________________________________________________


class stdout_saver:
    def __init__( self ):
        self.old_stdout = sys.stdout
        self.data = ""

    def write( self, txt ):
        self.data += txt

    def get( self ):
        sys.stdout = self.old_stdout
        return self.data

#~ sys.stdout = stdout_saver()

#_______________________________________________________________________


class internals:
    def __init__( self, PyLucid ):
        self.CGIdata    = PyLucid["CGIdata"]
        #~ self.CGIdata.debug()
        self.db         = PyLucid["db"]

        self.log        = PyLucid["log"]

        self.session    = PyLucid["session"]
        #~ self.session.debug()

        self.config     = PyLucid["config"]
        self.tools      = PyLucid["tools"]

        self.optimize_table_link  = '<a href="'
        self.optimize_table_link += self.config.system.poormans_url
        self.optimize_table_link += '?command=internals&optimize" title="optimize all SQL tables">optimize tables</a>'

        self.back_link = '<a href="%s?command=internals">back</a>' % self.config.system.poormans_url

    def action( self ):
        # Aktion starten
        if self.CGIdata.has_key("optimize"):
            return self.optimize_sql_table()

        page = "<h2>%s</h2>" % module_info().data["internals"]["txt_long"]
        page += self.session_data()
        page += self.system_info()
        page += self.SQL_table_status()
        page += self.log_data()
        page += self.os_environ()
        return page

    #_______________________________________________________________________
    # Informations-Methoden

    def session_data( self ):
        """ Session Informationen anzeigen """
        page = "<h3>session data</h3>"
        page += '<table id="internals_session_data" class="internals_table">'
        for k,v in self.session.iteritems():
            page += "<tr>"
            page += "<td>%s</td>" % k
            page += "<td>: %s</td>" % v
            #~ page += "%s:%s\n" % (k,v)
            page += "</tr>"
        page += "</table>"

        result = self.db.select(
                select_items    = ["session_data"],
                from_table      = "session_data",
                where           = [("session_id",self.session.ID)]
            )
        for line in result:
            page += str( line ).replace("\\n","<br/>")

        return page

    def system_info( self ):
        """ Allgemeine System Informationen """
        page = "<h3>system info</h3>"

        page += '<dl id="system_info">'
        if hasattr(os,"uname"):
            page += "<dt>os.uname():</dt>"
            page += "<dd>%s</dd>" % " - ".join( os.uname() )

        import locale

        page += "<dt>locale.getlocale():</dt>"
        page += "<dd>%s</dd>" % str( locale.getlocale() )
        page += "<dt>locale.getdefaultlocale():</dt>"
        page += "<dd>%s</dd>" % str( locale.getdefaultlocale() )
        page += "<dt>locale.getpreferredencoding():</dt>"
        try:
            page += "<dd>%s</dd>" % str( locale.getpreferredencoding() )
        except Exception, e:
            page += "<dd>Error: %s</dd>" % e

        page += "</dl>"

        return page

    def SQL_table_status( self ):
        page = "<h3>SQL table status</h3>"

        SQLresult = self.db.fetchall( "SHOW TABLE STATUS" )

        page += '<table id="internals_log_information" class="internals_table">'

        # Tabellen überschriften generieren
        page += "<tr>"
        page += "<th>name</th>"
        page += "<th>entries</th>" # Rows
        page += "<th>update_time</th>"
        page += "<th>size</th>"
        page += "<th>overhang</th>" # data_free
        page += "<th>collation</th>"
        page += "</tr>"

        total_rows = 0
        total_size = 0
        total_data_free = 0
        # eigentlichen Tabellen Daten erzeugen
        for line in SQLresult:
            page += "<tr>"
            page += "<td>%s</td>" % line["Name"]

            page += '<td style="text-align: right;">%s</td>' % line["Rows"]
            total_rows += line["Rows"]

            page += "<td>%s</td>" % line["Update_time"]

            size = line["Data_length"] + line["Index_length"]
            page += '<td style="text-align: right;">%sKB</td>' % self.tools.formatter( size/1024.0, "%0.1f")
            total_size += size

            if line["Data_free"]>0:
                data_free_size = "%sBytes" % self.tools.formatter( line["Data_free"], "%i" )
            else:
                data_free_size = '-'
            page += '<td style="text-align: center;">%s</td>' % data_free_size
            total_data_free += line["Data_free"]

            page += "<td>%s</td>" % line["Collation"]
            #~ page += "<td>%s</td>" % line["Comment"]
            page += "</tr>"

        page += '<tr style="font-weight:bold">'
        page += "<td></td>"
        page += '<td style="text-align: right;">%s</td>' % total_rows
        page += "<td></td>"
        page += '<td style="text-align: right;">%sKB</td>' % self.tools.formatter( total_size/1024.0, "%0.1f")
        page += '<td style="text-align: center;">%sBytes</td>' % self.tools.formatter( total_data_free, "%i" )
        page += "<td></td>"
        page += "</tr>"

        page += "</table>"

        page += "<p>%s</p>" % self.optimize_table_link

        return page

    def make_table_from_sql_select( self, select_results, id, css_class ):
        """ Allgemeine Information um SQL-SELECT Ergebnisse als Tabelle zu erhalten """
        table = '<table id="%s" class="%s">' % (id,css_class)

        # Tabellen überschriften generieren
        table += "<tr>"
        for key in select_results[0].keys():
            table += "<th>%s</th>" % key
        table += "</tr>"

        # eigentlichen Tabellen Daten erzeugen
        for line in select_results:
            table += "<tr>"
            for value in line.values():
                table += "<td>%s</td>" % value
            table += "</tr>"

        table += "</table>"

        return table


    def log_data( self ):
        """ Logging Informationen anzeigen """
        limit = 100 # Anzahl der Einträge die angezeigt werden sollen
        page  = "<h3>log information (last %i)</h3>" % limit
        page += self.make_table_from_sql_select(
            self.log.get_last_logs( limit ),
            id          = "internals_log_data",
            css_class   = "internals_table"
        )
        return page

    def os_environ( self ):
        page  = "<h3>OS-Enviroment:</h3>"
        page += '<dl id="environment">'
        keys = os.environ.keys()
        keys.sort()
        for key in keys:
            value = os.environ[key]
            page += "<dt>%s</dt>" % key
            page += "<dd>%s</dd>" % value
        page += "</dl>"

        return page

    #_______________________________________________________________________
    # Funktionen

    def optimize_sql_table( self ):
        page  = "<h3>optimize SQL tables</h3>"

        SQLresult = self.db.fetchall( "SHOW TABLE STATUS" )

        # Tabellen mit Überhang rausfiltern
        tables_to_optimize = []
        for line in SQLresult:
            if line["Data_free"]>0:
                # Tabelle hat Überhang
                tables_to_optimize.append( line["Name"] )

        if len(tables_to_optimize) > 0:
            # Tabellen optimieren
            tables_to_optimize = ",".join( tables_to_optimize )

            SQLresult = self.db.fetchall( "OPTIMIZE TABLE %s" % tables_to_optimize )

            page += '<table id="optimize_table" class="internals_table">'

            # Überschriften
            page += "<tr>"
            for desc in SQLresult[0].keys():
                page += "<th>%s</th>" % desc
            page += "</tr>"

            # Ergebniss Werte auflisten
            for line in SQLresult:
                page += '<tr style="text-align: center;">'
                for value in line.values():
                    page += "<td>%s</td>" % value
                page += "</tr>"

            page += "</table>"
        else:
            page += "<p>All Tables already up to date.</p>"

        page += self.SQL_table_status()

        page += self.back_link
        return page


#_______________________________________________________________________
# Allgemeine Funktion, um die Aktion zu starten

def PyLucid_action( PyLucid ):
    # Aktion starten
    return internals( PyLucid ).action()