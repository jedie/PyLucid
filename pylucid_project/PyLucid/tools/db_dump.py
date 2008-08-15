# http://www.djangosnippets.org/snippets/14/
#
# Author: limodou (limodou@gmail.com)
#
# This tool is used for dump and reload data from and into database
# You can see the help info through:
#
#     python db_dump.py -h
#
# For now, it only support .py format, so the output result will
# be saved as python source code, and you can import it.
#
# Version 1.7 2007-05.24
#
# Update 1.0 2007-01-18
#
# Update 1.1 2007-01-19
#    * if no arguments after db_dump.py, then it'll show help infomation
#
# Update 1.2 2007-01-20
#    * change dumpdb to use model info but not cursor.description,
#      because some database backend does not support cursor.description
#
# Update 1.3 2007-01-20
#    * change the output format of data file, and improve the process
#      effective of dumpping and loading
#
# Update 1.4 2007-01-21
#    * support mysql
#
# Update 1.5 2007-02-08
#    * If the filename is not exists, then skip it
#
# Update 1.6 2007-04-09
#    * Add float support
#
# Update 1.7 2007-05-24
#    * Backwards-incompatible change update by Jens Diemer:
#        May 8, 2007: Generic relations have moved
#
# Update 1.8 2007-08-22
#    * Backwards-incompatible change update by Jens Diemer:
#        http://www.djangosnippets.org/snippets/14/#c423

import os, sys
from optparse import OptionParser
import datetime
import decimal

def _get_table_order(app_labels):
    from django.db.models import get_app, get_apps, get_models
    from django.db.models import ForeignKey, OneToOneField

    if not app_labels:
        app_list = get_apps()
    else:
        app_list = [get_app(app_label) for app_label in app_labels]

    models = {}
    for app in app_list:
        for model in get_models(app):
            models[model._meta.db_table] = model
    s = []
    rules = []

    def order(s, rule):
        a, b = rule
        try:
            i = s.index(a)
            try:
                j = s.index(b)
                if j<i:
                    del s[i]
                    s.insert(j, a)
            except:
                s.append(b)
        except:
            s.append(a)
            try:
                j = s.index(b)
                del s[j]
                s.append(b)
            except:
                s.append(b)

    for i, table in enumerate(models.keys()[:]):
        for field in models[table]._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                tname = field.rel.to._meta.db_table
                if not models.has_key(tname) or tname == table:
                    continue
                rules.append((tname, table))
                order(s, (tname, table))

    n = []
    for k, v in models.items():
        if s.count(k) == 0:
            n.append(k)

    return [models[k] for k in s+n]

def _find_key(d, key):
    if not d:
        return None
    for k, v in d.items()[:]:
        if k == key:
            return d
        else:
            result = _find_key(v, key)
            if result is not None:
                return result

def loaddb(app_labels, format, options):
    from django.db import connection, transaction, backend


    if options.verbose:
        print "Begin to load data for %s format...\n" % format

    models = _get_table_order(app_labels)

    cursor = connection.cursor()

    errornum = 0

    if not options.remain and not options.stdout:
        m = models[:]
        m.reverse()
        for model in m:
            cursor.execute('DELETE FROM %s WHERE 1=1;' % backend.quote_name(model._meta.db_table))
            for table, fields in get_model_many2many_stru(model):
                cursor.execute('DELETE FROM %s WHERE 1=1;' % backend.quote_name(table))

    success = True
    for model in models:
        try:
            load_model(cursor, model, format, options)
            for table, fields in get_model_many2many_stru(model):
                load_model(cursor, (table, fields), format, options)
        except Exception, e:
            success = False
            errornum += 1

#    if success:
    transaction.commit_unless_managed()
#    else:
#        transaction.rollback_unless_managed()

#    if errornum:
#        print "There are %d errors found! The database has been rollbacked!" % errornum
#    else:
#        print "Successful!"

def load_model(cursor, model, format, options):
    from django.db import backend

    datadir, verbose, stdout = options.datadir, options.verbose, options.stdout
    sql = 'INSERT INTO %s (%s) VALUES (%s);'

    if isinstance(model, (tuple, list)):
        filename = os.path.join(datadir, model[0] + '.%s' % format)
        fields, default = model[1], {}
    else:
        opts = model._meta
        filename = os.path.join(datadir, opts.db_table + '.%s' % format)
        fields, default = get_model_stru(model)

    if verbose:
        print '..Dealing %s for %s format...\n' % (filename, format)
    if not os.path.exists(filename):
        if verbose:
            print '..%s does not exists, so Skip it..\n' % filename
        return
    try:
        objs = {}
        if format == 'py':
            s = []
            f = file(filename, 'rb')
            for line in f:
                varname = line.split('=')[0]
                if varname.strip() != 'records':
                    s.append(line)
                else:
                    d = {}
                    exec ''.join(s) in d
                    objs['table'] = d.get('table', '')
                    objs['fields'] = d.get('fields', [])
                    objs['default'] = d.get('default', {})
                    objs['records'] = f
                    break
        else:
#            f = file(filename, 'rb')
#            objs = f.read()
#            records = objs['records']
#            f.close()
            raise 'Not support this format %s' % format

        fs = objs['fields']
        table = objs['table']

        default.update(objs.get('default', {}))
        count = 0
        for row in objs["records"]:
            if row.strip() == ']':
                break
            row = eval(row)
            d = dict(zip(fs, row))
            sql_fields = []
            sql_values = []
            for fd in fields:
                v = None
                if d.has_key(fd):
                    v = d[fd]
                else:
                    if default.get(fd, None) is not None:
                        kind, value = default[fd]
                        if not kind or kind == 'value':
                            v = value
                        elif kind == 'reference':
                            try:
                                v = d[value]
                            except KeyError:
                                sys.stderr.write("Referenced field [%s] does not exist\n" % value)
                                raise

                        elif kind == 'date':
                            if not value or value == 'now':
                                v = datetime.date.today().strftime('%Y-%m-%d')
                            else:
                                v = value
                        elif kind == 'datetime':
                            if not value or value == 'now':
                                v = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            else:
                                v = value
                        else:
                            raise Exception, "Cann't support this default type [%s]\n" % kind
                if v is not None:
                    sql_fields.append(fd)
                    sql_values.append(v)
            e_sql = sql % (backend.DatabaseOperations().quote_name(table),
                ','.join(map(backend.DatabaseOperations().quote_name, sql_fields)), ','.join(['%s'] * len(sql_fields)))
            if stdout:
                print e_sql, sql_values, '\n'
            else:
                try:
                    cursor.execute(e_sql, sql_values)
                    count += 1
                except:
                    sys.stderr.write("Error sql: %s %s\n" % (e_sql, sql_values))
                    raise
        if verbose:
            print '(Total %d records)\n' % count
    except Exception, e:
        import traceback
        traceback.print_exc()
        sys.stderr.write("Problem loading %s format '%s' : %s\n" %
                 (format, filename, str(e)))
        raise

def get_model_stru(model):
    from django.db.models.fields import DateField, DateTimeField, TimeField

    fields = []
    default = {}
    for f in model._meta.fields:
        fields.append(f.column)
        v = f.get_default()
        if v is not None:
            default[f.column] = ('value', v)
        if isinstance(f, (DateTimeField, DateField, TimeField)):
            if f.auto_now or f.auto_now_add:
                v = datetime.datetime.now()
                default[f.column] = ('value', f.get_db_prep_save(v))
    return fields, default

def get_model_many2many_stru(model):
    try:
        from django.db.models import GenericRel
    except ImportError:
        # since May 8, 2007 (Changeset 5172): Generic relations have moved
        # http://code.djangoproject.com/wiki/BackwardsIncompatibleChanges
        # http://code.djangoproject.com/changeset/5172
        from django.contrib.contenttypes.generic import GenericRel

    opts = model._meta
    for f in opts.many_to_many:
        fields = []
        if not isinstance(f.rel, GenericRel):
            fields.append('id')
            fields.append(f.m2m_column_name())
            fields.append(f.m2m_reverse_name())
            yield f.m2m_db_table(), fields


def dumpdb(app_labels, format, options):
    from django.db.models import get_app, get_apps, get_models

    datadir, verbose, stdout = options.datadir, options.verbose, options.stdout

    if verbose:
        print "Begin to dump data for %s format...\n" % format

    if len(app_labels) == 0:
        app_list = get_apps()
    else:
        app_list = [get_app(app_label) for app_label in app_labels]

    if not os.path.exists(datadir):
        os.makedirs(datadir)

    errornum = 0
    for app in app_list:
        for model in get_models(app):
            try:
                write_result(dump_model(model), format, options)

                for result in dump_many2many(model):
                    write_result(result, format, options)
            except Exception, e:
                import traceback
                traceback.print_exc()
                sys.stderr.write("Unable to dump database: %s\n" % e)
                errornum += 1

    if errornum:
        print "There are %d errors found!" % errornum
    else:
        print "Successful!"

def dump_model(model):
    from django.db import connection, backend

    opts = model._meta
    cursor = connection.cursor()
    fields, default = get_model_stru(model)
    cursor.execute('select %s from %s' %
        (','.join(map(backend.DatabaseOperations().quote_name, fields)), backend.DatabaseOperations().quote_name(opts.db_table)))
    return call_cursor(opts.db_table, fields, cursor)

def call_cursor(table, fields, cursor):
    yield table
    yield fields
    while 1:
        rows = cursor.fetchmany(100)
        if rows:
            for row in rows:
                yield _pre_data(row)
        else:
            break

def _pre_data(row):
    row = list(row)
    for i, fd in enumerate(row):
        if isinstance(fd, datetime.datetime):
            row[i] = row[i].strftime('%Y-%m-%d %H:%M:%S') # + '.' + str(row[i].microsecond).rstrip('0')
        elif isinstance(fd, datetime.date):
            row[i] = row[i].strftime('%Y-%m-%d')
        elif isinstance(fd, decimal.Decimal):
            row[i] = row[i].__float__()

    return row

def dump_many2many(model):
    from django.db import connection, backend

    cursor = connection.cursor()

    for table, fields in get_model_many2many_stru(model):
        cursor.execute('select %s from %s' %
            (','.join(map(backend.DatabaseOperations().quote_name, fields)), backend.DatabaseOperations().quote_name(table)))
        yield call_cursor(table, fields, cursor)

def write_result(result, format, options):
    table = result.next()
    fields = result.next()
    filename = os.path.join(options.datadir, table + '.%s' % format)
    if options.verbose:
        print '..Dumping %s ...\n' % filename
    if not options.stdout:
        f = file(filename, 'wb')
    else:
        f = sys.stdout
    print >>f, 'table = %r' % table
    print >>f, 'fields = %r' % fields
    print >>f, '#default item format: "fieldname":("type", "value")'
    print >>f, 'default = {}'
    print >>f, 'records = ['
    i = 0
    for t in result:
        print >>f, repr(t)
        i += 1
    print >>f, ']'
    if options.verbose:
        print '(Total %d records)\n' % i
    if not options.stdout:
        f.close()

def get_usage():
    usage = """
  %prog [options] action [applist]:
      action: dump load
"""
    return usage

def execute_from_command_line(argv=None):
    # Use sys.argv if we've not passed in a custom argv
    if argv is None:
        argv = sys.argv

    # Parse the command-line arguments. optparse handles the dirty work.
    parser = OptionParser(usage=get_usage())
    parser.add_option('--settings',
        help='Python path to settings module, e.g. "myproject.settings.main". If this isn\'t provided, the DJANGO_SETTINGS_MODULE environment variable will be used.')
    parser.add_option('-d', '--dir', help='Output/Input directory.', default="datadir", dest="datadir")
#    parser.add_option('-f', '--format', help='Data format(json, xml, python).', type="choice",
#        choices=['json', 'xml', 'python'], default='json')
    parser.add_option('-v', '--verbose', help='Verbose mode', action='store_true')
    parser.add_option('-s', '--stdout', help='Output the data to stdout', action='store_true')
    parser.add_option('-r', '--remain', help='Remain the records of the tables, default will delete all the records. Only used for loading.', action='store_true')

    options, args = parser.parse_args(argv[1:])

    if len(args) == 0:
        parser.print_help()
        sys.exit(0)

    action = args[0]
    apps = args[1:]
    if options.settings:
        os.environ['DJANGO_SETTINGS_MODULE'] = options.settings
    else:
        from django.core.management import setup_environ
        try:
            import settings
        except ImportError:
            print "You don't appear to have a settings file in this directory!"
            print "Please run this from inside a project directory"
            sys.exit()

        setup_environ(settings)

    if action == 'dump':
        dumpdb(apps, 'py', options)
    elif action == 'load':
        loaddb(apps, 'py', options)
    else:
        parser.print_help()

if __name__ == '__main__':
    execute_from_command_line()
