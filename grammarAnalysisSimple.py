from lexicalAnalysis import Lexical_Analyzer
from pprint import pprint
from copy import deepcopy


import sys

# 递归下降分析器
# self.Ari_Semantic()、self.Boo_Semantic()、self.if_Semantic()分别为生成算术表达式、布尔表达式、if语句的四元式
# 以上三方法在slef.analyse()中调用

class Analyzer:
    def __init__(self, start, terminal, production):
        self.start = start
        self.terminal = terminal
        self.nonterminal = production.keys()
        self.production = production
        #递归下降分析法
        self.first = {nonterminal: set() for nonterminal in self.nonterminal}
        # 预测分析法
        # self.first = {nonterminal: {} for nonterminal in self.nonterminal}
        self.follow = {nonterminal: set() for nonterminal in self.nonterminal}
        self.symbolTable = []
        self.get_first()
        pprint(self.first)
        print('-----------')
        self.get_follow()
        pprint(self.follow)
        self.T = 0
        self.code = []

    def handle_get_first(self, nonterminal):
        for right in self.production[nonterminal]:
            for item in right:
                if item in self.terminal:
                    break
                if item in self.nonterminal:
                    self.first[nonterminal].update(self.first[item])
                    if ('ε' not in self.first[item]):
                        break

    def get_first(self):
        # S->aL First[S].add(a)
        for nonterminal in self.nonterminal:
            for right in self.production[nonterminal]:
                if(right[0] in self.terminal):
                    self.first[nonterminal].add(right[0])
        # pprint(self.first)
        # S->LMα First[S].add(First[L]) 若ε属于First[L], First[S].add(First[M]) ...直到First[S]不再增加
        while True:
            old_first = deepcopy(self.first)
            for nonterminal in self.nonterminal:
                self.handle_get_first(nonterminal)
            if old_first == self.first:
                break

    def get_follow(self):
        self.follow[self.start].add('#')
        while True:
            # old_follow和old_first用于判断是否已经不再更新
            old_follow = deepcopy(self.follow)
            for nonterminal in self.nonterminal:
                for right in self.production[nonterminal]:
                    for index, content in enumerate(right):
                        if content in self.terminal:
                            # 若该符号为终结符，则跳过
                            continue
                        if index == len(right) - 1:
                            # S->αL ,follow[L] |= follow[S]
                            self.follow[content] |= self.follow[nonterminal]
                        elif right[index+1] in self.terminal:
                            # S->La ,follow[L].add(a)
                            self.follow[content].add(right[index+1])
                        else:
                            # S->LB ,follow[L] |= first[B]/ε
                            a = {key for key in self.first[right[index + 1]]}
                            temp = {
                                key for key in self.first[right[index + 1]] if key != 'ε'}
                            self.follow[content] |= temp
                            if 'ε' in a:
                                self.follow[content] |= self.follow[nonterminal]
            if old_follow == self.follow:
                break

    def AriExp(self):
        self.AriItem()
        self.AriExp_foo()

    # 'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']]
    def AriExp_foo(self):
        if self.token_list[self.index][0] == '+' or self.token_list[self.index][0] == '-':
            self.index += 1
            self.AriExp()

    def AriItem(self):
        self.AriFactor()
        self.AriItem_foo()

    # 'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['%', 'AriItem'], ['ε']],
    def AriItem_foo(self):
        if self.token_list[self.index][0] == '*' or self.token_list[self.index][0] == '/' or self.token_list[self.index][0] == '%':
            self.index += 1
            self.AriItem()

    # 'AriFactor': [['(', 'AriExp', ')'], ['ID'], ['DIGITAL']],
    def AriFactor(self):
        if self.token_list[self.index][0] == '(':
            self.index += 1
            self.AriExp()
            if self.token_list[self.index][0] == ')':
                self.index += 1
            else:
                print(self.string[:-1] + ' 语法错误，缺少 ) ')
                sys.exit()
        elif self.token_list[self.index][0] == 'ID':
            self.index += 1
            if self.token_list[self.index][0] == 'ID' or self.token_list[self.index][0] == '(':
                print(self.string[:-1] + ' 语法错误，下标' +
                      str(self.index) + '处缺少算术运算符')
                sys.exit()
        elif self.token_list[self.index][0] == 'DIGITAL':
            self.index += 1
        else:
            print(self.string[:-1] + ' 语法错误，下标' +
                  str(self.index) + '处缺少算术运算对象')
            sys.exit()

    # 'BooExp': [['BooItem', 'BooExp_foo']],
    def BooExp(self):
        self.BooItem()
        self.BooExp_foo()

    # 'BooExp_foo': [['||', 'BooExp'], ['ε']],
    def BooExp_foo(self):
        if self.token_list[self.index][0] == '||':
            self.index += 1
            self.BooExp()

    # 'BooItem': [['BooFactor', 'BooItem_foo']],
    def BooItem(self):
        self.BooFactor()
        self.BooItem_foo()

    # 'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    def BooItem_foo(self):
        if self.token_list[self.index][0] == '&&':
            self.index += 1
            self.BooItem()

    # 'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    def BooFactor(self):
        if self.token_list[self.index][0] == '!':
            self.index += 1
            self.BooExp()
        else:
            self.AriExp()
            self.BooFactor_foo()

    # 'BooFactor_foo': [['RelExp', 'AriExp'], ['ε']],
    def BooFactor_foo(self):
        if self.token_list[self.index][0] in self.first['BooFactor_foo']:
            self.RelOperator()
            self.AriExp()

    # 'RelOperator': [['>'], ['<'], ['<='], ['>='], ['=='], ['!=']],
    def RelOperator(self):
        operators = ['<=', '>=', '<', '>', '==', '!=']
        if self.token_list[self.index][1] in operators:
            self.index += 1
        else:
            print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处缺少布尔运算符')
            sys.exit()

    def Exp(self):
        self.BooExp()
        self.Exp_foo()

    def Exp_foo(self):
        if self.token_list[self.index][0] == '=':
            self.index += 1
            self.Exp()

    # 'Sta': [['DecSta'], ['ExeSta']],
    def Sta(self):
        if self.token_list[self.index][0] in self.first['DecSta']:
            self.DecSta()
        elif self.token_list[self.index][0] in self.first['ExeSta']:
            self.ExeSta()
        else:
            print('err')
            sys.exit()

    # 'DecSta': [['CONST', 'Type', 'ID', 'DecSta_foo'], ['Type', 'ID', 'DecSta_foo']],
    def DecSta(self):
        if self.token_list[self.index][0] == 'CONST':
            self.index += 1
            self.Type()
            if self.token_list[self.index][0] == 'ID':
                self.index += 1
                self.DecSta_foo()
            else:
                print(self.string[:-1] + ' 语法错误，下标' +
                      str(self.index) + '处缺少标识符')
                sys.exit()
        elif self.token_list[self.index][0] in self.first['Type']:
            self.Type()
            if self.token_list[self.index][0] == 'ID':
                self.index += 1
                self.DecSta_foo()
        else:
            print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处赋值语句错误')
            sys.exit()

    # 'DecSta_foo': [['SingleParDecTable_foo', 'ParDecTable_foo']],
    def DecSta_foo(self):
        self.SingleParDecTable_foo()
        self.ParDecTable_foo()

    # 'ParDecTable': [['SingleParDecTable', 'ParDecTable_foo']],
    def ParDecTable(self):
        self.SingleParDecTable()
        self.ParDecTable_foo()

    # 'ParDecTable_foo': [[';'],[',', 'ParDecTable']],
    def ParDecTable_foo(self):
        if self.token_list[self.index][0] == ';':
            self.index += 1
        elif self.token_list[self.index][0] == ',':
            self.index += 1
            self.ParDecTable()
        else:
            print(self.string[:-1] + ' 语法错误，下标' +
                  str(self.index) + '处缺少 ; 或 ,')
            sys.exit()

    # 'SingleParDecTable': [['ID', 'SingleParDecTable_foo']],
    def SingleParDecTable(self):
        if self.token_list[self.index][0] == 'ID':
            self.index += 1
            self.SingleParDecTable_foo()

    # 'SingleParDecTable_foo': [['=', 'Exp'], ['ε']],
    def SingleParDecTable_foo(self):
        if self.token_list[self.index][0] == '=':
            self.index += 1
            self.Exp()

    # 'Type': [['INT'], ['CHAR'], ['FLOAT']],
    def Type(self):
        if self.token_list[self.index][0] == 'INT':
            self.index += 1
        elif self.token_list[self.index][0] == 'CHAR':
            self.index += 1
        elif self.token_list[self.index][0] == 'FLOAT':
            self.index += 1
        else:
            print(self.string[:-1] + ' 语法错误，下标' +
                  str(self.index) + '处错误的变/常量类型')
            sys.exit()

    # 'ExeSta': [['if_Sta'], ['ComSta'], ['DataProSta']],
    def ExeSta(self):
        if self.token_list[self.index][0] in self.first['if_Sta']:
            self.if_Sta()
        elif self.token_list[self.index][0] in self.first['ComSta']:
            self.ComSta()
        elif self.token_list[self.index][0] in self.first['DataProSta']:
            self.DataProSta()

    # 'DataProSta': [['ID', 'DataProSta_foo']],
    def DataProSta(self):
        if self.token_list[self.index][0] == 'ID':
            self.index += 1
            self.DataProSta_foo()
        else:
            print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处错缺少标识符')
            sys.exit()
    # 'DataProSta_foo': [['=', 'Exp', ';']],

    def DataProSta_foo(self):
        if self.token_list[self.index][0] == '=':
            self.index += 1
            self.Exp()
            if self.token_list[self.index][0] == ';':
                self.index += 1
            else:
                print(self.string[:-1] + ' 语法错误，下标' +
                      str(self.index) + '处缺少 ;')
                sys.exit()
        else:
            print(self.string[:-1] + ' 语法错误，下标' + str(self.index) + '处缺少 = ')
            sys.exit()

    # 'ComSta': [['{', 'StaTable', '}']],
    def ComSta(self):
        if self.token_list[self.index][0] == '{':
            self.index += 1
            self.StaTable()
            if self.token_list[self.index][0] == '}':
                self.index += 1
            else:
                # print(self.token_list[self.index])
                print(self.string[:-1] + ' 语法错误，下标' +
                      str(self.index) + '处缺少对应的 } -286')
                sys.exit()
        else:
            print(self.string[:-1] + ' 语法错误，下标' +
                  str(self.index) + '处缺少 { -289')
            sys.exit()

    # 'StaTable': [['Sta', 'StaTable_foo']],
    def StaTable(self):
        self.Sta()
        self.StaTable_foo()

    # 'StaTable_foo': [['StaTable'], ['ε']],
    def StaTable_foo(self):
        if self.token_list[self.index][0] in self.first['StaTable']:
            self.StaTable()

    # 'if_Sta': [['if', '(', 'BooExp', ')', 'Sta', 'if_Sta_foo']],
    def if_Sta(self):
        # print('----------')
        # print(self.token_list[self.index])
        # print('----------')
        if self.token_list[self.index][0] == 'IF':
            self.index += 1
            # print(self.token_list[self.index])
            if self.token_list[self.index][0] == '(':
                self.index += 1
                self.BooExp()
                # print(self.index)
                if self.token_list[self.index][0] == ')':
                    self.index += 1
                    self.Sta()
                    self.if_Sta_foo()
                else:
                    print(self.string[:-1] + ' 语法错误，下标' +
                          str(self.index) + '处缺少对应 ) ')
                    sys.exit()
            else:
                print(self.string[:-1] + ' 语法错误，下标' +
                      str(self.index) + '处if关键词后缺少 (')
                sys.exit()
        else:
            print(self.string[:-1] + ' 语法错误，下标' +
                  str(self.index) + '处无法找到if关键字')
            sys.exit()

    # 'if_Sta_foo': [['else', 'Sta'], ['ε']]
    def if_Sta_foo(self):
        if self.token_list[self.index][0] == 'ELSE':
            self.index += 1
            self.Sta()

    def delimiter_check(self):
        marks = ['(', ')', '[', ']', '{', '}', "'", '"', '`']
        mark_num = {mark: 0 for mark in marks}
        for item in self.token_list:
            if item[0] == '(':
                mark_num['('] += 1
            elif item[0] == ')':
                mark_num[')'] += 1
            elif item[0] == '[':
                mark_num['['] += 1
            elif item[0] == ']':
                mark_num[']'] += 1
            elif item[0] == '{':
                mark_num['{'] += 1
            elif item[0] == '}':
                mark_num['}'] += 1
            elif item[0] == '`':
                mark_num['`'] += 1
            elif item[0] == "'":
                mark_num["'"] += 1
            elif item[0] == '"':
                mark_num['"'] += 1
        if mark_num['('] > mark_num[')']:
            print(self.string[:-1] + ' 语法错误，缺少 ) ')
            sys.exit()
        elif mark_num[')'] > mark_num['(']:
            print(self.string[:-1] + ' 语法错误，缺少 ( ')
            sys.exit()

        if mark_num['['] > mark_num[']']:
            print(self.string[:-1] + ' 语法错误，缺少 ] ')
            sys.exit()
        elif mark_num[']'] > mark_num['[']:
            print(self.string[:-1] + ' 语法错误，缺少 [ ')
            sys.exit()

        if mark_num['{'] > mark_num['}']:
            print(self.string[:-1] + ' 语法错误，缺少 } ')
            sys.exit()
        elif mark_num['}'] > mark_num['{']:
            print(self.string[:-1] + ' 语法错误，缺少 { ')
            sys.exit()

        if mark_num['`'] % 2 == 1 and mark_num['`'] != 0:
            print(self.string[:-1] + ' 语法错误，出現奇数个 ` ')
            sys.exit()
        if mark_num["'"] % 2 == 1 and mark_num["'"] != 0:
            print(self.string[:-1] + " 语法错误，出現奇数个 ' ")
            sys.exit()
        if mark_num['"'] % 2 == 1 and mark_num['"'] != 0:
            print(self.string[:-1] + ' 语法错误，出現奇数个 " ')
            sys.exit()

    def analyse(self, res):
        res.append(['HASH', '#'])
        self.token_list = res
        self.string = ''
        for item in res:
            self.string += item[1]
        self.index = 0
        pprint(self.token_list)
        self.delimiter_check()
        if self.start == 'AriExp':
            self.AriExp()
        elif self.start == 'BooExp':
            self.BooExp()
        elif self.start == 'Exp':
            self.Exp()
        elif self.start == 'if_Sta':
            self.if_Sta()
        elif self.start == 'Sta':
            self.Sta()
        print('======判断结果======')
        pprint(self.string[:-1] + " OK!")
        # self.Ari_Semantic()
        # self.Boo_Semantic()
        self.if_Semantic()
        self.getSymbolTable()

    def Boo_Semantic(self, token_list=[]):
        operators = {'!': 3, '&&': 1, '==': 2,
                     '>': 2, '<': 2, '>=': 2, '<=': 2, '||': 0}
        char = []
        symbol = []
        top_char = 0
        top_symbol = 0

        if len(token_list) != 0:
            token_list = token_list
        else:
            token_list = self.token_list[:-1]
        for item in token_list:
            if item[0] not in operators.keys() and item[0] != '(' and item[0] != ')':
                if top_symbol != 0 and symbol[top_symbol - 1] == '!':
                    pop_symbol = symbol.pop()
                    self.code.append(
                        [pop_symbol, item[1], '_', 'T'+str(self.T)])
                    top_symbol -= 1
                    char.append('T'+str(self.T))
                    top_char += 1
                    self.T += 1
                else:
                    char.append(item[1])
                    top_char += 1
            elif item[0] in operators.keys() and len(symbol) == 0:
                symbol.append(item[1])
                top_symbol += 1
            elif item[0] == '(':
                symbol.append(item[1])
                top_symbol += 1
            elif item[0] == ')':
                while symbol[top_symbol-1] != '(':
                    first = char.pop()
                    second = char.pop()
                    pop_symbol = symbol.pop()
                    self.code.append(
                        [pop_symbol, second, first, 'T'+str(self.T)])
                    top_symbol -= 1
                    char.append('T'+str(self.T))
                    top_char -= 1
                    self.T += 1
                symbol.pop()
                top_symbol -= 1
            elif item[1] in operators.keys() and operators[item[1]] > operators[symbol[top_symbol - 1]]:
                symbol.append(item[1])
                top_symbol += 1
            elif item[1] in operators.keys() and operators[item[1]] <= operators[symbol[top_symbol - 1]]:
                first = char.pop()
                second = char.pop()
                pop_symbol = symbol.pop()
                self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
                char.append('T'+str(self.T))
                top_char -= 1
                symbol.append(item[1])
                self.T += 1

        while len(symbol) != 0:
            first = char.pop()
            second = char.pop()
            pop_symbol = symbol.pop()
            self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
            top_symbol -= 1
            char.append('T'+str(self.T))
            top_char -= 1
            self.T += 1
        # pprint(self.code)

    def if_Semantic(self):
        for index, content in enumerate(self.token_list[:-1]):
            if content[0] == '(':
                mark = 0
                end = 0
                while True:
                    if self.token_list[index+mark][0] == ')':
                        end = index+mark
                        break
                    mark += 1
                self.Boo_Semantic(token_list=self.token_list[index+1:end])
                # print(self.code, self.T)
                # print(self.token_list[index+1:end])
                self.code.append(['jnz', 'T'+str(self.T-1), '_', len(self.code)+2])
                self.code.append(['j', '_', '_', 0])
                self.nxq_f = len(self.code)
                # pprint('f'+str(len(self.code)))
            if content[0] == '{' and self.token_list[index-1][0] == ')':
                mark = 0
                while True:
                    if self.token_list[index+mark][0] == '}':
                        end = index+mark
                        break
                    mark += 1
                for i in self.cut(token_list=self.token_list[index+1:end]):
                    self.Ari_Semantic(token_list=i)
            if content[0] == '{' and self.token_list[index-1][0] == 'ELSE':
                self.code[self.nxq_f-1][3] = len(self.code)
                mark = 0
                while True:
                    if self.token_list[index+mark][0] == '}':
                        end = index+mark
                        break
                    mark += 1
                for i in self.cut(token_list=self.token_list[index+1:end]):
                    self.Ari_Semantic(token_list=i)
        pprint(self.code)

    def cut(self, token_list):
        res = []
        temp = []
        for i in token_list:
            if i[0] != ';':
                temp.append(i)
            else:
                res.append(temp)
                temp = []
        # pprint(res)
        return res

    def Ari_Semantic(self, token_list=[]):
        operators = {'+': 0, '-': 0, '*': 1, '/': 1,
                     '%': 1, ')': -1, '(': -1, '=': -1}
        type_list = ['INT', 'CHAR', 'FLOAT']
        char = []
        symbol = []
        top_char = 0
        top_symbol = 0

        if len(token_list) != 0:
            token_list = token_list
        else:
            token_list = self.token_list
        for item in token_list:
            if item[0] in type_list:
                pass
            if item[1] not in operators.keys() and item[1] != ')' and item[1] != '(':
                char.append(item[1])
                top_char += 1
            elif item[1] in operators.keys() and len(symbol) == 0:
                symbol.append(item[1])
                top_symbol += 1
            elif item[1] == '(':
                symbol.append(item[1])
                top_symbol += 1
            elif item[1] == ')':
                while symbol[top_symbol-1] != '(':
                    first = char.pop()
                    second = char.pop()
                    pop_symbol = symbol.pop()
                    self.code.append(
                        [pop_symbol, second, first, 'T'+str(self.T)])
                    top_symbol -= 1
                    char.append('T'+str(self.T))
                    top_char -= 1
                    self.T += 1
                symbol.pop()
                top_symbol -= 1
            elif item[1] in operators.keys() and operators[item[1]] > operators[symbol[top_symbol - 1]]:
                symbol.append(item[1])
                top_symbol += 1
            elif item[1] in operators.keys() and operators[item[1]] <= operators[symbol[top_symbol - 1]]:
                first = char.pop()
                second = char.pop()
                pop_symbol = symbol.pop()
                self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
                char.append('T'+str(self.T))
                top_char -= 1
                symbol.append(item[1])
                self.T += 1

        while len(symbol) != 0:
            first = char.pop()
            second = char.pop()
            pop_symbol = symbol.pop()
            self.code.append([pop_symbol, second, first, 'T'+str(self.T)])
            top_symbol -= 1
            char.append('T'+str(self.T))
            top_char -= 1
            self.T += 1
        # pprint(self.code)

    def getSymbolTable(self):
        mark = 0
        type_list = ['INT', 'CHAR', 'FLOAT']
        for index, content in enumerate(self.token_list):
            if content[0] in type_list:
                temp = []
                temp.append(mark)
                mark += 1
                temp.append(self.token_list[index+1][1])
                temp.append(content[0])
                if self.token_list[index+2][0] == '=':
                    value = ''
                    foo = 3
                    while True:
                        if self.token_list[index+foo][1] != ';':
                            value += self.token_list[index+foo][1]
                            foo += 1
                        else:
                            break
                    temp.append(value)

                else:
                    temp.append('')
                self.symbolTable.append(temp)
        print('======符号表======')
        pprint(self.symbolTable)


terminal = ['+', '-', '*', '/', '%', 'ε', '!', '=', 'IF', 'ELSE', ':', ';', ',', 'INT', 'CHAR', 'FLOAT',
            '{', '}', '(', ')', 'ID', 'CONST', '||', '&&', '<', '>', '>=', '<=', '==', '!=', 'DIGITAL']

production = {
    'AriExp': [['AriItem', 'AriExp_foo']],
    'AriExp_foo': [['+', 'AriExp'], ['-', 'AriExp'], ['ε']],
    'AriItem': [['AriFactor', 'AriItem_foo']],
    'AriItem_foo': [['*', 'AriItem'], ['/', 'AriItem'], ['%', 'AriItem'], ['ε']],
    'AriFactor': [['(', 'AriExp', ')'], ['ID'], ['DIGITAL']],

    'BooExp': [['BooItem', 'BooExp_foo']],
    'BooExp_foo': [['||', 'BooExp'], ['ε']],
    'BooItem': [['BooFactor', 'BooItem_foo']],
    'BooItem_foo': [['&&', 'BooItem'], ['ε']],
    'BooFactor': [['!', 'BooExp'], ['AriExp', 'BooFactor_foo']],
    'BooFactor_foo': [['RelOperator', 'AriExp'], ['ε']],

    'RelOperator': [['>'], ['<'], ['<='], ['>='], ['=='], ['!=']],

    'Exp': [['BooExp', 'Exp_foo']],
    'Exp_foo': [['=', 'Exp'], ['ε']],

    'Sta': [['DecSta'], ['ExeSta']],

    'DecSta': [['CONST', 'Type', 'ID', 'DecSta_foo'], ['Type', 'ID', 'DecSta_foo']],
    'DecSta_foo': [['SingleParDecTable_foo', 'ParDecTable_foo']],
    'ParDecTable': [['SingleParDecTable', 'ParDecTable_foo']],
    'ParDecTable_foo': [[';'], [',', 'ParDecTable']],
    'SingleParDecTable': [['ID', 'SingleParDecTable_foo']],
    'SingleParDecTable_foo': [['=', 'Exp'], ['ε']],

    'Type': [['INT'], ['CHAR'], ['FLOAT']],

    'ExeSta': [['if_Sta'], ['ComSta'], ['DataProSta']],

    'DataProSta': [['ID', 'DataProSta_foo']],
    'DataProSta_foo': [['=', 'Exp', ';']],

    'ComSta': [['{', 'StaTable', '}']],
    'StaTable': [['Sta', 'StaTable_foo']],
    'StaTable_foo': [['StaTable'], ['ε']],

    'if_Sta': [['IF', '(', 'BooExp', ')', 'Sta', 'if_Sta_foo']],
    'if_Sta_foo': [['ELSE', 'Sta'], ['ε']]
}
source_string = 'if(a>b&& temp||a){ a = b*(c-d+f*(g+h-i/b)+ k);}else{int c=10;int demo=11;}'
# source_string = 'if (a>0) {a = a+b+c;b = 1;c = a+b*c;}'
# source_string='b*(c-d+f*(g+h-i/j+k))'
# source_string = '''
#     {
#       //sajdfkljsd
#     ~
#     }'''
# source_string = '!a>=demo||temp&&!index'
# source_string = 'a>b'
# source_string = 'a>b&&temp||a'

res = Lexical_Analyzer(source_string).analyse()
# starter = 'if_Sta'
# starter = 'Exp'
# starter = 'AriExp'
# starter = 'BooExp'
starter = 'Sta'

analyzer = Analyzer(starter, terminal, production)
pprint('----詞法分析----')
pprint(res)
analyzer.analyse(res=res)
