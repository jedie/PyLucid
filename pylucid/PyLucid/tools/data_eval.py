#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Data eval
    ~~~~~~~~~

    Evaluate a Python expression string, but only Python data type objects:
        - Constants, Dicts, Lists, Tuples
        - from datetime: datetime and timedelta

    Error class hierarchy:

        DataEvalError
         +-- EvalSyntaxError (compiler SyntaxError)
         +-- UnsafeSourceError (errors from the AST walker)

    Note
    ~~~~
    Based on "Safe" Eval by Michael Spencer
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/364469

    Last commit info:
    ~~~~~~~~~~~~~~~~~
    $LastChangedDate$
    $Rev$
    $Author$

    :copyleft: 2008 by the PyLucid team.
    :license: GNU GPL v3, see LICENSE.txt for more details.
"""

import compiler


# For visitName()
NAME_MAP = {"None": None, "True": True, "False": False}

# For visitGetattr(): key is the callable name and value is the module name
ALLOWED_CALLABLES = {
    "datetime" : "datetime",
    "timedelta": "datetime",
}


class SafeEval(object):
    """
    walk to compiler AST objects and evaluate only data type objects. If other
    objects found, raised a UnsafeSourceError
    """
    def visit(self, node, **kw):
        node_type = node.__class__.__name__
#        print "node_type:", node_type
        method_name = "visit" + node_type
        method = getattr(self, method_name, self.unsupported)
        result = method(node, **kw)
        return result

    def visitExpression(self, node, **kw):
        for child in node.getChildNodes():
            return self.visit(child, **kw)

    #_________________________________________________________________________
    # Errors

    def unsupported(self, node, **kw):
        raise UnsafeSourceError(
            "Unsupported source construct", node.__class__, node
        )

    def visitName(self, node, **kw):
        if node.name in NAME_MAP:
            return NAME_MAP[node.name]

        raise UnsafeSourceError(
            "Strings must be quoted", node.name, node
        )

    #_________________________________________________________________________
    # supported nodes

    def visitConst(self, node, **kw):
        return node.value

    def visitDict(self, node, **kw):
        return dict([(self.visit(k),self.visit(v)) for k,v in node.items])

    def visitTuple(self, node, **kw):
        return tuple(self.visit(i) for i in node.nodes)

    def visitList(self, node, **kw):
        return [self.visit(i) for i in node.nodes]

    #_________________________________________________________________________
    # ALLOWED_CALLABLES nodes

    def visitGetattr(self, node, **kw):
        """
        returns the callable object, if its in ALLOWED_CALLABLES.
        """
        attrname = node.attrname
        try:
            callable_name = ALLOWED_CALLABLES[attrname]
        except KeyError:
            raise UnsafeSourceError("Callable not allowed.", attrname, node)

        module = __import__(callable_name, fromlist=[attrname])
        callable = getattr(module, attrname)

        return callable

    def visitCallFunc(self, node, **kw):
        """
        For e.g. datetime and timedelta
        """
        child_node = node.asList()[0]
        callable = self.visit(child_node)
        args = [self.visit(i) for i in node.args]
        return callable(*args)


def data_eval(source):
    """
    Compile the given source string to AST objects and evaluate only data
    type objects.
    """
    if not isinstance(source, basestring):
        raise DataEvalError("source must be string/unicode!")
    source = source.replace("\r\n", "\n").replace("\r", "\n")
    try:
        ast = compiler.parse(source, "eval")
    except SyntaxError, e:
        raise EvalSyntaxError(e)

    return SafeEval().visit(ast)


#_____________________________________________________________________________
# ERROR CLASS

class DataEvalError(Exception):
    """ main error class for all data eval errors """
    pass

class EvalSyntaxError(DataEvalError):
    """ compile raised a SyntaxError"""
    pass

class UnsafeSourceError(DataEvalError):
    """ Error class for the SafeEval AST walker """
    def __init__(self, error, descr = None, node = None):
        self.error = error
        self.descr = descr
        self.node = node
        self.lineno = getattr(node, "lineno", None)

    def __repr__(self):
        return "%s in line %d: '%s'" % (self.error, self.lineno, self.descr)

    __str__ = __repr__



#_____________________________________________________________________________
# UNITTEST



import unittest

class TestDataEval(unittest.TestCase):
    def assert_eval(self, data):
        data_string = repr(data)
        result = data_eval(data_string)
        #print data, type(data), result, type(result)
        self.assertEqual(result, data)

    def testNone(self):
        self.assert_eval(None)

    def testBool(self):
        self.assert_eval(True)
        self.assert_eval(False)
        self.assert_eval([True, False])

    def testConst(self):
        self.assert_eval(1)
        self.assert_eval("FooBar")
        self.assert_eval(u"FooBar")

    def testTuple(self):
        self.assert_eval(())
        self.assert_eval((1,2))
        self.assert_eval(("1", u"2", None, True, False))

    def testList(self):
        self.assert_eval([])
        self.assert_eval([1,2,3,4])
        self.assert_eval(["foo", u"bar", None, True, False])

    def testDict(self):
        self.assert_eval({})
        self.assert_eval({1:2})
        self.assert_eval({"foo":"bar", u"1": None, 1:True, 0:False})

    def testDatetime(self):
        from datetime import datetime, timedelta
        self.assert_eval(datetime.now())
        self.assert_eval({"dt": datetime.now()})
        self.assert_eval(timedelta(seconds=2))

    def testLineendings(self):
        data_eval("\r\n{\r\n'foo'\r\n:\r\n1\r\n}\r\n")
        data_eval("\r{\r'foo'\r:\r1\r}\r")

    def testNoString(self):
        self.assertRaises(DataEvalError, data_eval, 1)

    def testQuoteErr(self):
        self.assertRaises(UnsafeSourceError, data_eval, "a")
        self.assertRaises(DataEvalError, data_eval, "a")

    def testUnsupportedErr(self):
        self.assertRaises(UnsafeSourceError, data_eval, "a+2")
        self.assertRaises(UnsafeSourceError, data_eval, "eval()")
        self.assertRaises(DataEvalError, data_eval, "eval()")

    def testSyntaxError(self):
        self.assertRaises(EvalSyntaxError, data_eval, ":")
        self.assertRaises(EvalSyntaxError, data_eval, "import os")
        self.assertRaises(DataEvalError, data_eval, "import os")



if __name__ == '__main__':
    unittest.main()
