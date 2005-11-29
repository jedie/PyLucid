
import sys, time
from PyLucid_simpleTAL import simpleTAL, simpleTALES

class simpletal_test:

    def __init__(self, PyLucid):
        pass

    def lucidTag(self):
        start_time = time.time()
        template = """
        <table>
        <tr tal:repeat="data example"
        tal:attributes="class string:color${'repeat/data/odd'}">
            <td tal:content="repeat/data/number"></td>
            <td tal:content="data/char"></td>
        </tr>
        </table>
        <style type="text/css">
            .color0 {background-color:#EEEEEE;}
            .color1 {background-color:#DDDDDD;}
        </style>
        """
        data = [{"char":chr(i)} for i in range(65, 91)]

        context = simpleTALES.Context()
        context.addGlobal("example", data)

        template = simpleTAL.compileHTMLTemplate(template)
        template.expand(context, sys.stdout)

        print "time:", time.time()-start_time


if __name__=="__main__":
    simpletal_test("").lucidTag()