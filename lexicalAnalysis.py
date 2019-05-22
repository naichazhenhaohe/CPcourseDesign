from pprint import pprint

# 词法分析器

class Lexical_Analyzer:
    token = ''
    string = ''
    index = 0
    is_end = False
    ch = ''
    error_type = ''
    one_op = ['+', '-', ',', '*', '%', '/', ';',
              '(', ')', "'", '"', ' ', '\n', '.', '{', '}', '[', ']', '`', '#']
    not_print = [' ', '\n']
    reserved = ['char', 'int', 'float', 'break', 'const', 'return', 'void',
                'return', 'void', 'continue', 'do', 'while', 'if', 'else', 'for']
    two_next = {
        '<': ['='],
        '>': ['='],
        '=': ['='],
        '!': ['='],
        '|': ['|'],
        '&': ['&'],
    }
    token_to_category = {word: word.upper() for word in reserved}
    # token_to_category['>'] = '213'
    # token_to_category['<'] = '211'
    # token_to_category['>='] = '214'
    # token_to_category['<='] = '212'
    # token_to_category['=='] = '215'
    # token_to_category['='] = '219'
    # token_to_category['!='] = '216'
    # token_to_category[';'] = '303'
    # token_to_category['#'] = 'HASH'
    # token_to_category['+'] = '209'
    # token_to_category['.'] = '220'
    # token_to_category['-'] = '210'
    # token_to_category['!'] = '205'
    # token_to_category['*'] = '206'
    # token_to_category['/'] = '207'
    # token_to_category['&&'] = '217'
    # token_to_category['||'] = '218'
    # token_to_category['%'] = '208'
    # token_to_category[','] = '304'
    # token_to_category['('] = '201'
    # token_to_category[')'] = '202'
    # token_to_category['['] = '203'
    # token_to_category[']'] = '204'
    # token_to_category['{'] = '301'
    # token_to_category['}'] = '302'
    # token_to_category['`'] = 'ACCENT'
    # token_to_category["'"] = 'QUO'
    # token_to_category['"'] = 'DQUO'
    # token_to_category[' '] = 'BLANK'
    # token_to_category['\n'] = 'ENTER'

    #由于在后续的文法的编写中，未使用编码，由此token串的标识使用符号本身。
    token_to_category['>'] = '>'
    token_to_category['<'] = '<'
    token_to_category['>='] = '>='
    token_to_category['<='] = '<='
    token_to_category['=='] = '=='
    token_to_category['='] = '='
    token_to_category['!='] = '!='
    token_to_category[';'] = ';'
    token_to_category['#'] = '#'
    token_to_category['+'] = '+'
    token_to_category['.'] = '.'
    token_to_category['-'] = '-'
    token_to_category['!'] = '!'
    token_to_category['*'] = '*'
    token_to_category['/'] = '/'
    token_to_category['&&'] = '&&'
    token_to_category['||'] = '||'
    token_to_category['%'] = '%'
    token_to_category[','] = ','
    token_to_category['('] = '('
    token_to_category[')'] = ')'
    token_to_category['['] = '['
    token_to_category[']'] = ']'
    token_to_category['{'] = '{'
    token_to_category['}'] = '}'
    token_to_category['`'] = '`'
    token_to_category["'"] = "'"
    token_to_category['"'] = '"'
    token_to_category[' '] = 'BLANK'
    token_to_category['\n'] = 'ENTER'
    def __init__(self, string=''):
        self.string = string
        self.res = []

    def lookup(self):
        return True if self.token in self.reserved else False

    def out(self, c=''):
        if c == '':
            if self.token in self.token_to_category.keys():
                if self.token not in self.not_print:
                    self.res.append(
                        [self.token_to_category[self.token], self.token])
                else:
                    pass
            else:
                self.error_type = "unkown terminal character '%s'" % self.token
                self.report_error()
        else:
            if c == 'NOTE':
                pass
            else:
                self.res.append([c, self.token])

        self.token = ''

    def get_char(self):
        if self.is_end:
            return False

        self.ch = self.string[self.index]
        self.token += self.ch
        self.index += 1
        if self.index == len(self.string):
            self.is_end = True
        return self.ch

    def retract(self):
        self.is_end = False
        self.index = max(self.index - 1, 0)
        self.ch = self.string[max(self.index - 1, 0)]
        self.token = self.token[:-1]

    def alpha(self):
        while not self.is_end and self.string[self.index].isalnum() and self.get_char():
            pass

        self.out('' if self.lookup() else 'ID')

    def digit(self):
        while not self.is_end and (self.string[self.index].isdigit() or self.string[self.index] == '.' or self.string[self.index] == 'e' or self.string[self.index] == 'E') and self.get_char():
            pass
            # if (self.string[self.index] == '.'):
            #     mark = True
        #     else: 
        #         pass
        # if mark == False:
        #     self.out('int_DIGITAL')
        # else:
        #     self.out('float_DIGITAL')
        self.out("DIGITAL")

    def one(self):
        self.out()

    def two(self):
        now_ch = self.ch
        if self.get_char() in self.two_next[now_ch]:
            self.out()
        else:
            self.retract()
            self.out()

    def back_slant(self):
        self.get_char()
        if self.ch == '*':
            try:
                end_index = self.string.index('*/', self.index)
            except:
                self.error_type = "no pair with '*/'"
                self.report_error()
            self.token = self.token + self.string[self.index:end_index] + '*/'
            self.ch = self.string[end_index + 1]
            if end_index + 2 < len(self.string):
                self.index = end_index + 2
            else:
                self.is_end = True
            self.out('NOTE')
        elif self.ch == '/':
            end_index = self.string.index('\n', self.index)
            self.token = self.token + self.string[self.index:end_index] + '\n'
            self.ch = self.string[end_index]
            if end_index + 1 < len(self.string):
                self.index = end_index + 1
            else:
                self.is_end = True
            self.out('NOTE')
        else:
            self.retract()
            self.out()

    def report_error(self):
        exit('[error]index %s: %s' % (self.index, self.error_type))

    switch = {
        'alpha': alpha, 'digit': digit,  'one': one,  'two': two,
        '/': back_slant,  '': report_error,
    }

    def analyse(self):
        while self.get_char():
            if self.ch.isalpha():
                case = 'alpha'
            elif self.ch.isdigit():
                case = 'digit'
            elif self.ch == '/':
                case = '/'
            elif self.ch in self.one_op:
                case = 'one'
            elif self.ch in self.two_next.keys():
                case = 'two'
            else:
                self.error_type = "unkown character '%s'" % self.ch
                case = ''
            self.switch[case](self)
        return self.res
