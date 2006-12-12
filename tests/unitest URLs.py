#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Unitest für \PyLucid\system\URLs.py


Last commit info:
----------------------------------
$LastChangedDate:$
$Rev:$
$Author$

Created by Jens Diemer

license:
    GNU General Public License v2 or above
    http://www.opensource.org/licenses/gpl-license.php

"""

__version__= "$Rev:$"


import sys, unittest


sys.path.insert(0, "../") # PyLucid-Root

from PyLucid.system.URLs import URLs
from PyLucid_app import runlevel





class FakeRequest(object):
    """
    Zum Test wird ein request-Object mit ein paar Eigenschaften benötigt
    """
    runlevel = None
    environ = {}
    preferences = {}
    session = {"page_id": 32}


class FakeResponse(object):
    def write(self, txt):
        print txt
    def page_msg(self, *txt):
        print "".join([str(i) for i in txt])




class testURLs(unittest.TestCase):
    def setUp(self):
        self.fake_requestObj = FakeRequest()
        self.fake_requestObj.runlevel = runlevel()
        self.fake_responseObj = FakeResponse()
        self.fake_requestObj.preferences["commandURLprefix"] = "_command"

    def setURLclass(self):
        self.url = URLs(self.fake_requestObj, self.fake_responseObj)
        self.url.lock = False

        # Es ist kein Module gestartet!
        self.url["command"] = None
        self.url["action"] = None

    #_________________________________________________________________________

    def testURLs_normal1(self):
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "/_command/32/current_command/current_method/",
            "SCRIPT_ROOT": "/",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_normal()
        self.fake_requestObj.runlevel.set_normal()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        self.assertEqual(
            self.url["hostname"],
            'http://domain.tld'
        )
        self.assertEqual(
            self.url["scriptRoot"], '/'
        )

        self.assertRaises(RuntimeError, self.url.currentAction)
        self.assertRaises(RuntimeError, self.url.actionLink, "")

        self.assertEqual(
            self.url.commandLink("modulename", "methodname"),
            "/_command/32/modulename/methodname/"
        )

        self.assertEqual(self.url.pageLink("level1/level2"),   "/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2"),  "/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2/"), "/level1/level2/")


    def testURLs_normal2(self):
        """
        PyLucid liegt in einem Unterverzeichnis
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "DocRoot/Handler.py",
            "SCRIPT_ROOT": "/DocRoot/Handler.py",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_normal()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        self.assertEqual(
            self.url["hostname"],
            'http://domain.tld/DocRoot/Handler.py'
        )
        self.assertEqual(
            self.url["scriptRoot"], '/DocRoot/Handler.py'
        )

        self.assertRaises(RuntimeError, self.url.currentAction)
        self.assertRaises(RuntimeError, self.url.actionLink, "")

        self.assertEqual(
            self.url.commandLink("modulename", "methodname"),
            "/DocRoot/Handler.py/_command/32/modulename/methodname/"
        )

        self.assertEqual(self.url.pageLink("level1/level2"),   "/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2"),  "/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2/"), "/level1/level2/")

    def testURLs_normal2(self):
        """
        PyLucid liegt in einem Unterverzeichnis
        +GET-Parameter
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "DocRoot/Handler.py?GetParam=1&Param2=jau",
            "SCRIPT_ROOT": "/DocRoot/Handler.py",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_normal()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        self.assertEqual(self.url["hostname"], 'http://domain.tld')
        self.assertEqual(
            self.url["scriptRoot"], '/DocRoot/Handler.py'
        )

        self.failUnlessRaises(RuntimeError, self.url.currentAction)
        self.failUnlessRaises(RuntimeError, self.url.actionLink, "")

        self.assertEqual(
            self.url.commandLink("modulename", "methodname"),
            "/DocRoot/Handler.py/_command/32/modulename/methodname/"
        )
        self.assertEqual(self.url.pageLink("level1/level2"),   "/DocRoot/Handler.py/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2"),  "/DocRoot/Handler.py/level1/level2/")
        self.assertEqual(self.url.pageLink("/level1/level2/"), "/DocRoot/Handler.py/level1/level2/")

    #_________________________________________________________________________

    def testURLs_command1(self):
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "/_command/32/current_command/current_method/",
            "SCRIPT_ROOT": "/",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_command()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        # Wird vom Module-Manager festgelegt:
        self.url.lock = False
        self.url["command"] = "current_command"
        self.url["action"] = "current_method"
        self.url.lock = True

        self.assertEqual(self.url["hostname"], 'http://domain.tld')
        self.assertEqual(self.url["scriptRoot"], '/')
        self.assertEqual(self.url["actionArgs"], [])

        self.assertEqual(
            self.url.currentAction(),
            "/_command/32/current_command/current_method/"
        )

        self.assertEqual(
            self.url.actionLink("new_methodname"),
            "/_command/32/current_command/new_methodname/"
        )

        self.assertEqual(
            self.url.commandLink("new_modulename", "new_methodname"),
            "/_command/32/new_modulename/new_methodname/"
        )
        self.assertEqual(
            self.url.pageLink("level1/level2"),   "/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2"),  "/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2/"), "/level1/level2/"
        )


    def testURLs_command2(self):
        """
        command mit GET Parametern in der URL
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": (
                "/_command/32/current_command/current_method/url2args1/url2args2/"
                "?GetParam=1&Param2=jau"
            ),
            "SCRIPT_ROOT": "/DocRoot/Handler.py",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_command()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        # Wird vom Module-Manager festgelegt:
        self.url.lock = False
        self.url["command"] = "current_command"
        self.url["action"] = "current_method"
        self.url.lock = True

        self.assertEqual(self.url["hostname"], 'http://domain.tld')
        self.assertEqual(self.url["scriptRoot"], '/DocRoot/Handler.py')
        self.assertEqual(self.url["actionArgs"], [u'url2args1', u'url2args2'])

        self.assertEqual(
            self.url.currentAction(),
            "/DocRoot/Handler.py/_command/32/current_command/current_method/"
        )

        self.assertEqual(
            self.url.actionLink("new_methodname"),
            "/DocRoot/Handler.py/_command/32/current_command/new_methodname/"
        )

        self.assertEqual(
            self.url.commandLink("new_modulename", "new_methodname"),
            "/DocRoot/Handler.py/_command/32/new_modulename/new_methodname/"
        )
        self.assertEqual(
            self.url.pageLink("level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2/"),
            "/DocRoot/Handler.py/level1/level2/"
        )

    #_________________________________________________________________________

    def testURLs_install1(self):
        """
        command mit GET Parametern in der URL
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "/_install",
            "SCRIPT_ROOT": "/",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_install()
        self.url.setup_runlevel()
        # im _install Bereich wird self.url.setup_page_id() nicht ausgeführt!
        #~ self.url.debug()

        self.assertEqual(self.url["hostname"], 'http://domain.tld')
        self.assertEqual(self.url["scriptRoot"], '/')
        self.assertEqual(self.url.installBaseLink(), '/_install')
        self.assertEqual(self.url["actionArgs"], [])

        self.assertEqual(self.url["command"], None)
        self.assertEqual(self.url["action"], None)

        self.failUnlessRaises(RuntimeError, self.url.currentAction)
        self.failUnlessRaises(RuntimeError, self.url.actionLink, "")

        self.assertEqual(
            self.url.commandLink("new_modulename", "new_methodname"),
            "/_install/new_modulename/new_methodname/"
        )
        self.assertEqual(
            self.url.pageLink("level1/level2"),
            "/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2"),
            "/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2/"),
            "/level1/level2/"
        )

    def testURLs_install2(self):
        """
        command mit GET Parametern in der URL
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": (
                "/_install/current_command/current_method/urlargs1/urlargs2/"
                "?GetParam=1&Param2=jau"
            ),
            "SCRIPT_ROOT": "/DocRoot/Handler.py",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_install()
        self.url.setup_runlevel()
        # im _install Bereich wird self.url.setup_page_id() nicht ausgeführt!
        #~ self.url.debug()

        self.assertEqual(self.url["hostname"], 'http://domain.tld')
        self.assertEqual(self.url["scriptRoot"], '/DocRoot/Handler.py')
        self.assertEqual(
            self.url.installBaseLink(),
            '/DocRoot/Handler.py/_install'
        )
        self.assertEqual(self.url["actionArgs"], [u'urlargs1', u'urlargs2'])

        self.assertEqual(self.url["command"], "current_command")
        self.assertEqual(self.url["action"], "current_method")

        self.assertEqual(
            self.url.currentAction(),
            "/DocRoot/Handler.py/_install/current_command/current_method/"
        )

        self.assertEqual(
            self.url.actionLink("new_methodname"),
            "/DocRoot/Handler.py/_install/current_command/new_methodname/"
        )

        self.assertEqual(
            self.url.commandLink("new_modulename", "new_methodname"),
            "/DocRoot/Handler.py/_install/new_modulename/new_methodname/"
        )
        self.assertEqual(
            self.url.pageLink("level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2/"),
            "/DocRoot/Handler.py/level1/level2/"
        )

    def testURLs_404error(self):
        """
        PyLucid liegt in einem Unterverzeichnis
        """
        self.fake_requestObj.environ = {
            "HTTP_HOST": "domain.tld",
            "PATH_INFO": "/ok1/ok2/wrong1/wrong2",
            "SCRIPT_ROOT": "/DocRoot/Handler.py",
        }
        self.setURLclass()
        self.fake_requestObj.runlevel.set_normal()
        self.url.setup_runlevel()
        self.url.setup_page_id()
        #~ self.url.debug()

        # Wird normalerweise von detect_page aufgerufen:
        self.url.handle404errors(
            correctShortcuts = ["ok1","ok2"],
            wrongShortcuts = ["wrong1", "wrong2"]
        )

        self.assertEqual(
            self.url["hostname"],
            'http://domain.tld'
        )
        self.assertEqual(
            self.url["scriptRoot"],
            '/DocRoot/Handler.py'
        )

        self.assertRaises(RuntimeError, self.url.currentAction)
        self.assertRaises(RuntimeError, self.url.actionLink, "")

        self.assertEqual(
            self.url.commandLink("modulename", "methodname"),
            "/DocRoot/Handler.py/_command/32/modulename/methodname/"
        )

        self.assertEqual(
            self.url.pageLink("level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2"),
            "/DocRoot/Handler.py/level1/level2/"
        )
        self.assertEqual(
            self.url.pageLink("/level1/level2/"),
            "/DocRoot/Handler.py/level1/level2/"
        )







def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testURLs))
    return suite





if __name__ == "__main__":
    print
    print ">>> %s - Unitest"
    print "_"*79
    unittest.main()
    sys.exit()



