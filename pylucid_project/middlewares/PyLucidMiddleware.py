# coding: utf-8

from pylucid.system import pylucid_objects

class PyLucidMiddleware(object):
    def process_request(self, request):
        """ Add PyLucid objects to the request object """
        request.PYLUCID = pylucid_objects.PyLucidRequestObjects(request)
