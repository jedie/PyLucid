
import sys, time


class cheetah_test:

    #_______________________________________________________________________
    # Module-Manager Daten

    module_manager_data = {
        "lucidTag" : {
            "must_login"    : False,
            "must_admin"    : False,
        }
    }

    def __init__(self, PyLucid):
        pass

    def lucidTag(self):

        daten = []
        for i in xrange(100):
            daten.append(
                {"surname":"n%s" % i,
                "firstname":"fn%s" % i,
                "email":"j%s@eifh.com" % i}
            )

        start_time = time.time()
        from Cheetah.Template import Template
        print "import:", time.time()-start_time

        template = """<h2>$title</h2>
        <p>$contents</p>
        <TABLE>
        #for $client in $service
        <TR>
        <TD>$client.surname, $client.firstname</TD>
        <TD><A HREF="mailto:$client.email" >$client.email</A></TD>
        </TR>
        #end for
        </TABLE>
        """
        nameSpace = {
            'title': 'Hello World Example', 'contents': 'Hello World!',
            "service": daten
        }

        start_time = time.time()
        print Template(template, searchList=[nameSpace])
        print time.time()-start_time


if __name__=="__main__":
    simpletal_test("").lucidTag()