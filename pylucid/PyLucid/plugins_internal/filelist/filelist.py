#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
    PyLucid media file manager
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    TODO:
        * 
        * 

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev:  $
    $Author: $

    :copyright: 
    :license: GNU GPL v2 or above, see LICENSE for more details
"""

__version__= ""

import time, cgi
import os,sys,datetime,stat
from time import gmtime, strftime,time,localtime,strftime

from django import newforms as forms
from django.utils.translation import ugettext as _

from PyLucid import settings
from PyLucid.models import Page
from PyLucid.system.BasePlugin import PyLucidBasePlugin


ABSPATH = os.path.abspath(settings.MEDIA_ROOT)

def _action( dir_string, file, action, dest='' ):
    """
    Diferent actions over file or dir
    """
    filerel=os.path.normpath( os.path.join(dir_string, file) )
    file=os.path.abspath(os.path.join(settings.MEDIA_ROOT, filerel ))

    if file.find( settings.MEDIA_ROOT )<0:
        WrongDirectory(file)

    if action=='del':
        os.remove( file )
        return os.path.normpath( dir_string )
    if action=='deldir':
        os.rmdir( file )
        return os.path.normpath( os.path.join(filerel, './../') )
    if action=='rename':
        os.rename( file, dest )
        return filerel
    elif action=='mdir':
        if file[0]!='.':
            os.mkdir(file)
            return os.path.normpath( dir_string )





def getFilesList( dire ):
    """
    Returns all file in dir dire
     'relative' to url root
     
     

...

    #convert to disk path
    dire=os.path.abspath(os.path.join(settings.MEDIA_ROOT, dire ))
    if not dire.startswith(ABSPATH):
        raise WrongDirectory( dire ) 
     
    """
    listFile=[]
    listDir=[]

    #convert to disk path
    dire=os.path.abspath(os.path.join(settings.MEDIA_ROOT, dire ))

    if not dire.startswith( ABSPATH ):
        raise WrongDirectory( dire )
        #return listDir,listFile


    for f in os.listdir(dire):
        try:
            #dont allow hidden files or dir
            if f[0]=='.':
                continue
            pathname = os.path.join(dire, f)
            statinfo = os.stat(pathname)
            mode = statinfo[stat.ST_MODE]
            accestime = statinfo[stat.ST_ATIME]
            sizeK=statinfo[stat.ST_SIZE]/1024


            theFileDir={'name':f ,'time':strftime('%Y:%m:%M',localtime(statinfo[stat.ST_MTIME]))  ,'size':sizeK ,'statinfo': statinfo };
            if stat.S_ISDIR(mode):
                listDir.append( theFileDir )
            else:
                listFile.append( theFileDir )
        except:
            theFile={'name':f+"_error" ,'statinfo': '' };
            listFile.append( theFile )

    return listDir,listFile



class filelist(PyLucidBasePlugin):


    def splitdirlist( self, path ):
        """
        path: /data/one/two

        return [('/data/one/two','two'), ('/data/one','one'),('/data','data')  ]
        """
        self.page_msg.green("splitdirlist "+path)
        dirlist=[]
        tup=os.path.split( path )

        while tup[0]!='':
            if tup[1]!='' and  tup[1]!='.':
                self.page_msg.green(tup[1]+" <p /> ")
                dirlist.append( self.createdirtuple( tup[1], tup[0]))
            if tup[0]=='/':
                break
            tup=os.path.split(tup[0])
        if tup[1]!='' and  tup[1]!='.':
            self.page_msg.green("splitdirlist 2 "+tup[1])
            dirlist.append( self.createdirtuple( tup[1], tup[0]) )

        self.page_msg.green("splitdirlist 3 "+str(dirlist))	
        dirlist.reverse()
        return dirlist #.reverse()


    def createdirtuple(self, dirfinal, allpath ):
        """
        Creates a tuble ( dirname, hispath)
        """
        return ( dirfinal, os.path.join(allpath,dirfinal))



    def lucidTag(self, rest=''):
        """
        List dir and file. Some actions.
        rest: path to dir or file
        """
        # Change the global page title:
        self.context["PAGE"].title = _("File list")
        direc=settings.MEDIA_ROOT
        context = {}
        dir_list=[]
        files_list=[]   

        dir_string=''

        if rest!='':
            dir_string=os.path.normpath( rest )


        if self.request.method == 'POST' and self.request.has_key('action'):

            dir_string=os.path.normpath( self.request['dir_string'] )
            file=os.path.normpath( self.request['file_string'] )

            newdir=_action( dir_string, file, self.request['action'] )

            dir_list,files_list=getFilesList(newdir)
            dir_string=newdir

        elif self.request.method == 'POST' and self.request.FILES.has_key('ufile'):
            """
            uploading a file
            """
            file=self.request.FILES['ufile']
            dir_string= os.path.normpath( self.request['dir_string'] )
            name=os.path.normpath( file['filename'] )
            pathFile=os.path.abspath( os.path.join(settings.MEDIA_ROOT ,os.path.join(dir_string, name)) )

            fileLike=open(pathFile,'w' ) #if it exists, overwrite
            fileLike.write( file['content'] )
            fileLike.close()

            dir_list,files_list=getFilesList(dir_string)

        else:
        #dir change
            dir_list,files_list = getFilesList(dir_string )


        updir=0
        if dir_string!='' and dir_string!='.':
            updir=1
        deldir=0
        if len(dir_list)==0 and len(files_list)==0:
            deldir=1

        dirlist=self.splitdirlist( dir_string )
        self.page_msg.green("splitdirlist 4 "+rest)
        context = {
            "url": self.URLs.methodLink("lucidTag"),
            "dir": dir_string,
            "dirlist":dirlist,
            "files_list": files_list,
            "dir_list":dir_list,
            "media_url":settings.MEDIA_URL,
            "updir": updir,
            "deldir":deldir,
	    "messages":self.page_msg,
        }

        self._render_template("file_form", context)




class WrongDirectory(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)





