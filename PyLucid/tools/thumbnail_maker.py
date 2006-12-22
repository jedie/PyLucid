#!/usr/bin/python
# -*- coding: ISO-8859-1 -*-

__author__      = "Jens Diemer"
__url__         = "http://www.jensdiemer.de/index.py/Codesnippets/"
__license__     = "GNU General Public License (GPL)"
__description__ = "makes thumbs with the PIL"

__version__ = "v0.2.1"

__history__ = """
v0.2.1
    - try-except if the file is not a image
v0.2
    - JPEG quality Setting in cfg, now
v0.1
    - Patch für PIL's Fehler "Suspension not allowed here"
"""

import sys, os, time, fnmatch, urllib


try:
    import Image, ImageFont, ImageDraw

    # PIL's Fehler "Suspension not allowed here" work around:
    # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
    import ImageFile
    ImageFile.MAXBLOCK = 1000000 # default is 64k
except ImportError:
    print "Import Error:"
    print "You must install PIL, The Python Image Library"
    print "http://www.pythonware.com/products/pil/index.htm"
    sys.exit()



class thumb_maker_cfg:
    # Standardwerte
    path_to_convert = os.getcwd()
    make_thumbs     = True
    thumb_size      = (160, 120)
    thumb_suffix    = "_thumb"

    make_smaller    = False
    smaller_size    = (640, 480)
    suffix          = "_WEB"
    image_text      = ""

    jpegQuality     = 85

    clean_filenames = True

    rename_rules = [
        (" ", "_"),
        ("ä", "ae"),
        ("ö", "oe"),
        ("ü", "ue"),
        ("Ä", "Ae"),
        ("Ö", "Oe"),
        ("Ü", "Ue"),
        ("ß", "ss"),
    ]


class thumb_maker:
    def __init__( self, cfg ):
        self.cfg = cfg
        self.skip_file_pattern = [
            "*%s.*" % self.cfg.thumb_suffix,
            "*%s.*" % self.cfg.suffix
        ]

    def go( self ):
        """ Aktion starten """
        time_begin = time.time()
        print "work path:", self.cfg.path_to_convert

        for root,dirs,files in os.walk( self.cfg.path_to_convert ):
            print root
            print "_"*80
            for file_name in files:
                abs_file = os.path.join( self.cfg.path_to_convert, root, file_name )

                self.process_file( abs_file )

        print "-"*80
        print "all files converted in %0.2fsec." % (time.time() - time_begin)

    def process_file( self, abs_file ):
        path, im_name   = os.path.split( abs_file )
        print abs_file
        try:
            im_obj = Image.open( abs_file )
        except IOError:
            # Ist wohl kein Bild, oder unbekanntes Format
            #~ print "Not a image, skip.\n"
            return
        except OverflowError, e:
            print ">>> OverflowError: %s" % e
            print "Not a picture ? (...%s)" % abs_file[10:]
            print
            return

        print "%-40s - %4s %12s %s" % (
            im_name, im_obj.format, im_obj.size, im_obj.mode
        )

        if self.cfg.clean_filenames == True:
            # Dateinamen säubern
            im_name = self.clean_filename( im_name )

        # Kleinere Bilder für's Web erstellen
        if self.cfg.make_smaller == True:
            self.convert(
                im_obj      = im_obj,
                im_path     = path,
                im_name     = im_name,
                suffix      = self.cfg.suffix,
                size        = self.cfg.smaller_size,
                text        = self.cfg.image_text,
            )

        # Thumbnails erstellen
        if self.cfg.make_thumbs == True:
            self.convert(
                im_obj      = im_obj,
                im_path     = path,
                im_name     = im_name,
                suffix      = self.cfg.thumb_suffix,
                size        = self.cfg.thumb_size,
            )
        print "-"*3

    def convert( self,
        im_obj, # Das PIL-Image-Objekt
        im_path,# Der Pfad in dem das neue Bild gespeichert werden soll
        im_name,# Der vollständige Name der Source-Datei
        suffix, # Der Anhang für den Namen
        size,   # Die max. größe des Bildes als Tuple
        text="" # Text der unten rechts ins Bild eingeblendet wird
        ):
        """ Rechnet das Bild kleiner und fügt dazu den Text """

        name, ext       = os.path.splitext( im_name )
        out_name        = name + suffix + ".jpg"
        out_abs_name    = os.path.join( im_path, out_name )

        for skip_pattern in self.skip_file_pattern:
            if fnmatch.fnmatch( im_name, skip_pattern ):
                #~ print "Skip file."
                return

        if os.path.isfile( out_abs_name ):
            print "File '%s' exists! Skip." % out_name
            return

        print "resize (max %ix%i)..." % size,
        try:
            im_obj.thumbnail( size, Image.ANTIALIAS )
        except Exception, e:
            print ">>>Error: %s" % e
            return
        else:
            print "OK, real size %ix%i" % im_obj.size

        if im_obj.mode!="RGB":
            print "convert to RGB...",
            im_obj = im_obj.convert("RGB")
            print "OK"

        if text != "":
            font_obj = ImageFont.truetype('arial.ttf', 12) # unter Linux ganzen Pfad angeben!
            ImageDraw.Draw( im_obj ).text( (10, 10), text, font=font_obj, fill=1 )

        print "save '%s'..." % out_name,
        try:
            im_obj.save(
                out_abs_name, "JPEG", quality=self.cfg.jpegQuality,
                optimize=True, progressive=False
            )
        except Exception, e:
            print "ERROR:", e
        else:
            print "OK"

    def clean_filename( self, file_name ):
        """ Dateinamen für's Web säubern """

        if urllib.quote( file_name ) == file_name:
            # Gibt nix zu ersetzten!
            return file_name

        for rule in self.cfg.rename_rules:
            file_name = file_name.replace( rule[0], rule[1] )

        return urllib.quote( file_name )



if __name__ == "__main__":
    thumb_maker_cfg.path_to_convert = r"D:\MyPics"
    thumb_maker_cfg.make_smaller    = True
    #~ thumb_maker_cfg.make_smaller    = False
    thumb_maker_cfg.smaller_size    = (960, 600)
    thumb_maker_cfg.image_text      = "Your image Text :)"

    thumb_maker( thumb_maker_cfg ).go()









