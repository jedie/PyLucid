#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Unitest für \PyLucid\system\URLs.py
"""


import sys, unittest


from DBwrapper import SQL_wrapper


# Note: You must manually edit the Host-Adress of the MySQL-Server!
MySQLserver = "localhost"
MySQLserver = "192.168.6.2"


#~ debug = debug
debug = False




class testDBwrapper(unittest.TestCase):
    def setUp(self):
        self.db = SQL_wrapper(sys.stdout)
        self.db.tableprefix="unittest_"

    def test_sqlite(self):
        print "\n\nSQLite test"

        self.db.connect_sqlite(":memory:")
        if debug:
            print "self.dbtyp.......:", self.db.self.dbtyp
            print "tableprefix.:", self.db.tableprefix
            print "paramstyle..:", self.db.paramstyle
            print "placeholder.:", self.db.placeholder

        # Create Table
        createTableStatement = (
            "CREATE TABLE $$TestTable ("
            "id INTEGER PRIMARY KEY,"
            "data1 VARCHAR(50) NOT NULL,"
            "data2 VARCHAR(50) NOT NULL"
            ");"
        )
        try:
            self.check(createTableStatement)
        finally:
            self.cleanup()

    def test_mysql(self):
        print "\n\nMySQL test"

        self.db.connect_mysqldb(
            host    = MySQLserver,
            user    = "UserName",
            passwd  = "Password",
            db      = "DatabaseName",
        )
        if debug:
            print "self.dbtyp.......:", self.db.self.dbtyp
            print "tableprefix.:", self.db.tableprefix
            print "paramstyle..:", self.db.paramstyle
            print "placeholder.:", self.db.placeholder

        # Create Table
        createTableStatement = (
            "CREATE TABLE $$TestTable ("
            "id INT( 11 ) NOT NULL AUTO_INCREMENT,"
            "data1 VARCHAR( 50 ) NOT NULL,"
            "data2 VARCHAR( 50 ) NOT NULL,"
            "PRIMARY KEY ( id )"
            ") TYPE = InnoDB COMMENT = '%s Temporary test table';"
        ) % __file__
        try:
            self.check(createTableStatement)
        finally:
            self.cleanup()

    def cleanup(self):
        try:
            print "Delete the temporary test Table."
            self.db.cursor.execute("DROP TABLE $$TestTable")
            self.assertEqual(self.db.get_tables(), [])
        finally:
            print "Close SQL-connection..."
            self.db.close()

    def check(self, createTableStatement):
        print "- "*40

        print "get_tables()"
        self.assertEqual(self.db.get_tables(), [])

        print "Creat a temporary test table - execute SQL-command directly"
        self.db.cursor.execute(createTableStatement)
        self.db.commit()
        tables = self.db.get_tables()
        if debug: print tables
        self.assertEqual(tables, [u'unittest_TestTable'])


        print "get_table_fields()"
        table_fields = self.db.get_table_fields("TestTable")
        if debug: print table_fields
        self.assertEqual(table_fields, ['id', 'data1', 'data2'])


        print "INSERT line 1"
        self.db.insert(
            table = "TestTable",
            data  = { "data1" : "Value A 1", "data2" : "Value A 2" },
            debug = debug
        )
        lastrowid = self.db.cursor.lastrowid
        if debug: print "cursor.lastrowid:", lastrowid
        self.assertEqual(lastrowid, 1)


        print "INSERT line 2"
        self.db.insert(
            table = "TestTable",
            data  = { "data1" : "Value B 1", "data2" : "Value B 2" },
            debug = debug
        )
        lastrowid = self.db.cursor.lastrowid
        if debug: print "cursor.lastrowid:", lastrowid
        self.assertEqual(lastrowid, 2)


        print "SELECT"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
            where           = ("data1","Value B 1"),
            debug           = debug
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'Value B 1', 'id': 2, 'data2': u'Value B 2'}]
        )

        print "tableDict"
        result = self.db.get_tableDict(
            select_items = ["data1","data2"],
            index_key = "id",
            table_name = "TestTable",
        )
        self.assertEqual(
            result,
            {
                1L: {'data1': u'Value A 1', 'id': 1L, 'data2': u'Value A 2'},
                2L: {'data1': u'Value B 1', 'id': 2L, 'data2': u'Value B 2'}
            }
        )

        print "DELETE line 1"
        self.db.delete(
            table = "TestTable",
            where = ("id",1),
            limit = 1,
            debug = debug
        )
        print "SELECT"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
            #~ where           = ("data1","Value B 1"),
            debug           = debug
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'Value B 1', 'id': 2, 'data2': u'Value B 2'}]
        )

        if debug:
            self.db.dump_table("TestTable")

        print "UPDATE line 2"
        self.db.update(
            table   = "TestTable",
            data    = {"data1" : "NewValue1!"},
            where   = ("id",2),
            debug = debug
        )
        if debug: print "cursor.lastrowid:", self.db.cursor.lastrowid
        self.db.commit()

        print "SELECT *"
        result = self.db.select(
            select_items    = ["id","data1","data2"],
            from_table      = "TestTable",
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'NewValue1!', 'id': 2, 'data2': u'Value B 2'}]
        )


        print "Test Transaction:"
        self.db.insert("TestTable", {"data1": "tranceact1", "data2": "1"})
        id1 = self.db.cursor.lastrowid
        self.db.insert("TestTable", {"data1": "tranceact2", "data2": "2"})
        id2 = self.db.cursor.lastrowid
        self.db.delete(
            table = "TestTable",
            where = ("id",id1),
        )
        self.db.update(
            table   = "TestTable",
            data    = {"data1": "tranceact3"},
            where   = ("id",id2)
        )
        result = self.db.select(
            select_items    = "*",
            from_table      = "TestTable",
            order           = ("id","ASC"),
        )
        if debug: self.db.dump_select_result(result)
        self.db.rollback() # Alle letzten Befehle rückgängig machen
        result = self.db.select(
            select_items    = "*",
            from_table      = "TestTable",
            order           = ("id","ASC"),
        )
        if debug: self.db.dump_select_result(result)
        self.assertEqual(
            result,
            [{'data1': u'NewValue1!', 'id': 2, 'data2': u'Value B 2'}]
        )






def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testDBwrapper))
    return suite





if __name__ == "__main__":
    print
    print ">>> %s - Unitest:" % __file__
    print "_"*79
    unittest.main()
    sys.exit()



