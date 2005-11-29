#!/usr/bin/python
# -*- coding: UTF-8 -*-

__author__  = "Jens Diemer (www.jensdiemer.de)"
__license__ = "GNU General Public License (GPL)"

"""
CVS-pserver-Client

* Only export implemented

pserver Protokoll Beschreibung:
http://www.elegosoft.com/cvs/cvsclient.html
"""

__version__="0.1.1"

__history__="""
v0.1.1
    - rudimentärer Umbau als PyLucid-Plugin
v0.1.0
    - erste Version, export Funktioniert.
"""

#~ import cgitb;cgitb.enable()
import os, sys, time, socket
import tempfile, zipfile, zlib

zlib.Z_DEFAULT_COMPRESSION = 9





class CVS:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        #~ "debug" : True,
        "debug" : False,

        "lucidFunction" : {
            "must_login"    : False,
            "must_admin"    : False,
            "direct_out"    : True,
        }
    }

    #_______________________________________________________________________

    def __init__(self, PyLucid):
        pass

    def lucidFunction( self, connect_info ):
        host, repos_path, module_name = connect_info.split(":")

        #~ print "Content-type: text/html; charset=utf-8\r\n"
        #~ return host, repos_path, module_name

        cvs = pserver(blocklen=1024)
        cvs.connect(host, port=2401, timeout=15)
        cvs.auth_anonymous(repos_path)

        cvs.download_ziped_export(
            module_name,
            directory   = repos_path,
            filename    = module_name
        )

        cvs.close()















class pserver:
    def __init__(self, blocklen=1024, debug=False):
        self.blocklen   = blocklen
        self.debug      = debug

    def connect(self, host, port, timeout=30):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        try:
            self.sock.settimeout(timeout)
        except AttributeError:
            # Geht erst ab Python 2.3 :(
            pass

        #~ print self.sock.getpeername()

    def auth_anonymous(self, repos_path):
        self.send_command("BEGIN AUTH REQUEST")
        self.send_command("%s" % repos_path) # Repository Path
        self.send_command("anonymous")       # Username
        self.send_command("A")               # Password
        self.send_command("END AUTH REQUEST")
        result = self.recv_lines()
        if result[0] != "I LOVE YOU":
            # "login" nicht erfolgreich
            msg = "<h2>Error:</h2>"
            msg += "-"*80
            msg += "\n".join(result)
            msg += "-"*80
            self.error( msg )

    def print_valid_requests(self):
        result = self.process("valid-requests")[0]
        result = result.split()
        print "\n".join(result)

    def send_command(self, command):
        if self.debug: print "send '%s'..." % command,
        self.sock.send("%s\n" % command)
        if self.debug: print "OK"

    def recv_lines(self, buffer=1024):
        result = self.sock.recv(1024)
        return result.splitlines()

    #~ def process(self, command, buffer=1024):
        #~ self.send_command(command)
        #~ return self.recv_lines(buffer)

    def close(self):
        self.sock.close()

    def error(self, msg):
        print "Content-type: text/html; charset=utf-8\r\n"
        print "<pre>%s</pre>" % msg
        sys.exit()

    #__________________________________________________________________
    # Hight-level methods

    #~ def history( self, module_name, directory ):
        #~ self.root_dir = directory
        #~ self.send_command("Root %s" % self.root_dir)
        #~ self.send_command("Argument -r")
        #~ self.send_command("Argument HEAD")
        #~ self.send_command("Argument %s" % module_name)
        #~ self.send_command("Directory .")
        #~ self.send_command(directory)
        #~ self.send_command("history")
        #~ self.send_command("log")
        #~ while 1:
            #~ new_data = self.sock.recv(self.blocklen)
            #~ print new_data

    def download_ziped_export(self, module_name, directory, filename):
        zip_fileobj = self.export(module_name, directory)
        zip_content = zip_fileobj.read()

        print 'Content-Length:  %s' % len( zip_content )
        print 'Content-Disposition: attachment; filename=%s_%s.zip' % (time.strftime("%Y%m%d"), filename)
        print 'Content-Transfer-Encoding: binary'
        print 'Content-Type: application/octet-stream; charset=utf-8\n'

        sys.stdout.write( zip_content )

        sys.exit()

    def export(self, module_name, directory):
        self.root_dir = directory
        self.send_command("UseUnchanged")
        self.send_command("Root %s" % self.root_dir)
        #~ self.send_command("Global_option -q")
        #~ self.send_command("Argument %s" % module_name)
        #~ self.send_command("Directory .")
        #~ self.send_command(directory)
        #~ self.send_command("expand-modules")
        #~ print "export: ", self.recv_lines()
        #~ print

        self.send_command("Argument -N")
        self.send_command("Argument -r")
        self.send_command("Argument HEAD")
        self.send_command("Argument %s" % module_name)
        self.send_command("Directory .")
        self.send_command(directory)
        self.send_command("export")

        #~ tmp_fileobj, tmp_filename = tempfile.mkstemp()
        tmp_fileobj = tempfile.TemporaryFile()
        outfile = zipfile.ZipFile( tmp_fileobj, "w", zipfile.ZIP_DEFLATED)
        self.get_files(module_name, outfile)
        outfile.close()

        tmp_fileobj.seek(0)

        #~ f = file( r"d:\temp\test.zip", "wb")
        #~ f.write( tmp_fileobj.read() )
        #~ f.close()

        return tmp_fileobj


    def get_files(self, module_name, outfile):
        block = ""
        while 1:
            new_data = self.sock.recv(self.blocklen)
            block += new_data

            while 1:
                try:
                    current, block = block.split("\n",1)
                except ValueError:
                    break

                if current[:4] == "M U ": # Dateinamen
                    file_name = current[4:]
                    continue

                if current[:2] == "E ": # neues Verzeichnis
                    continue

                if current.endswith("THEAD"): # Datei-Versionsnummer
                    #~ print current
                    continue

                if current.startswith( "u=" ): # Dateirechte
                    continue

                if current.startswith( "Updated" ):
                    # Verzeichnis, relativ
                    continue

                if current.startswith( self.root_dir ):
                    # absoluter CVS-Pfad der Datei
                    continue

                try:
                    # Der Header wird abgeschlossen mit das Angabe
                    # der Dateigröße, danach folgt der Dateiinhalt
                    file_len = int( current )
                    #~ print ">file_len:", file_len
                except:
                    # Die eigentlichen Daten kommen noch nicht
                    # Wir sind noch im Header
                    #~ print "\t",current
                    continue

                readed_bytes = len(block)
                rest_bytes = file_len - readed_bytes

                if rest_bytes<0:
                    # Alle Daten zur Datei sind schon im aktuellen Block
                    self.write_file( file_name, outfile, block[:rest_bytes], file_len )
                    # Restlichen Bytes für den nächsten Durchlauf aufbewahren
                    block = block[rest_bytes:]
                    break

                current_blocklen = self.blocklen
                while 1:
                    # Restlichen Bytes in Blöcke einlesen
                    if rest_bytes<current_blocklen:
                        # Letzter Block ist kleiner als die normale Blockgröße
                        current_blocklen = rest_bytes

                    new_data = self.sock.recv(current_blocklen)
                    current_bytes = len(new_data)

                    readed_bytes    += current_bytes
                    rest_bytes      -= current_bytes

                    block += new_data

                    if rest_bytes<=0:
                        # Alle Daten gelesen
                        break

                self.write_file(file_name, outfile, block, file_len)
                block = ""
                break

            if new_data == "ok\n":
                # Alle Dateien wurden empfangen
                return

    def write_file( self, file_name, outfile, content, file_len ):
        content_len = len(content)
        #~ print file_name, content_len
        #~ return

        if content_len != file_len:
            self.error(
                "+++ Error '%s' +++\ncontent_len != file_len: %s != %s" % (
                    file_name, content_len, file_len
                )
            )

        #~ print "write '%s' %s Bytes..." % (file_name, content_len),
        outfile.writestr(file_name, content)
        #~ print "OK"




#~ print tempfile.gettempdir()
#~ print tempfile.gettempprefix()

#~ sys.exit()




if __name__ == "__main__":
    #~ host        = "cvs.sourceforge.net"
    #~ repos_path  = "/cvsroot/pylucid"
    #~ timeout=30

    host        = "192.168.6.2"
    repos_path  = "/daten/cvsroot"
    timeout=1

    port = 2401

    cvs = pserver(blocklen=1024)#, debug=True)
    cvs.connect(host, port, timeout)
    cvs.auth_anonymous(repos_path)

    #~ print cvs.print_valid_requests()

    #~ cvs.history(
        #~ module_name = "PyLucid_tarball",
        #~ directory   = repos_path,
    #~ )

    cvs.download_ziped_export(
        module_name = "PyLucid_tarball",
        directory   = repos_path,
        filename = r"cvstest.zip"
    )

    cvs.close()





