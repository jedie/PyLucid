
import sys
import simpleTAL, simpleTALES

template = """
<div tal:repeat="data example" tal:omit-tag="">
<span tal:define="no data/no" tal:condition="python:no != 67">
    <p tal:content="python:str(no)"></p>
    <p tal:content="string:${data/no} - ${data/char}"></p>
</span>
</div>
"""
data = [{"char":chr(i),"no":i} for i in range(65, 70)]

context = simpleTALES.Context(allowPythonPath=1)
context.addGlobal("example", data)

template = simpleTAL.compileHTMLTemplate(template)
template.expand(context, sys.stdout)

print " -"*40

template = """
<div tal:repeat="data example" tal:omit-tag="">
<span tal:condition="python:data['no'] != 67">
    <p tal:content="string:${data/no} - ${data/char}"></p>
</span>
</div>
"""
data = [{"char":chr(i),"no":i} for i in range(65, 70)]

context = simpleTALES.Context(allowPythonPath=1)
context.addGlobal("example", data)

template = simpleTAL.compileHTMLTemplate(template)
template.expand(context, sys.stdout)