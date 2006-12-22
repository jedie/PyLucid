#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author: jensdiemer $

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php
"""

import sys, os, time, fnmatch, urllib


from PyLucid.system.BaseModule import PyLucidBaseModule


debug = True
#~ debug = False



class ThumbnailMaker(PyLucidBaseModule):
    cfg = {
        ## Thumnails
        "thumb_size": (160, 120),
        "thumb_suffix": "_thumb",

        ## Kleinere Version
        "smaller_size": (640, 480),
        "smaller_suffix": "_WEB",

        # Text der eingeblendet werden soll (Nur in der kleinen Version)
        "image_text": None,

        "jpegQuality": 85,
    }

    def __init__(self, *args, **kwargs):
        super(ThumbnailMaker, self).__init__(*args, **kwargs)

        try:
            import Image, ImageFont, ImageDraw

            # PIL's Fehler "Suspension not allowed here" work around:
            # s. http://mail.python.org/pipermail/image-sig/1999-August/000816.html
            import ImageFile
            ImageFile.MAXBLOCK = 1000000 # default is 64k
        except ImportError, e:
            raise PIL_ImportError("Can't Import the Python Image Library: %s" % e)

        #~ self.skip_file_pattern = [
            #~ "*%s.*" % self.cfg.thumb_suffix,
            #~ "*%s.*" % self.cfg.suffix
        #~ ]

    #~ def make_thumbs(self, path):
        #~ """
        #~ Erstell Thumbnails von allen Bildern im Pfad.
        #~ - Läßt existierende Thumbnails aus (thumb_suffix im Dateinamen)
        #~ """
        #~ time_begin = time.time()

        #~ for root,dirs,files in os.walk(path):
            #~ print root
            #~ print "_"*80
            #~ for file_name in files:
                #~ abs_file = os.path.join( self.cfg.path_to_convert, root, file_name )

                #~ self.process_file( abs_file )

        #~ print "-"*80
        #~ print "all files converted in %0.2fsec." % (time.time() - time_begin)

    def process_file(self, abs_file, out_path, \
                                            make_thumb=True, make_small=False):
        """
        Ein Bild verabreiten

        - abs_file  : Absoluter Pfad zu Source Datei
        - out_path  : Ouputpfad für die generierten Bilder
        - make_thumb: True/False -> Soll Thumbnail erstellt werden?
        - make_small: True/False -> Soll kleinere Version erstellt werden?
        """
        path, im_name = os.path.split(abs_file)
        try:
            im_obj = Image.open(abs_file)
        except IOError, e: # Ist wohl kein Bild, oder unbekanntes Format
            raise UnknownFormat(e)
        except OverflowError, e:
            raise UnknownFormat("OverflowError: %s" % e)

        if debug:
            msg = "%-40s - %4s %12s %s" % (
                im_name, im_obj.format, im_obj.size, im_obj.mode
            )
            self.page_msg(msg)

        raise "To Be Continued!"

        if small_name != None
            # Kleinere Bilder für's Web erstellen
            self.convert(
                im_obj      = im_obj,
                im_path     = path,
                im_name     = im_name,
                out_path    = small_name,
                suffix      = self.cfg["smaller_suffix"],
                size        = self.cfg["smaller_size"],
                text        = self.cfg["image_text"],
            )

        if thumb_name != None
            # Thumbnails erstellen
            self.convert(
                im_obj      = im_obj,
                im_path     = path,
                im_name     = im_name,
                out_path    = thumb_name,
                suffix      = self.cfg["thumb_suffix"],
                size        = self.cfg["thumb_size"],
            )

    def convert(self,
        im_obj,     # Das PIL-Image-Objekt
        im_path,    # Der Pfad in dem das neue Bild gespeichert werden soll
        im_name,    # Der vollständige Name der Source-Datei
        out_path,   # Absoluter Pfad für den Output
        suffix,     # Der Anhang für den Namen
        size,       # Die max. größe des Bildes als Tuple
        text=""     # Text der unten rechts ins Bild eingeblendet wird
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



class PIL_ImportError(Exception):
    """ PIL kann nicht importiert werden """
    pass

class UnknownFormat(Exception):
    """ Das Sourcebild kann nicht geöffnet werden """
    pass







