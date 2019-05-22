from lexicalAnalysis import Lexical_Analyzer
from pprint import pprint
from copy import deepcopy

import sys


class Analyzer:
    def __init__(self, start, terminal, production):
        self.start = start
        self.terminal = terminal
        self.nonterminal = production.keys()
        self.production = production
        self.first = {nonterminal: {} for nonterminal in self.nonterminal}
        self.follow = {nonterminal: set() for nonterminal in self.nonterminal}
        self.stark = []
        self.get_first()
        pprint(self.first)
        print('-----------')
        self.get_follow()
        self.getPreTable()
        pprint(self.follow)
        print('-----------')
        pprint(self.PreTable)

    def handle_get_first(self, nonterminal):
        for right in self.production[nonterminal]:
            for item in right:
                if item in self.terminal:
                    break
                if item in self.nonterminal:
                    for i in self.first[item]:
                        if i in self.first[nonterminal].keys():
                            pass
                        else:
                            self.first[nonterminal][i] = right
                    if ('ε' not in self.first[item]):
                        break

    # 在建立first集同时获得预测分析表
    def get_first(self):
        # S->aL First[S].add(a)
        for nonterminal in self.nonterminal:
            for right in self.production[nonterminal]:
                if(right[0] in self.terminal):
                    self.first[nonterminal][right[0]] = right
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

    def analyse(self, res):
        res.append(['#', '#'])
        self.stark.append('#')
        pprint(res)
        self.token_list = res
        self.stark.append(self.start)
        self.index = 0
        self.string = ''
        for item in res:
            self.string += item[1]
        while True:
            self.current = self.stark.pop()
            print('当前x为：'+self.current)
            if self.current == '#':
                if self.current == self.token_list[self.index][0]:
                    print(self.string + ' OK!')
                    break
                else:
                    print(str(self.index) + '处err-0')
                    sys.exit()
            elif self.current in self.terminal:
                if self.current == self.token_list[self.index][0]:
                    print('匹配成功'+self.token_list[self.index][0])
                    self.index += 1
            elif self.current in self.nonterminal:
                pprint(self.PreTable[self.current])
                print(self.index)
                if self.token_list[self.index][0] not in self.PreTable[self.current].keys():
                    print([self.token_list[self.index][0]])
                    print(str(self.index) + '处err-1')
                    sys.exit()
                else:
                    if self.PreTable[self.current][self.token_list[self.index][0]][0] != 'ε':
                        for i in range(len(self.PreTable[self.current][self.token_list[self.index][0]])-1, -1, -1):
                            self.stark.append(self.PreTable[self.current][self.token_list[self.index][0]][i])
                        pprint(self.stark)
    
    def getPreTable(self):
        self.PreTable = deepcopy(self.first)
        for nonterminal in self.nonterminal:
            if 'ε' in self.first[nonterminal].keys():
                print(self.follow[nonterminal])
                for i in self.follow[nonterminal]:
                    if i not in self.PreTable[nonterminal].keys():
                        self.PreTable[nonterminal][i] = ['ε']



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


# starter = 'AriExp'
# starter = 'Exp'
# starter = 'BooExp'
starter = 'Sta'

# source_string = '!demo && b'
# source_string = 'demo = a + box'
# source_string = 'if(a>a&& b||c){int a = 11;c=10;}'
source_string = '''
    {int result ;
    int a = 1-c;}
'''

res = Lexical_Analyzer(source_string).analyse()

analyzer = Analyzer(starter, terminal, production)
analyzer.analyse(res=res)