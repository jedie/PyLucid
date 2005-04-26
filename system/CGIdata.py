#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os

import sessiondata

def put_in_sessiondata():
    """
    sammelt POST und GET Daten zusammen

    Ein dict wird gespeichert in
        sessiondata.cgi.data
    """
    if os.environ.has_key('QUERY_STRING'):
        # GET URL-Parameter parsen
        for i in os.environ['QUERY_STRING'].split("&"):
            i=i.split("=")
            if len(i)==1:
                if i[0]!="":
                    sessiondata.cgi.data[ i[0] ] = ""
            else:
                sessiondata.cgi.data[ i[0] ] = i[1]

    from cgi import FieldStorage
    FieldStorageData = FieldStorage()
    # POST Daten auswerten
    for i in FieldStorageData.keys():
        sessiondata.cgi.data[i]=FieldStorageData.getvalue(i)

if __name__ == "__main__":
    get()


