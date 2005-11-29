#!/usr/bin/python
# -*- coding: UTF-8 -*-

""" <lucidTag:liste_kunden /> """

__version__="0.0.1"
__history__=""" v0.0.1 - erste Version """

#import cgitb;cgitb.enable()
import os, sys, urllib
from pywawi import func




edit_template = '''
<form method="post" action="%(url)supdatedb&amp;id=%(id)s" name="kunden">
 <fieldset><legend><b>Stammdaten</b></legend>
 <table class="tablelook" class="tablelook" cellpadding="0" cellspacing="5" border="0">
  <tbody>
   <tr>
    <td class="label" align="right">Kd.Nr.:</td>
    <td><input class="textfeld"  name="kdnr" value="%(kdnr)s" /></td>
    <td class="label" align="right">Firmenkunde:</td>
    <td><input class="textfeld"  name="ist_firmenkunde" value="%(ist_firmenkunde)s" /></td>
    <td align="right" colspan="2"><input type="submit" name="showtime" value="Speichern"></td>
    <td><td align="right" colspan="2"><input type="submit" name="showtime" value="L&#246;schen"></td>
   </tr>
   <tr>
    <td class="label" align="right">Anrede:</td>
    <td><input class="textfeld"  name="anrede" value="%(anrede)s" /></td>
    <td colspan="4">&nbsp;</td>
   </tr>
   <tr>
    <td colspan="6">&nbsp;</td>
   </tr>
   <tr>
    <td class="label" align="right">Name:</td>
    <td><input class="textfeld"  name="name" value="%(name)s" /></td>
    <td class="label" align="right">Vorname:</td>
    <td><input class="textfeld"  name="vorname" value="%(vorname)s" /></td>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td class="label" align="right">Strasse:</td>
    <td colspan="4"><input class="textfeld"  name="strasse" value="%(strasse)s" /></td>
  </tr>
  <tr>
   <td class="label" align="right">PLZ:</td>
   <td><input class="textfeld"  name="plz" value="%(plz)s" /></td>
   <td class="label" align="right">Ort:</td>
   <td><input class="textfeld"  name="ort" value="%(ort)s" /></td>
   <td colspan="4">&nbsp;</td>
  </tr>
  <tr>
   <td class="label" align="right">Land:</td>
   <td><input class="textfeld"  name="land" value="%(land)s" /></td>
   <td colspan="4"></td>
  </tr>
  <tr>
   <td colspan="6">&nbsp;</td>
  </tr>
  <tr>
   <td class="label" align="right">Telefon1:</td>
   <td><input class="textfeld"  name="telefon1" value="%(telefon1)s" /></td>
   <td class="label" align="right">Telefon2:</td>
   <td><input class="textfeld"  name="telefon2" value="%(telefon2)s" /></td>
   <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
   <td class="label" align="right">Fax:</td>
   <td><input class="textfeld"  name="fax" value="%(fax)s" /></td>
   <td class="label" align="right">E-Mail:</td>
   <td><input class="textfeld"  name="email" value="%(email)s" /></td>
   <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
   <td class="label" align="right">Mobil:</td>
   <td colspan="4"><input class="textfeld"  name="mobil" value="%(mobil)s" /></td>
  </tr>
  <tr>
    <td colspan="6">&nbsp;</td>
  </tr>
  <tr>
    <td class="label" align="right">Firma:</td>
    <td><input class="textfeld"  name="firma" value="%(firma)s" /></td>
    <td class="label" align="right">Kontakt:</td>
    <td><input class="textfeld"  name="kontakt" value="%(kontakt)s" /></td>
    <td colspan="2"></td>
  </tr>
  <tr>
    <td class="label" align="right">Matchcode:</td>
    <td><input class="textfeld"  name="matchcode" value="%(matchcode)s" /></td>
    <td class="label" align="right">Zusatz:</td>
    <td><input class="textfeld"  name="zusatz" value="%(zusatz)s" /></td>
    <td colspan="2">&nbsp;</td>
  </tr>
  <tr>
    <td colspan="6">&nbsp;</td>
  </tr>
  </tbody>
 </table>
 </fieldset>

 <br />

 <fieldset><legend><b>Zahlung</b></legend>
 <table class="tablelook" cellpadding="0" cellspacing="5" border="0">
  <tbody>
   <tr>
    <td class="label" align="right">Zahlungsart:</td>
    <td><input class="textfeld"  name="zahlart" value="%(zahlart)s" /></td>
    <td class="label" align="right">Zahlungsziel:</td>
    <td><input class="textfeld"  name="zahlziel" value="%(zahlziel)s" /></td>
    <td align="right" colspan="2"><input type="submit" name="showtime" value="Speichern"></td>
    <td><td align="right" colspan="2"><input type="submit" name="showtime" value="L&#246;schen"></td>
   </tr>
   <tr>
    <td class="label" align="right">Kontonummer:</td>
    <td><input class="textfeld"  name="kntnr" value="%(kntnr)s" /></td>
    <td class="label" align="right">BLZ:</td>
    <td><input class="textfeld"  name="blz" value="%(blz)s" /></td>
    <td colspan="2">&nbsp;</td>
   </tr>
   <tr>
    <td class="label" align="right">Bankeinzug:</td>
    <td><input class="textfeld"  name="einzug" value="%(einzug)s" /></td>
    <td class="label" align="right">Lieferstop:</td>
    <td><input class="textfeld"  name="lieferstopp" value="%(lieferstopp)s" /></td>
    <td colspan="2">&nbsp;</td>
   </tr>
  </tbody>
 </table>
 </fieldset>

 <br />

 <fieldset><legend><b>Abweichende Lieferung</b></legend>
 <table class="tablelook" cellpadding="0" cellspacing="5" border="0">
  <tbody>
   <tr>
    <td class="label" align="right">Liefername:</td>
    <td><input class="textfeld"  name="liefername" value="%(liefername)s" /></td>
    <td class="label" align="right">Liefervorname:</td>
    <td><input class="textfeld"  name="liefervorname" value="%(liefervorname)s" /></td>
    <td align="right" colspan="2"><input type="submit" name="showtime" value="Speichern"></td>
    <td><td align="right" colspan="2"><input type="submit" name="showtime" value="L&#246;schen"></td>
   </tr>
   <tr>
    <td class="label" align="right">Lieferfirma:</td>
    <td colspan="4"><input class="textfeld"  name="lieferfirma" value="%(lieferfirma)s" /></td>
   </tr>
   <tr>
    <td class="label" align="right">Lieferadresse:</td>
    <td><input class="textfeld"  name="lieferdelta" value="%(lieferdelta)s" /></td>
    <td class="label" align="right">Liefer Strasse:</td>
    <td><input class="textfeld"  name="lieferstrasse" value="%(lieferstrasse)s" /></td>
    <td colspan="2">&nbsp;</td>
   </tr>
   <tr>
    <td class="label" align="right">Liefer PLZ:</td>
    <td><input class="textfeld"  name="lieferplz" value="%(lieferplz)s" /></td>
    <td class="label" align="right">Lieferort:</td>
    <td><input class="textfeld"  name="lieferort" value="%(lieferort)s" /></td>
    <td colspan="2">&nbsp;</td>
   </tr>
   <tr>
    <td class="label" align="right">Lieferland:</td>
    <td colspan="4"><input class="textfeld"  name="lieferland" value="%(lieferland)s" /></td>
   </tr>
  </tbody>
 </table>

 </fieldset>
</form>
<style>
.textfeld { color: navy; font-size: 10px; font-weight: bold; background-color: #DDEEFF; }
.label { color: grey; font-size:10px; font-weight: bold;}
.tablelook { margin-left: auto;  }
</style>

'''







class liste_kunden:
    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
        },

        "select" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"select": str},
        },

        "edit" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"id": int},
        },

        "suchen" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"suchwort": str},
        },
       "sortcol" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"col": str, "order": str},
        },
       "updatedb" : {
            "must_login"    : False,
            "must_admin"    : False,
            "get_CGI_data"  : {"id": int, "showtime": str},
        },
    }

    def __init__( self, PyLucid ):
        self.CGIdata        = PyLucid["CGIdata"]
        self.db             = PyLucid["db"]
        self.config         = PyLucid["config"]
        self.tools          = PyLucid["tools"]

        self.html_part = func.html_part(PyLucid)


    def lucidTag( self ):

        self.html_part.set_urls(self.action_url, self.main_action_url)

        felder = [ "kdnr", "name", "vorname", "strasse", "plz", "ort"]
        SQLresult = self.db.select(
            select_items    = felder + ["firma"],
            from_table      = "endkunden",
            order           = ( "name", "ASC" )
        )

        self.html_part.generiere_tabelle(felder, SQLresult)

    def select(self, select):
        if select=="ALLE":
            self.lucidTag
            return

        self.html_part.set_urls(self.action_url, self.main_action_url)

        SQLresult = self.db.fetchall(
            SQLcommand = "SELECT * FROM endkunden WHERE name LIKE %s order by name asc",
            SQL_values = ( "%s%%" % select, )
        )

        felder = [ "kdnr", "name", "vorname", "strasse", "plz", "ort"]
        self.html_part.generiere_tabelle(felder, SQLresult)


    def suchen(self, suchwort):

        self.html_part.set_urls(self.action_url, self.main_action_url)

        felder = [ "kdnr", "name", "vorname", "strasse", "plz", "ort"]

        SQLresult = self.db.select(
            select_items    = felder + ["firma"],
            from_table      = "endkunden",
            where           = ( "name", suchwort ),
            order           = ( "name", "ASC" )
        )

        self.html_part.generiere_tabelle(felder, SQLresult)


    def sortcol(self, col, order):
        self.html_part.set_urls(self.action_url, self.main_action_url)

        if col:
            SQLString = 'select * from endkunden order by '+ col +' '+ order

            SQLresult = self.db.fetchall( SQLcommand = SQLString  )

            felder = [ "kdnr", "name", "vorname", "strasse", "plz", "ort"]
            self.html_part.generiere_tabelle(felder, SQLresult)


    def edit(self, id):
        self.html_part.set_urls(self.action_url, self.main_action_url)

        SQLresult = self.db.select(
            select_items    = "*",
            from_table      = "endkunden",
            where           = ( "kdnr", id ),
        )[0]

        # Daten zum dict hinzufügen
        SQLresult.update({
            "url": self.action_url,
            "id": id
        })

        print edit_template % SQLresult


    def updatedb(self, id, showtime):
        self.html_part.set_urls(self.action_url, self.main_action_url)

        print '<div align="center">\n <b>UpdateDB:</b>&nbsp;&nbsp;\n'

        if showtime == "Speichern":
          '''
          data = {
            "kdnr"              : kdnr,
            "anrede"            : anrede,
            "name"              : name,
            "vorname"           : vorname,
            "firma"             : firma,
            "matchcode"         : matchcode,
            "zusatz"            : zusatz,
            "kontakt"           : kontakt,
            "strasse"           : strasse,
            "plz"               : plz,
            "ort"               : ort,
            "land"              : land,
            "telefon1"          : telefon1,
            "telefon2"          : telefon2,
            "fax"               : fax,
            "email"             : email,
            "mobil"             : mobil,
            "zahlart"           : zahlart,
            "zahlziel"          : zahlziel,
            "einzug"            : einzug,
            "kontoname"         : kontoname,
            "blz"               : blz,
            "kntnr"             : kntnr,
            "lieferstopp"       : lieferstopp,
            "ist_firmenkunde"   : ist_firmenkunde,
            "lieferdelta"       : lieferdelta,
            "liefername"        : liefername,
            "liefervorname"     : liefervorname,
            "lieferfirma"       : lieferfirma,
            "lieferstrasse"     : lieferstrasse,
            "lieferplz"         : lieferplz,
            "lieferort"         : lieferort,
            "lieferland"        : lieferland
            }
          '''
          '''
          db.update(
          table   = "TestTable",
          data    = data,
          where   = ("id",1),
          limit   = 1 )
          '''

          print "Datensatz %s wird gepeichert <br />\n" % id




        if showtime == "Löschen":
          print "Datensatz %s wird geloescht <br />\n" % id

        print '</div>\n'

        self.edit(id)



'''
 $sql = "
  INSERT INTO ".$db_prefix."hopek_todo_data
  ( `username` , 
    `projektname` , 
    `titel` , 
    `beschreibung`,
    `status`,
    `dringlichkeit`,
    `aenderung` ) 
  VALUES 
  ( '$username', 
    '$projektname', 
    '$titel', 
    '$beschreibung' ,
    '$status',
    '$dringlichkeit',
    '".datum2db(strftime("%d.%m.%Y"))."' );";
'''