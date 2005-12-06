"""
    WSGI Debug Middleware
    ---------------------
    This module tried to implement a cgitb like debug output as WSGI
    middleware.
    Because you can't cover up all error cases using a WSGI Middleware
    this module also provides a function cgi_debug() which you can use
    like the cgitb.enable() function.

    code used in this middleware:
        cgitb code:                 Ka-Ping Yee
        improved cgitb module:      Nir Soffer
        middlware:                  Armin Ronacher
"""

from __future__ import generators
import sys
import os
import pydoc
import inspect
import linecache
import tokenize
import keyword
import traceback


__UNDEF__ = [] # a special sentinel object

class HTMLFormatter:
    """ Minimal html formatter """
    
    def attributes(self, attributes=None):
        if attributes:
            result = [' %s="%s"' % (k, v) for k, v in attributes.items()]           
            return ''.join(result)
        return ''
    
    def tag(self, name, text, attributes=None):
        return '<%s%s>%s</%s>\n' % (name, self.attributes(attributes), 
                                    text, name)
    
    def section(self, text, attributes=None):
        return self.tag('div', text, attributes)

    def title(self, text, attributes=None):
        return self.tag('h1', text, attributes)

    def subTitle(self, text, attributes=None):
        return self.tag('h2', text, attributes)

    def subSubTitle(self, text, attributes=None):
        return self.tag('h3', text, attributes)

    def paragraph(self, text, attributes=None):
        return self.tag('p', text, attributes)

    def list(self, items, attributes=None):
        return self.formatList('ul', items, attributes)

    def orderedList(self, items, attributes=None):
        return self.formatList('ol', items, attributes)

    def formatList(self, name, items, attributes=None):
        """ Send list of raw texts or formatted items. """
        if isinstance(items, (list, tuple)):
            items = '\n' + ''.join([self.listItem(i) for i in items])
        return self.tag(name, items, attributes)
    
    def listItem(self, text, attributes=None):
        return self.tag('li', text, attributes)        

    def link(self, href, text, attributes=None):
        if attributes is None:
            attributes = {}
        attributes['href'] = href
        return self.tag('a', text, attributes)

    def strong(self, text, attributes=None):
        return self.tag('strong', text, attributes)        

    def em(self, text, attributes=None):
        return self.tag('em', text, attributes)        

    def repr(self, object):
        return pydoc.html.repr(object)
        

class TextFormatter:
    """ Plain text formatter """

    def section(self, text, attributes=None):
        return text

    def title(self, text, attributes=None):
        lineBellow = '=' * len(text)
        return '%s\n%s\n\n' % (text, lineBellow)

    def subTitle(self, text, attributes=None):
        lineBellow = '-' * len(text)
        return '%s\n%s\n\n' % (text, lineBellow)

    def subSubTitle(self, text, attributes=None):
        lineBellow = '~' * len(text)
        return '%s\n%s\n\n' % (text, lineBellow)

    def paragraph(self, text, attributes=None):
        return text + '\n\n'

    def list(self, items, attributes=None):
        if isinstance(items, (list, tuple)):
            items = [' * %s\n' % i for i in items]
            return ''.join(items) + '\n'
        return items

    def orderedList(self, items, attributes=None):
        if isinstance(items, (list, tuple)):
            items = [' * %s\n' % i for i in items]
            return ''.join(items) + '\n'
        return items

    def listItem(self, text, attributes=None):
        return ' * %s\n' % text       

    def link(self, href, text, attributes=None):
        return '[[%s]]' % text

    def strong(self, text, attributes=None):
        return text
   
    def em(self, text, attributes=None):
        return text
   
    def repr(self, object):
        return repr(object)
        

class Frame:
    """ Analyze and format single frame in a traceback """

    def __init__(self, frame, file, lnum, func, lines, index):
        self.frame = frame
        self.file = file
        self.lnum = lnum
        self.func = func
        self.lines = lines
        self.index = index

    def format(self, formatter):
        """ Return formatted content """
        self.formatter = formatter
        vars, highlight = self.scan()
        items = [self.formatCall(),
                 self.formatContext(highlight),
                 self.formatVariables(vars)]
        return ''.join(items)

    # -----------------------------------------------------------------
    # Private - formatting
        
    def formatCall(self):
        call = '%s in %s' % (self.formatFile(),
                               self.formatter.strong(self.func),
                               )
        return ''.join([
            self.formatter.paragraph(call, {'class': 'call'}),
            self.formatter.paragraph(self.formatArguments(), {'class': 'args'})
        ])
    
    def formatFile(self):
        """ Return formatted file link """
        if not self.file:
            return '__main__'
        file = pydoc.html.escape(os.path.abspath(self.file))
        return file       

    def formatArguments(self):
        """ Return formated arguments list """
        if self.func == '?':
            return ''

        def formatValue(value):
            return ' = ' + self.formatter.repr(value)

        args, varargs, varkw, locals = inspect.getargvalues(self.frame)
        return inspect.formatargvalues(args, varargs, varkw, locals,
                                       formatvalue=formatValue)

    def formatContext(self, highlight):
        """ Return formatted context, next call highlighted """
        if self.index is None:
            return ''
        context = []
        i = self.lnum - self.index
        for line in self.lines:
            line = '<span class="linenumber">%6d  </span>%s' % (i, pydoc.html.escape(line))
            attributes = {}
            if i in highlight:
                attributes = {'class': 'highlight'}
            context.append(self.formatter.listItem(line, attributes))
            i += 1
        context = '\n' + ''.join(context) + '\n'
        return self.formatter.orderedList(context, {'class': 'context'})

    def formatVariables(self, vars):
        """ Return formatted variables """ 
        done = {}
        dump = []
        for name, where, value in vars:
            if name in done: 
                continue
            done[name] = 1
            if value is __UNDEF__:
                dump.append('%s %s' % (name, self.formatter.em('undefined')))
            else:
                dump.append(self.formatNameValue(name, where, value))
        return self.formatter.list(dump, {'class': 'variables'})

    def formatNameValue(self, name, where, value):
        """ Format variable name and value according to scope """
        if where in ['global', 'builtin']:
            name = '%s %s' % (self.formatter.em(where),
                              self.formatter.strong(name))
        elif where == 'local':
            name = self.formatter.strong(name)
        else:
            name = where + self.formatter.strong(name.split('.')[-1])
        return '%s = %s' % (name, self.formatter.repr(value))

    # ---------------------------------------------------------------
    # Private - analyzing code

    def scan(self):
        """ Scan frame for vars while setting highlight line """
        highlight = {}
        
        def reader(lnum=[self.lnum]):
            highlight[lnum[0]] = 1
            try: 
                return linecache.getline(self.file, lnum[0])
            finally: 
                lnum[0] += 1

        vars = self.scanVariables(reader)
        return vars, highlight

    def scanVariables(self, reader):
        """ Lookup variables in one logical Python line """
        vars, lasttoken, parent, prefix, value = [], None, None, '', __UNDEF__
        for ttype, token, start, end, line in tokenize.generate_tokens(reader):
            if ttype == tokenize.NEWLINE: 
                break
            if ttype == tokenize.NAME and token not in keyword.kwlist:
                if lasttoken == '.':
                    if parent is not __UNDEF__:
                        value = getattr(parent, token, __UNDEF__)
                        vars.append((prefix + token, prefix, value))
                else:
                    where, value = self.lookup(token)
                    vars.append((token, where, value))
            elif token == '.':
                prefix += lasttoken + '.'
                parent = value
            else:
                parent, prefix = None, ''
            lasttoken = token
        return vars

    def lookup(self, name):
        """ Return the scope and the value of name """
        scope = None
        value = __UNDEF__
        locals = inspect.getargvalues(self.frame)[3]
        if name in locals:
            scope, value = 'local', locals[name]
        elif name in self.frame.f_globals:
            scope, value = 'global', self.frame.f_globals[name]
        elif '__builtins__' in self.frame.f_globals:
            scope = 'builtin'
            builtins = self.frame.f_globals['__builtins__']
            if isinstance(builtins, dict):
                value = builtins.get(name, __UNDEF__)
            else:
                value = getattr(builtins, name, __UNDEF__)
        return scope, value


class View:
    """ Traceback view """
    
    frameClass = Frame # analyze and format a frame
    
    def __init__(self, info=None, debug=0):
        """ Save starting info or current exception info """
        self.info = info or sys.exc_info()
        self.debug = debug
        
    def format(self, formatter, context=5):
        self.formatter = formatter
        self.context = context
        return ''.join([
            self.reset(),
            formatter.section(self.formatContent(), {'class': 'cgitb'})
        ])

    def formatContent(self):
        """ General layout - override to change layout """
        return ''.join((
            self.script(),
            self.formatStylesheet(),
            self.formatTitle(),
            self.formatMessage(),
            self.formatButtons(),
            self.formatDebugInfo(),
            self.formatTextTraceback()
        ))

    # -----------------------------------------------------------------
    # Reset Headers
    
    def reset(self):
        return '''<!--: spam
Content-Type: text/html

<div style="display: none">--></div>'''

    # -----------------------------------------------------------------
    # Script
    
    def script(self):
        return '''
<script type="text/javascript">
function toggleDebugInfo() {
    var tb = document.getElementById('cgitb-debug-output');
    if (tb != null) {
        if (tb.style.display == "none") {
            tb.style.display = "block";
        }
        else {
            tb.style.display = "none";
        }
    }
}
</script>
'''

    # -----------------------------------------------------------------
    # Hide debug info
    
    def debugInfoHideScript(self):
        """ Hide debug info for javascript enabled browsers """
        if not self.debug:
            return '<script type="text/javascript">toggleDebugInfo()</script>'
        return ''

    # -----------------------------------------------------------------
    # Buttons
    def formatButtons(self):
        return self.formatter.paragraph(self.formatter.link('javascript:toggleDebugInfo()', 'toggle Debug Info'))

    # -----------------------------------------------------------------
    # Stylesheet

    def formatStylesheet(self):
        """ Format inline html stylesheet """
        return '<style type="text/css">%s</style>' % self.stylesheet()

    def stylesheet(self):
        """ return stylesheet """
        return """
.cgitb {
    font-family: 'Verdana', sans-serif;
    font-size: 14px;
    background-color: #fafafa;
    border: 1px solid #163d68;
    margin: 32px;
}
.cgitb hr {
    border: none!important;
    height: 1px!important;
    line-height: 1px!important;
    background-color: #163d68;
}
.cgitb a {
    color: black;
}
.cgitb a:hover {
    color: #333;
}
.cgitb p {
    margin: 0;
    padding: 10px 20px 10px 20px;
    text-align: left;
}
.cgitb pre {
    margin: 0;
    padding: 5px 20px 5px 20px;
    font-family: monospace;
    font-size: 13px;
    background-color: #eee;
    border-top: 1px solid #bbb;
    border-bottom: 1px solid #bbb;
}
.cgitb ol {
    margin: 0;
    padding: 0;
}
.cgitb li {
    margin: 0;
    padding: 0;
}
.cgitb h1, .cgitb h2, .cgitb h3 {
    font-family: 'Trebuchet MS', sans-serif;
    padding: 5px 10px; 
    margin: 0; 
    background-color: #163d68; 
    color: white;
}
.cgitb h1 {
    font-size: 26px;
}
.cgitb h2 {
    font-size: 22px; 
}
.cgitb h3 {
    font-size: 18px;
}
.cgitb .frames {
    margin: 0; 
    padding: 0; 
    color: #666;
}
.cgitb .frames li {
    display: block;
}
.cgitb .frames p.args {
    font-size: 13px;
    font-family: monospace;
    color: #777;
}
.cgitb .call {
    padding: 5px 10px;
    background-color: #4470a2;
    color: white;
}
.cgitb .context {
    padding: 12px 0 12px 0;
    font-family: monospace;
    font-size: 13px;
    background-color: #eee;
    border-top: 1px solid #bbb;
    border-bottom: 1px solid #bbb;
}
.cgitb .context li {
    margin: 3px 0 3px 0;
    padding: 0;
    display: block;
    white-space: pre;
}
.cgitb .context li .linenumber {
    color: #777;
    font-weight: bold;
}
.cgitb .context li.highlight {
    background-color: #7d9aba;
    color: white;
    border-top: 1px solid #163d68;
    border-bottom: 1px solid #163d68;
}
.cgitb .context li.highlight .linenumber {
    color: white;
}
.cgitb .variables {
    padding: 10px 20px 10px 20px;
    font-family: monospace;
    color: black;
}
.cgitb .exception {
    border: 1px solid #163d68;
    margin: 10px;
}
.cgitb .exception h3 {
    background-color: #163d68;
    color: white;
}
.cgitb .exception p {
    color: black;
}
.cgitb .exception ul {
    margin: 0;
    padding: 0 20px 10px 20px;
    font-family: monospace;
    font-size: 13px;
}
.cgitb .exception li {
    padding: 0;
    margin: 0;
    display: block;
}
"""

    # -----------------------------------------------------------------
    # Head
    
    def formatTitle(self):
        return self.formatter.title(self.exceptionTitle(self.info))
        
    def formatMessage(self):
        return self.formatter.paragraph(self.exceptionMessage(self.info))
        
    
    # -----------------------------------------------------------------
    # Debug Info
        
    def formatDebugInfo(self):
        """ Put debugging information in a hidden div and sourround
        by a html tag"""
        attributes = {'id': "cgitb-debug-output"}
        info = [self.debugInfoHideScript(),
                self.formatTraceback(),
                self.formatSystemDetails(),]
        return self.formatter.section(''.join(info), attributes)
        
    # -----------------------------------------------------------------
    # Traceback

    def formatTraceback(self):
        return self.formatAllTracebacks(self.formatOneTraceback)
    
    def formatAllTracebacks(self, formatFuction):
        """ Format multiple tracebacks using formatFunction """
        tracebacks = []
        for type, value, tb in self.exceptions():
            if type is None: 
                break
            tracebacks.append(formatFuction((type, value, tb)))
            del tb
        return ''.join(tracebacks)
      
    def formatOneTraceback(self, info):
        """ Format one traceback
        
        Separate to enable formatting multiple tracebacks.
        """
        output = [self.formatter.subTitle('Traceback'),
                  self.formatter.paragraph(self.tracebackText(info)),
                  self.formatter.orderedList(self.tracebackFrames(info),
                                            {'class': 'frames'}),
                  self.formatter.section(self.formatException(info),
                                         {'class': 'exception'}),]
        return self.formatter.section(''.join(output), {'class': 'traceback'})

    def tracebackFrames(self, info):
        frames = []
        traceback = info[2]
        for record in inspect.getinnerframes(traceback, self.context):
            frame = self.frameClass(*record)
            frames.append(frame.format(self.formatter))
        del traceback
        return frames

    def tracebackText(self, info):
        return '''A problem occurred in a Python script.  Here is the
        sequence of function calls leading up to the error, in the
        order they occurred.'''

    # --------------------------------------------------------------------
    # Exception

    def formatException(self, info):
        items = [self.formatExceptionTitle(info),
                 self.formatExceptionMessage(info),
                 self.formatExceptionAttributes(info),]
        return ''.join(items)

    def exceptions(self):
        """ Return a list of exceptions info, starting at self.info """
        try:
            return [self.info] + self.info[1].exceptions()
        except AttributeError:
            return [self.info]

    def formatExceptionTitle(self, info):
        return self.formatter.subSubTitle(self.exceptionTitle(info))
        
    def formatExceptionMessage(self, info):
        """ Handle multiple paragraphs in exception message """
        text = View.exceptionMessage(self, info)
        text = text.split('\n\n')
        text = ''.join([self.formatter.paragraph(item) for item in text])
        return text

    def formatExceptionAttributes(self, info):
        attribtues = []
        for name, value in self.exceptionAttributes(info):
            value = self.formatter.repr(value)
            attribtues.append('%s = %s' % (name, value))
        return self.formatter.list(attribtues)

    def exceptionAttributes(self, info):
        """ Return list of tuples [(name, value), ...] """
        instance = info[1]
        attribtues = []
        for name in dir(instance):
            if name.startswith('_'):
                continue
            value = getattr(instance, name)
            attribtues.append((name, value))
        return attribtues

    def exceptionTitle(self, info):
        type = info[0]
        return getattr(type, '__name__', str(type))
        
    def exceptionMessage(self, info):
        instance = info[1]
        if hasattr(instance, '__html__'):
            return instance.__html__()
        else:
            return pydoc.html.escape(str(instance))


    # -----------------------------------------------------------------
    # System details

    def formatSystemDetails(self):
        details = ['Date: %s' % self.date(),
                   'Platform: %s' % self.platform(),
                   'Python: %s' % self.python(),]
        details += self.applicationDetails()
        return (self.formatter.subTitle('System Details') +
                self.formatter.list(details, {'class': 'system'}))

    def date(self):
        import time
        rfc2822Date = time.strftime("%a, %d %b %Y %H:%M:%S +0000",
                                    time.gmtime())
        return rfc2822Date

    def platform(self):
        try:
            return pydoc.html.escape(' '.join(os.uname()))
        except:
            return pydoc.html.escape('%s (%s)' % (sys.platform, os.name))

    def python(self):
        return 'Python %s (%s)' % (sys.version.split()[0], sys.executable)

    def applicationDetails(self):
        """ Override for your application """
        return []

    # -----------------------------------------------------------------
    # Text traceback

    def formatTextTraceback(self):
        template = self.textTracebackTemplate()
        return template % self.formatOneTextTraceback(self.info)

    def formatOneTextTraceback(self, info):
        """ Separate to enable formatting multiple tracebacks. """
        return ''.join(traceback.format_exception(*info))
    
    def textTracebackTemplate(self):
        return '''
    
<!-- The above is a description of an error in a Python program,
     formatted for a Web browser. In case you are not reading this 
     in a Web browser, here is the original traceback:

%s
-->
'''

class Hook:
    """A hook to replace sys.excepthook that shows tracebacks in HTML."""

    def __init__(self, display=1, logdir=None, context=5, file=None,
                 format="html", viewClass=View, debug=0):
        self.display = display          # send tracebacks to browser if true
        self.logdir = logdir            # log tracebacks to files if not None
        self.context = context          # number of source code lines per frame
        self.file = file or sys.stdout  # place to send the output
        self.format = format
        self.viewClass = viewClass
        self.debug = debug

    def __call__(self, etype, evalue, etb):
        self.handle((etype, evalue, etb))

    def handle(self, info=None):
        info = info or sys.exc_info()
        if self.format.lower() == "html":
            formatter = HTMLFormatter()
            plain = False
        else:
            formatter = TextFormatter()
            plain = True
        try:
            view = self.viewClass(info, self.debug)
            doc = view.format(formatter, self.context)
        except:
            raise
            doc = ''.join(traceback.format_exception(*info))
            plain = True

        if self.display:
            if plain:
                doc = doc.replace('&', '&amp;').replace('<', '&lt;')
                self.file.write('<pre>' + doc + '</pre>\n')
            else:
                self.file.write(doc + '\n')
        else:
            self.file.write('<p>A problem occurred in a Python script.\n')

        if self.logdir is not None:
            import os, tempfile
            suffix = ['.txt', '.html'][self.format=="html"]
            (fd, path) = tempfile.mkstemp(suffix=suffix, dir=self.logdir)
            try:
                file = os.fdopen(fd, 'w')
                file.write(doc)
                file.close()
                msg = '<p> %s contains the description of this error.' % path
            except:
                msg = '<p> Tried to save traceback to %s, but failed.' % path
            self.file.write(msg + '\n')
        try:
            self.file.flush()
        except: pass

# ------------------------------------------------
# CGI Debug
def cgi_debug():
    sys.excepthook = Hook(file=sys.stdout)

# ------------------------------------------------
# Debug Middleware  

class DebugMiddleware(object):

    def __init__(self, application):
        self.application = application
            
    def __call__(self, environ, start_response):
        started = False
        def detect_start_response(status, headers, exc_info=None):
            try:
                result = start_response(status, headers, exc_info)
                started = True
                return result
            except: pass
            else:
                started = True
    
        app_iter = self.application(environ, detect_start_response)
        if not started:
            start_response('500 Internal Server Error',
                           [('content-type', 'text/html')],
                           sys.exc_info())
        
        return self.catching_iter(app_iter, environ)

    def catching_iter(self, app_iter, environ):
        if not app_iter:
            raise StopIteration
        error_on_close = False
     
        try:
            for v in app_iter:
                yield v
            if hasattr(app_iter, 'close'):
                error_on_close = True
                app_iter.close()
        except:
            response = self.exception_handler(environ)
            if not error_on_close and hasattr(app_iter, 'close'):
                try:
                    app_iter.close()
                except:
                    response = self.exception_handler(environ)
            yield response

    def exception_handler(self, environ):
        from StringIO import StringIO
               
        # html debugging output
        out = StringIO()
        Hook(file=out, format="html").handle()
        return out.getvalue()
