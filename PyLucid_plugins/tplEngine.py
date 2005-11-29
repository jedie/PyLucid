#!/usr/bin/python

###############################################################################
#
#  A Python template engine supporting, supporting variables, loops/blocks,
#  recursion and template cache. Its template language is object oriented and
#  easily comprehensible for non-programmers.
#
#  Copyright (C) 2005 Nils Adermann (http://www.naderman.de)
#
#  This library is free software; you can redistribute it and/or modify it
#  under the terms of the GNU Lesser General Public License as published by the
#  Free Software Foundation; either version 2.1 of the License, or (at your
#  option) any later version.
#
#  This library is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
#  for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this library; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
###############################################################################

import sys, os, re, ConfigParser;

RECOMPILE_ALWAYS = 2
RECOMPILE_CHANGED = 1
RECOMPILE_NEVER = 0


class TplCompilerError(Exception):

    """This Exception is used for all errors occuring during the compilation process.

    Be aware that included files increase the line number!
    """

    def __init__(self, message, file, line):

        self.message = message
        self.line = line
        self.file = file


    def __str__(self):

        """Returns a message with details about where the compiler found the error."""

        return self.message + ' in "' + self.file + '" on line ' + str(self.line)



class TplFileError(Exception):

    """This Exception is used whenever there is any file/directory related problem."""

    def __init__(self, message, file):

        self.file = file
        self.message = message


    def __str__(self):

        """Returns a message, %(file)s is replaced with the file argument given to the constructor."""

        file = self.file
        return self.message % {'file': file}




class TplCompiler(object):

    """Compiles Raw Template Files and returns a string with python code.

    You should only use the constructor and compile methods.
    """

    def __init__(self, conf, raw_template, file_name):

        """Constructor which simply stores the relevant data in attributes and initialises some variables."""

        self.conf = conf
        self.raw_template = raw_template
        self.file_name = file_name
        self.indent = 0
        self.new_indent = 0
        self.errpos = ''
        self.match = {}
        self.in_block = []
        self.in_recursion = []


    def get_indent(self, indent):

        """Returns indentation whitespaces."""

        return ' ' * 4 * indent


    def pre_space(self, string):

        """Returns the part of string in front of the first space found."""

        return string[0:string.find(' ')]


    def post_space(self, string):

        """Returns the part of string after the first space found."""

        return string[string.find(' ') + 1:]


    def pre_escaped_new_line(self, string):

        """Removes all trailing whitespaces from string until the last character is an escaped new line."""

        m = len(string)
        if m < 1:
            return string
        j = 1

        while ((string[(m-j)].isspace()) and (string[(m-j)] != "\n")) or (string[(m-j-1):(m-j+1)] == '\\n') or (string[(m-j)] == '\\'):
            if string[(m-j-2):(m-j)] == '\\n':
                j += 3
                break
            j += 1

        return string[0:(m-j+1)]


    def get_recursion_name(self, name):

        """Creates a valid function name used for recursion from name."""

        return "func_recursion_" + re.compile(r"[^a-z]").sub("", name.lower())


    def append_python_char(self, string, char):

        """Append char to string but escape newlines and double quotes."""

        if char == "\n":
            string += "\\n"

        elif char == "\"":
            string += "\\\""

        else:
            string += char

        return string


    def object_path_to_real_path(self, var, block=False):

        """Generates the Python code referencing a variable based on var.

        If block is True the function creates the code referencing to a block instead of a variable.
        """

        parts = var.split('.')
        name = parts.pop()
        var = 'self'

        if len(parts) <= 0:

            if not block:
                var += '.vars["' + name + '"]'

            else:
                var += '.blocks["' + parts[0] + '"]'

        else:

            var += '.blocks["' + parts[0] + '"].runs[x[0]]'

            for i in range(1, len(parts)):
                var += '["b"]["' + parts[i] + '"].runs[x[' + str(i) + ']]'

            if not block:
                var += '["v"]["' + name + '"]'

            else:
                var += '["b"]["' + name + '"]'

        return var


    def object_path_to_python(self, object_path, length, block):

        """Retruns python code which will return the value associated with object_path.

        If length is True, code for returning the length of the block in object_path is generated.

        If block is True, code for retruning the block in object_path is generated.
        """

        python = "self"
        parts = object_path.split('.')

        if len(parts) == 0:
            parts = [object_path]

        n = (len(parts) - 1)

        if not length:

            if parts[n] == 'LENGTH':
                length = True
                parts.pop()
                n = n - 1

        check = []
        check.extend(parts)

        if not block and not length:
            check.pop()

        recursion = False

        for i in range(1, len(check) + 1):

            x = len(check) - i
            for j in range(x+1):

                if ".".join(check[j:j+i]) in self.in_recursion:
                    recursion = True
                    break

            else:
                break

        if length:
            check.pop()

        if (len(check) > 0) and (".".join(check) not in self.in_block):
            raise TplCompilerError(".".join(parts) + ' is not inside the block ' + ".".join(check), self.file, self.line)


        for i in range(n):

            if (recursion) and (i == n - 1):
                python += '.get_recursive_block(x, "' + parts[i] + '", depth, ' + str(i) + ')'

            else:
                python += '.get_block(x[' + str(i) + '], "' + parts[i] + '")'

        if length:

            if recursion:
                if python.rfind('.') != -1:
                    python = python[0:python.rfind('.')]
                if (len(parts) > 1) and (parts[len(parts)-2] == parts[len(parts)-1]):
                    python += '.get_recursive_block(x, "' + parts[n] + '", depth+1, ' + str(n-1) + ')'
                else:
                    python += '.get_recursive_block(x, "' + parts[n] + '", depth, ' + str(n) + ')'

            else:
                python += '.get_block(x[' + str(n) + '], "' + parts[n] + '")'

            python += '.get_length()'

        else:

            if not block:

                if parts[n] == 'RUN':

                    if recursion:
                        python = 'x[depth]'

                    else:
                        python = 'x[' + str(n) + ']'

                else:

                    if recursion:
                        python += '.get_var(x[depth], "' + parts[n] + '")'

                    else:
                        python += '.get_var(x[' + str(n) + '], "' + parts[n] + '")'

            else:

                if recursion:
                    python += '.get_recursive_block(x, "' + parts[n] + '", depth, ' + str(n) + ')'

                else:
                    python += '.get_block(x[' + str(n) + '], "' + parts[n] + '")'

        return python


    def expression_to_python(self, expression):

        """This function converts a template expression to python code.

        Be aware, it's really tricky!
        """

        python = ''
        expression += ' '
        n = len(expression)
        in_string = False
        in_func = False
        escaped = False
        word = ''
        type = ''
        functions = []
        tmp = ''
        extra_operators = ['(', ')', ' ']
        no_end_operators = ['isset', 'isSet', 'ev', 'isEven', 'odd', 'isOdd']
        last_op = 'True'
        in_func_string = False

        i = 0
        while i < n:

            char = expression[i]

            if in_string:

                if (char == '\\') and (not escaped):
                    escaped = True

                elif (char == '"') and (not escaped):
                    in_string = False

                else:
                    escaped = False

                word += char

            elif in_func:

                if (len(functions[(len(functions) - 1)]['params']) == 0) and (char == ')'):

                    in_func = False

                else:

                    if len(functions[(len(functions) - 1)]['params']) == 0:
                        functions[(len(functions) - 1)]['params'].append('')

                    if in_func_string:
                        functions[(len(functions) - 1)]['params'][(len(functions[(len(functions) - 1)]['params']) - 1)] += word
                        word = tmp[:]
                        tmp = ''
                        in_func_string = False

                    if char == '(':
                        brackets += 1
                        functions[(len(functions) - 1)]['params'][(len(functions[(len(functions) - 1)]['params']) - 1)] += char

                    elif char == '"':
                        in_string = True
                        in_func_string = True
                        escaped = False
                        tmp = word[:]
                        word = '"'

                    elif char == ')':

                        if brackets == 0:
                            in_func = False
                            tmp = ''

                        else:
                            brackets -= 1
                            functions[(len(functions) - 1)]['params'][(len(functions[(len(functions) - 1)]['params']) - 1)] += char

                    elif (char == ',') and (brackets == 0):
                        functions[(len(functions) - 1)]['params'].append('')

                    else:
                        functions[(len(functions) - 1)]['params'][(len(functions[(len(functions) - 1)]['params']) - 1)] += char

            else:

                found_op = 'False'

                for operator in self.conf.get_operators():

                    if expression[i:(i + len(operator[0]))] == operator[0]:

                        if (not re.match('[a-zA-Z]', operator[0])) or ((not re.match('[a-zA-Z]', expression[(i - 1)])) and (not re.match('[a-zA-Z]', expression[(i + len(operator[0]))]))):

                            found_op = operator[0]
                            op_replace = operator[1]
                            i = i + len(operator[0]) - 1
                            break


                if found_op != 'False':

                    if type == 'number':
                        python += word

                    elif type == 'var':
                        word = self.object_path_to_python(word, False, False)
                        type = 'string'

                    elif type == 'func':

                        code = self.conf.get_function(functions[0]['name'], len(functions[0]['params']) - 1)
                        code = code.replace('%S', self.expression_to_python(functions[0]['params'][0]))

                        for j in range(1, len(functions[0]['params'])):
                            code = code.replace('%P' + str(j-1), self.expression_to_python(functions[0]['params'][j]))

                        python += code

                    if type == 'string':

                        final = word

                        for function in functions:

                            code = self.conf.get_function(function['name'], len(function['params']))

                            for j in range(len(function['params'])):
                                code = code.replace('%P' + str(j), self.expression_to_python(function['params'][j]))

                            final = code.replace('%S', final)

                        python += final

                    elif type != 'number':

                        if (found_op not in extra_operators) and (last_op != 'False'):
                            raise TplCompilerError('Unexpected Operator', self.file, self.line)

                    python += op_replace
                    type = ''
                    word = ''
                    functions = []

                    if found_op not in extra_operators:
                        last_op = found_op

                    if found_op in no_end_operators:
                        last_op = 'False'

                elif (type != ''):

                    if type == 'number':

                        if char.isdigit():
                            word += char

                        elif (char == '.') and (word.find('.') == -1):
                            word += char

                        else:
                            raise TplCompilerError('Unexpected Character Data', self.file, self.line)

                    elif type == 'func':

                        if char == '.':

                            code = self.conf.get_function(functions[0]['name'], len(functions[0]['params']) - 1)
                            code = code.replace('%S', self.expression_to_python(functions[0]['params'][0]))

                            for j in range(1, len(functions[0]['params'])):
                                code = code.replace('%P' + str(j-1), self.expression_to_python(functions[0]['params'][j]))

                            word = code
                            type = 'string'
                            in_func = True
                            brackets = 0
                            functions = []

                            start = expression.find('(', i, expression.find(' ', i))
                            functions.append({'name': expression[i+1:start],
                                'params': []})
                            i = start

                        else:
                            raise TplCompilerError('Unexpected Character Data', self.file, self.line)

                    elif type == 'string':

                        if char == '.':

                            in_func = True
                            brackets = 0

                            start = expression.find('(', i)
                            functions.append({'name': expression[i+1:start],
                                'params': []})
                            i = start

                        else:
                            raise TplCompilerError('Unexpected Character Data', self.file, self.line)

                    elif type == 'var':

                        if char == '.':

                            next_bracket = expression.find('(', i, expression.find(' ', i))
                            next_dot = expression.find('.', i+1, expression.find(' ', i))

                            if ((next_dot < next_bracket) and (next_dot != -1)) or ((next_dot != -1) and (next_bracket == -1)):
                                word += '.'

                            elif ((next_dot > next_bracket) and (next_bracket != -1)) or ((next_dot == -1) and (next_bracket != -1)):

                                in_func = True
                                brackets = 0
                                functions.append({'name': expression[(i+1):next_bracket],
                                    'params': []})
                                i = next_bracket

                            else:
                                word += '.'

                        else:

                            if not char.isalnum() and char != '_' and char != '-':
                                raise TplCompilerError('Unexpected Token "' + char + '"', self.file, self.line)

                            word += char

                elif char == '"':

                    if last_op == 'False':
                        raise TplCompilerError('Unexpected String', self.file, self.line)

                    last_op = 'False'
                    in_string = True
                    type = 'string'
                    word = char

                elif char.isdigit():

                    if last_op == 'False':
                        raise TplCompilerError('Unexpected digit', self.file, self.line)

                    last_op = 'False'
                    word = char
                    type = 'number'

                elif expression[i:(i+4)].lower() == 'true':

                    if last_op == 'False':
                        raise TplCompilerError('Unexpected Boolean Value', self.file, self.line)

                    last_op = 'False'
                    python += 'True'
                    i += 3

                elif expression[i:(i+5)].lower() == 'false':

                    if last_op == 'False':
                        raise TplCompilerError('Unexpected Boolean Value', self.file, self.line)

                    last_op = 'False'
                    python += 'False'
                    i += 4

                elif re.match('[a-zA-Z_]', char):

                    if last_op == 'False':
                        raise TplCompilerError('Unexpected Variable', self.file, self.line)

                    last_op = 'False'

                    next_bracket = expression.find('(', i, expression.find(' ', i))
                    next_dot = expression.find('.', i+1, expression.find(' ', i))

                    if ((next_dot < next_bracket) and (next_dot != -1)) or ((next_dot != -1) and (next_bracket == -1)):
                        type = 'var'
                        word = char

                    elif ((next_dot > next_bracket) and (next_bracket != -1)) or ((next_dot == -1) and (next_bracket != -1)):

                        type = 'func'
                        in_func = True
                        brackets = 0
                        functions.append({'name': expression[i:next_bracket],
                            'params': []})
                        i = next_bracket

                    else:
                        word = char
                        type = 'var'

                else:
                    raise TplCompilerError('Unexpected Token "' + char + '"', self.file, self.line)

            i += 1

        if last_op != 'False':
            raise TplCompilerError('Unexpected End', self.file, self.line)

        return python[:-1]


    def create_begin(self):

        """Generates Python code which replaces a create command."""

        self.match['content'] = self.post_space(self.match['content'])
        type = self.pre_space(self.match['content'])
        self.match['content'] = self.post_space(self.match['content'])

        if self.match['content'].find(' ') != -1:
            raise TplCompilerError('Unexpected Character Data', self.file, self.line)

        if type == 'BLOCK':

            num = self.match['content'].count('.')
            self.in_block.append(self.match['content'])

            block = self.object_path_to_python(self.match['content'], True, False)

            python = 'x.append(0)\n'
            python += self.get_indent(self.indent) + 'for x[' + str(num + 1) + '] in range(' + block + '):'

            self.new_indent = self.indent + 1

        elif type == 'RECURSION':

            num = self.match['content'].count('.')

            self.in_block.append(self.match['content'])
            self.in_recursion.append(self.match['content'])

            block_length = self.object_path_to_python(self.match['content'], True, False)

            self.new_indent = self.indent + 2

            python = 'try:\n'
            python += self.get_indent(self.indent+1) + self.get_recursion_name(self.match['content']) + '\n'
            python += self.get_indent(self.indent) + 'except NameError:\n'
            python += self.get_indent(self.indent+1) + "def " + self.get_recursion_name(self.match['content']) + "(self, depth, x):\n"
            python += self.get_indent(self.new_indent) + 'x.append(0)\n'
            python += self.get_indent(self.new_indent) + 'o = ""\n'
            python += self.get_indent(self.new_indent) + 'for x[depth] in range(' + block_length + '):'

            self.new_indent += 1

        else:

            raise TplCompilerError('Unknown Loop Type "' + type + '"', self.file, self.line)

        return python


    def create_if(self):

        """Generates Python code which replaces an if statement."""

        python = 'if ' + self.expression_to_python(self.post_space(self.match['content'])) + ':'

        self.new_indent = self.indent + 1

        return python


    def create_elseif(self):

        """Generates Python code which replaces an elseif statement."""

        self.indent = self.indent - 1

        python = 'elif ' + self.expression_to_python(self.post_space(self.match['content'])) + ':'

        self.new_indent = self.indent + 1

        return python


    def create_else(self):

        """Generates Python code which replaces an else statement."""

        self.indent = self.indent - 1

        return 'else:'


    def create_endif(self):

        """Generates Python code which replaces an endif statement."""

        self.new_indent = self.indent - 1

        return ''


    def create_end(self):

        """Generates Python code which replaces an end command."""

        self.match['content'] = self.post_space(self.match['content'])
        type = self.pre_space(self.match['content'])
        self.match['content'] = self.post_space(self.match['content'])

        if self.match['content'].find(' ') != -1:
            raise TplCompilerError('Unexpected Character Data', self.file, self.line)

        block = self.match['content']

        self.in_block.remove(block)

        if type == 'BLOCK':

            self.new_indent = self.indent - 1

            python = ''
            python += "\n" + self.get_indent(self.indent - 1) + 'x.pop()'

        elif type == 'RECURSION':

            self.new_indent = self.indent - 3
            self.in_recursion.remove(block)

            python = ''
            python += "\n" + self.get_indent(self.indent - 1) + 'x.pop()'
            python += "\n" + self.get_indent(self.indent - 1) + 'return o'
            python += "\n" + self.get_indent(self.new_indent) + "self.func = " + self.get_recursion_name(self.match['content'])
            python += "\n" + self.get_indent(self.new_indent) + "o += self.func(self, len(x), x)"

        else:
            raise TplCompilerError('Unexpected Loop Type "' + type + '"', self.file, self.line)

        return python


    def create_set(self):

        """Generates Python code which replaces a set command."""

        self.match['content'] = self.post_space(self.match['content'])

        operators = ['=', '+', '-', '*', '/', '%', '|', '&', ' ']

        var = ''
        i = 0

        while self.match['content'][i] not in operators:

            var += self.match['content'][i]
            i+=1

            if i >= len(self.match['content']):
                raise TplCompilerError('Unexpected End', self.file, self.line)

        self.match['content'] = self.match['content'][i:]

        operator = ''
        i = 0

        while self.match['content'][i] in operators:

            if self.match['content'][i] != ' ':
                operator += self.match['content'][i]

            i+=1

            if i >= len(self.match['content']):
                raise TplCompilerError('Unexpected End', self.file, self.line)

        self.match['content'] = self.match['content'][i:]

        var = self.object_path_to_real_path(var, False)

        python = var + ' ' + operator + ' ' + self.expression_to_python(self.match['content'])

        return python


    def create_recurse(self):

        """Generates Python code which replaces a recurse command."""

        self.match['content'] = self.post_space(self.match['content'])

        python = "o += self.func(self, len(x), x)"

        return python


    def create_echo(self):

        """Generates Python code which replaces an echo command.

        Print and non command variables are handled by this function as well."""

        python = 'o += str(' + self.expression_to_python(self.match['content']) + ');'

        return python


    def compile(self):

        """Compiles the raw template code in self.raw_template."""

        self.raw_template = self.raw_template.replace('\r\n', '\n')
        self.raw_template = self.raw_template.replace('\r', '\n')

        n = len(self.raw_template)

        record = False
        is_string = False
        in_raw = False
        lines = 1
        self.compiled = ''
        escaped = False
        self.in_block = []
        self.in_recursion = []

        i = 0
        while i < n:

            char = self.raw_template[i]

            if char == "\n":

                lines += 1

                if record and (self.raw_template[i-1] != '\\'):
                    record = False
                    self.compiled += match

            if record:

                if is_string:

                    if (char == "\\") and (not escaped):
                        escaped = True
                        match += char

                    elif (char == '"') and (not escaped):
                        is_string = False
                        match += '"'

                    else:
                        match += char
                        escaped = False

                elif char == '"':

                    is_string = True
                    escaped = False
                    match += '"'

                elif self.raw_template[i:i + len(self.conf.get_general('Parser', 'Postfix'))] == self.conf.get_general('Parser', 'Postfix'):

                    record = False
                    self.new_indent = self.indent
                    self.match = {'content': match,
                                  'raw': match,
                                  'line': str(lines)}
                    self.errpos = 'in ' + self.file_name + ' on line ' + str(lines)
                    self.file = self.file_name
                    self.line = lines

                    space = self.match['content'].find(' ')

                    if space == -1:
                        command = self.match['content']

                    else:
                        command = self.match['content'][:space]

                    if command == 'BEGIN':
                        python = self.create_begin()

                    elif command == 'IF':
                        python = self.create_if()

                    elif command == 'ELSEIF':
                        python = self.create_elseif()

                    elif command == 'ELSE':
                        python = self.create_else()

                    elif command == 'ENDIF':
                        python = self.create_endif()

                    elif command == 'END':
                        python = self.create_end()

                    elif command == 'SET':
                        python = self.create_set()

                    elif command == 'RECURSE':
                        python = self.create_recurse()

                    elif (command == 'ECHO') or (command == 'PRINT'):

                        self.match['content'] = self.post_space(self.match['content'])

                        python = self.create_echo()
                        command = 'ECHO'

                    else:
                        python = self.create_echo()
                        command = 'ECHO'

                    if command != 'ECHO':
                        self.compiled = self.pre_escaped_new_line(self.compiled)

                    self.compiled += "\";"

                    if python != '':
                        self.compiled += "\n" + self.get_indent(self.indent) + python

                    self.indent = self.new_indent
                    self.compiled += "\n" + self.get_indent(self.indent) + "o += \""
                    i += len(self.conf.get_general('Parser', 'Postfix')) - 1

                else:

                    if (char == "\n") and (self.raw_template[i-1] == '\\'):
                        match = match[0:-1]

                    else:
                        match += char

            elif (self.raw_template[i:(i + len(self.conf.get_general('Parser', 'Prefix')))] == self.conf.get_general('Parser', 'Prefix')) and (self.raw_template[(i + len(self.conf.get_general('Parser', 'Prefix')))] != ' '):

                is_string = False
                record = False
                match = ''

                if in_raw == False:

                    i += len(self.conf.get_general('Parser', 'Prefix')) - 1

                    if self.raw_template[i+1:i+4] == 'raw':

                        in_raw = True
                        i += 4
                        self.compiled = self.pre_escaped_new_line(self.compiled)

                    else:
                        record = True

                else:

                    if self.raw_template[i+1:i+5] == '/raw':

                        i += 5
                        in_raw = False
                        self.compiled = self.pre_escaped_new_line(self.compiled)

                    else:
                        self.compiled = self.append_python_char(self.compiled, char)

            else:
                self.compiled = self.append_python_char(self.compiled, char)

            i+=1

        self.compiled = "o = \"" + self.compiled + "\"\nself.o = o"

        return self.compiled




class TplConf(object):

    """Provides a Wrapper for the template configuration.

    Be aware that you have to use reload_* if the config files have been edited after they have been loaded the first time.
    """

    def __init__(self):

        """Iniatilises some variables."""

        self.loaded_operators = False
        self.loaded_functions = False
        self.loaded_general = False


    def reload_operators(self):

        """Reloads the operator configuration."""

        self.loaded_operators = False
        self.load_operators()


    def reload_functions(self):

        """Reloads the function configuration."""

        self.loaded_functions = False
        self.load_functions()


    def reload_general(self):

        """Reloads the general configuration."""

        self.loaded_general = False
        self.load_general()


    def load_operators(self):

        """Loads the operator configuration file and parses it.

        It's format should be:
        'template_operator python_operator'
        """

        if self.loaded_operators == True:
            return

        path = os.path.join('config', 'operators.cfg')
        if not os.access(path, os.R_OK):
            raise TplFileError('Could not open "%(file)s" in read mode', path)

        f = open(path, 'r')
        data = f.read()
        f.close()

        data = data.replace('\r\n', '\n')
        data = data.replace('\r', '\n')

        lines = data.split('\n')

        translation = []
        i = 0

        for line in lines:

            if line.find(' ',1) == -1:
                raise TplGeneralError('Invalid configuration file syntax on line ' + str(i+1))

            map_from = line[0:line.find(' ',1)]
            map_to = line[line.find(' ',1)+1:]

            translation.append((map_from, map_to))

            i+=1

        self.loaded_operators = True
        self.operators = translation
        return


    def load_functions(self):

        """Loads the functions configuration file with ConfigParser and reads its data."""

        if self.loaded_functions == True:
            return

        path = os.path.join('config', 'functions.cfg')
        if not os.access(path, os.R_OK):
            raise TplFileError('Could not open "%(file)s" in read mode', path)

        Conf = ConfigParser.ConfigParser()
        Conf.read(path)

        function_names = Conf.sections()
        functions = {}

        for function in function_names:

            param_nums = Conf.options(function)
            codes = {}

            for param_num in param_nums:

                codes[param_num] = Conf.get(function, param_num)[1:-1]

            functions[function] = codes

        self.loaded_functions = True
        self.functions = functions
        return


    def load_general(self):

        """Loads the general condifguration file with ConfigParser and stores the parser in self.general"""

        if self.loaded_general == True:
            return

        path = os.path.join('config', 'general.cfg')
        if not os.access(path, os.R_OK):
            raise TplFileError('Could not open "%(file)s" in read mode', path)

        Conf = ConfigParser.ConfigParser()
        Conf.read(path)

        self.general = Conf

        return


    def get_general(self, section, option):

        """Use this function to get a general configuration option."""

        if self.loaded_general == False:
            self.load_general()

        val = self.general.get(section, option)
        if (section == 'Parser') and ((option == 'Prefix') or (option == 'Postfix')) and (val[0] == '"'):
            val = val[1:-1]

        return val


    def set_general(self, section, option, value):

        """With this function you can overwrite configuration values temporarily."""

        if self.loaded_general == False:
            self.load_general()

        return self.general.set(section, option, value)

    def get_operators(self):

        """Returns the operator translation table."""

        if self.loaded_operators == False:
            self.load_operators()

        return self.operators

    def get_function(self, name, param_num):

        """Returns a dict with all function and the python code associated with them."""

        if self.loaded_functions == False:
            self.load_functions()

        return self.functions[name][str(param_num)]




class TplBlock(object):

    """Stores all data of a Template Block and provides functionallity to interact with it.

    Normally this class should only be accessed by TplTemplate.

    The data is stored seperately for each run of the block. The number of variables and subblocks are unlimited.
    """

    def __init__(self, name):

        """Stores the block name and initialises some values."""

        self.name = name
        self.runs = {}
        self.next_element = 0
        self.length = 0;


    def assign_vars(self, vars, run = -1):

        """Assigns values to the block.

        If run is -1 a new row is inserted, otherwise the runth one is overwritten or added if it does not yet exist.
        vars should be a dict in the form {'TPL_VAR': value}
        """

        if run == -1:

            run = self.next_element
            self.next_element += 1

            if self.length < self.next_element:
                self.length = self.next_element

        else:

            if self.next_element <= run:
                self.next_element = run + 1
                self.length = self.next_element

        for name, var in vars.iteritems():

            if not self.runs.has_key(run):
                self.runs[run] = {'v': {}, 'b': {}}

            self.runs[run]['v'][name] = var

        return True


    def assign_sub_block_vars(self, blocks, vars, run = -1):

        """Assigns values to a subblock of this block.

        If run is -1 a new row is inserted, otherwise the runth one is overwritten or added if it does not yet exist.
        blocks should either be a string in th form 'subblock.subsubblock' or a dict in the form {'subblock': subrun, 'subsubblock': subsubrun}
        """

        if run == -1:
            run = self.next_element - 1

        else:

            if self.next_element < run:
                self.next_element = run
                self.length = self.next_element

        if type(blocks) == type({}):

            new_blocks = {}
            first = True

            for name, x in blocks.iteritems():

                if first:

                    block = name
                    block_run = x
                    first = False

                else:
                    new_blocks[name] = x

            if not self.runs[run]['b'].has_key(block):
                self.runs[run]['b'][block] = TplBlock(block)

            if len(new_blocks) > 0:
                return self.runs[run]['b'][block].assign_sub_block_vars(new_blocks, vars, block_run)

            else:
                return self.runs[run]['b'][block].assign_vars(vars, block_run)

        else:

            if blocks.find('.') > -1:

                block = blocks.split('.')
                blocks = blocks[(len(block[0]) + 1):]

                if not self.runs[run]['b'].has_key(block[0]):
                    self.runs[run]['b'][block] = TplBlock(block[0])

                return self.runs[run]['b'][block[0]].assign_sub_block_vars(blocks, vars)

            else:

                if not self.runs[run]['b'].has_key(blocks):
                    self.runs[run]['b'][blocks] = TplBlock(blocks)

                return self.runs[run]['b'][blocks].assign_vars(vars)

        return True


    def get_length(self):

        """Returns the number of runs this block has."""

        return self.length


    def get_block(self, x, block):

        """Returns the subblock block in the xth run."""

        if not self.runs.has_key(x):

            tmp = TplBlock(block)
            return tmp

        elif not self.runs[x]['b'].has_key(block):

            tmp = TplBlock(block)
            return tmp

        else:

            return self.runs[x]['b'][block]


    def get_recursive_block(self, x, block, depth, start):

        """Returns the depth subblock named block.

        start and depth should be integers which contain the recursion level start and end.
        x contains all iterators.
        """

        if not self.runs.has_key(x[start]):
            tmp = TplBlock(block)
            return tmp

        elif not self.runs[x[start]]['b'].has_key(block):
            tmp = TplBlock(block)
            return tmp

        else:

            tmp = self.runs[x[start]]['b'][block]
            y = start + 1

            while y < depth:

                if tmp.get_block(x[y+1], block).get_length() <= 0:
                    break;

                tmp = tmp.get_block(x[y+1], block)
                y += 1

            if (y < depth) and (y != 1):
                tmp = TplBlock(block)

            return tmp

    def get_var(self, x, var):

        """Returns the value for var in the xth run.

        If not set it returns an empty string.
        """

        if not self.runs.has_key(x):
            return ''

        elif not self.runs[x]['v'].has_key(var):
            return ''

        else:
            return self.runs[x]['v'][var]



class TplTemplate(object):

    """Provides the programming interface to Template files, stores the Template files, runtime data, manages caching and may have blocks belonging to the Template

    You can also access this class with TplEngine

    This class handles all precompiler directives.
    """

    def __init__(self, file_id, file_name, conf = False, string = False, recompile = 1):

        """Stores the given data and loads the template.

        If no cached template can be found the raw file is used and will be recompiled.
        Strings are never cached.
        """

        self.file_id = file_id
        self.file_name = file_name
        self.string = string
        self.recompile = recompile
        self.store_mode = 'raw'
        self.compiled = False
        self.vars = {}
        self.blocks = {}

        if conf == False:
            self.conf = TplConf()
        else:
            self.conf = conf

        if not string:
            loaded = False
            if (recompile == 0) or ((recompile == 1) and (self.last_change(os.path.join(self.conf.get_general('Directories', 'Cache'), self.file_name + '.py')) != 0)):
                if (recompile == 0) or ((recompile == 1) and (self.last_change(os.path.join(self.conf.get_general('Directories', 'Templates'), self.file_name)) <= self.last_change(os.path.join(self.conf.get_general('Directories', 'Cache'), self.file_name + '.py')))):
                    path = os.path.join(self.conf.get_general('Directories', 'Cache'), self.file_name + '.py')
                    loaded = os.access(path, os.R_OK)
                    self.store_mode = 'compiled'
                    self.file_path = path
                    self.compiled = True
            if not loaded:
                self.raw_template = self.load_clean_fs(file_name)
                self.store_mode = 'raw'
                self.compiled = False
        else:
            self.raw_template = file_name
        if not self.compiled:
            self.raw_template = self.pre_compile(self.raw_template)


    def last_change(self, path):

        """Returns the path's last change as a unix timestamp."""

        if not os.access(path, os.R_OK):
            return 0

        return os.stat(path).st_mtime


    def load_clean_fs(self, file_name):

        """Reads file_name and returns its contents."""

        path = os.path.join(self.conf.get_general('Directories', 'Templates'), file_name)

        if not os.access(path, os.R_OK):
            raise TplFileError('Could not open "%(file)s" in read mode', path)

        f = open(path, 'r')
        data = f.read()
        f.close()

        return data


    def write_file_fs(self, data, file_name):

        """Writes data into file_name in the Cache Directory."""

        path = os.path.join(self.conf.get_general('Directories', 'Cache'), file_name + '.py')

        if not os.access(self.conf.get_general('Directories', 'Cache'), os.W_OK):
            raise TplFileError('Can not write to cache dir "%(file)s", check the permissions', self.conf.get_general('Directories', 'Cache'))

        f = open(path, 'w+')
        f.write(data)
        f.close()


    def assign_vars(self, vars):

        """Assign top level variables.

        vars format: {'TPL_VAR': value, ...}
        """

        for name, var in vars.iteritems():
            self.vars[name] = var

        return True


    def assign_block_vars(self, blocks, vars):

        """Assigns variables to a block inside this template.

        blocks should either be a string in the form 'block.subblock.subsublock' or a dict in the form {'block': run, 'subblock': subrun, 'subsubblock': subsubrun}
        """

        if type(blocks) == type({}):

            new_blocks = {}
            first = True

            for name, run in blocks.iteritems():

                if first:

                    block = name
                    block_run = run
                    first = False

                else:
                    new_blocks[name] = run

            if not self.blocks.has_key(block):
                self.blocks[block] = TplBlock(block)

            if len(new_blocks) > 0:
                return self.blocks[block].assign_sub_block_vars(new_blocks, vars, block_run)

            else:
                return self.blocks[block].assign_vars(vars, block_run)

        else:

            if blocks.find('.') > -1:

                block = blocks.split('.')
                blocks = blocks[(len(block[0]) + 1):]

                if not self.blocks.has_key(block[0]):
                    self.blocks[block] = TplBlock(block[0])

                return self.blocks[block[0]].assign_sub_block_vars(blocks, vars)

            else:

                if not self.blocks.has_key(blocks):
                    self.blocks[blocks] = TplBlock(blocks)

                return self.blocks[blocks].assign_vars(vars)


    def get_block(self, x, block):

        """Returns the block named block (x is ignored)."""

        if not self.blocks.has_key(block):
            tmp = TplBlock(block)
            return tmp

        else:
            return self.blocks[block]


    def get_recursive_block(self, x, block, depth, start):

        """Returns the depth block named block.

        start and depth should be integers which contain the recursion level start and end.
        x contains all iterators.
        """

        if not self.blocks.has_key(block):

            tmp = TplBlock(block)
            return tmp

        else:

            tmp = self.blocks[block]
            y = start + 1

            while y < depth:

                if tmp.get_block(x[y], block).get_length() <= 0:
                    break;

                tmp = tmp.get_block(x[y], block)
                y += 1

            if y < depth:
                tmp = TplBlock(block)

            return tmp


    def get_var(self, x, var):

        """Returns the top level variable var (x is ignored).

        Returns an empty string if the variable is not set.
        """

        if not self.vars.has_key(var):
            return ''

        else:
            return self.vars[var]


    def pre_compile(self, content):

        """Parses all pre compiler statements and rempves template comments."""

        if len(content) == 0:
            return ''

        regexp = re.compile(re.escape(self.conf.get_general('Parser', 'Prefix')) + r"\*(.*?)\*" + re.escape(self.conf.get_general('Parser', 'Postfix')), re.S)

        content = regexp.sub('', content)
        regexp = re.compile(re.escape(self.conf.get_general('Parser', 'Prefix')) + r"\#(.*?)" + re.escape(self.conf.get_general('Parser', 'Postfix')), re.S)
        iterator = regexp.finditer(content)

        for match in iterator:

            pccommand = match.group(1)[:(match.group(1).find(' '))]

            if pccommand == 'INCLUDE':

                file = match.group(1)[(match.group(1).find(' '))+1:]
                content = content.replace(self.conf.get_general('Parser', 'Prefix') + '#INCLUDE ' + file + self.conf.get_general('Parser', 'Postfix'),
                    self.pre_compile(self.load_clean_fs(file)))

            else:
                raise TplCompilerError('Unknown Precompiler Command: "' + pccommand + '"', self.file_name, 'Unknown')

        return content


    def compile(self):

        """Uses the TplCompiler class to compile the code and cache it."""

        if len(self.raw_template) == 0:
            return ''

        Compiler = TplCompiler(self.conf, self.raw_template, self.file_name)
        self.compiled_template = Compiler.compile()

        if not self.string:
            self.write_file_fs(self.compiled_template, self.file_name)

        self.compiled = True


    def get_executed(self):

        """Compiles the raw_template if there was no cached version and executes the generated code."""

        if not self.compiled:

            self.compile()

        x = [0]

        if not self.string:
            execfile(os.path.join(self.conf.get_general('Directories', 'Cache'), self.file_name + '.py'))

        else:
            eval(self.compiled_template)

        return self.o


class TplEngine(object):

    """Provides an interface to manage all templates, highlighting and cache management."""

    def __init__(self, defaults = {}, recompile = 1):

        """Stores the given arguments and initialises the class."""

        self.recompile = recompile;
        self.templates = {};
        self.default_vars = defaults;
        self.highlight_strings = [];
        self.conf = TplConf()
        return


    def set_defaults(self, vars):

        """Set default vars for all templates used with this object."""

        self.default_vars = vars


    def get_defaults(self):

        """Get the default variables assigned to this object."""

        return self.default_vars


    def assign_vars(self, file_id, vars):

        """Uses TplTemplate.assign_vars, file_id specifies the template."""

        if not self.templates.has_key(file_id):
            raise TplFileError('File id "%(file)s" is not registered', file_id)

        return self.templates[file_id].assign_vars(vars)


    def assign_block_vars(self, file_id, blocks, vars):

        """Uses TplTemplate.assign_block_vars, file_id specifies the template."""

        if not self.templates.has_key(file_id):
            raise TplFileError('File id "%(file)s" is not registered', file_id)

        return self.templates[file_id].assign_block_vars(blocks, vars)


    def register_file(self, file_id, file_name, string = False):

        """Creates a new TplTemplate object and stores it in self.templates."""

        self.templates[file_id] = TplTemplate(file_id,
                                              file_name,
                                              self.conf,
                                              string,
                                              self.recompile)
        self.register_defaults(file_id)
        return True


    def register_string(self, string_id, string):

        """Use this function to compile a string instead of a template file."""

        self.register_file(string_id, string, True)

    def get_executed(self, file_id):

        """Returns the output of file_id with all variables filled in."""

        if not self.templates.has_key(file_id):
            raise TplFileError('File id "%(file)s" is not registered', file_id)

        parsed = self.templates[file_id].get_executed()

        del self.templates[file_id]

        return parsed


    def register_defaults(self, file_id):

        """Assigns the default variables for the template specified by file_id."""

        if not self.templates.has_key(file_id):
            raise TplFileError('File id "%(file)s" is not registered', file_id)

        self.assign_vars(file_id, self.default_vars)


    def delete_cached_files(self):

        """Deletes all cached template files."""

        files = os.listdir(self.conf.get_general('Directories', 'Cache'))

        for file in files:

            path = os.path.join(self.conf.get_general('Directories', 'Cache'), file)

            if os.access(path, os.W_OK):

                try:
                    os.unlink(path)

                except OSError:
                    pass


    def delete_cached_file(self, file):

        """Deletes a single cached file."""

        if os.access(path, os.W_OK):
            os.unlink(os.path.join(self.conf.get_general('Directories', 'Cache'), file))


    def add_highlight_string(self, string):

        """Adds a string which shall be highlighted by TplEngine.highlight"""

        self.highlight_strings.append(string)


    def add_highlight_strings(self, strings):

        """Adds multiple strings which shall be highlighted by TplEngine.highlight"""

        for string in strings:
            self.highlight_strings.append(string)


    def remove_highlight_string(self, string):

        """Removes a string which shall not be highlighted by TplEngine.highlight"""

        self.highlight_strings.remove(string)


    def remove_highlight_strings(self, strings):

        """Removes multiple strings which shall not be highlighted by TplEngine.highlight"""

        for string in strings:
            self.remove_highlight_string(string)


    def set_highlight_replacement(self, string):

        """Overwrites the ReplacePattern from general.cfg which is used to highlight the specified strings."""

        self.conf.set_general('Highlighting', 'ReplacePattern', string)


    def highlight(self, html):

        """Highlights all strings in self.highlight_strings in the code specified in html."""

        if len(self.highlight_strings) > 0:

            pattern = r"(?!(<|<script[^\ ]|<style[^\ ]*>).*?)(%(search)s)(?![^<>]*?(</style>|</script>|>))"
            flags = re.S | re.I

            for string in self.highlight_strings:

                string = re.escape(string)

                if self.conf.get_general('Highlighting', 'CompleteWords'):
                    string = r"\b[^ >]*" + string + r"[^ <]*\b"

                regexp = pattern % {'search': string}

                m = re.compile(regexp, flags)
                html = m.sub(self.conf.get_general('Highlighting', 'ReplacePattern')[1:-1], html)

        return html

