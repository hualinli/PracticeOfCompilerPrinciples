# 词法分析器

# 特殊状态下标
from enum import Enum, unique, auto
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

ERROR_STATE = -1

# 状态类型
NORMAL_TYPE = 1
FINAL_TYPE = 2
ROLLBACK_FINAL_TYPE = 3

# 特殊字符
EOF = "EOF"

# 特殊token类别码
EOF_TOKEN_CATEGORY = -1
UNRECOGNIZED_TOKEN_CATEGORY = 0
IDENTIFIER = 1
INTEGER = 2
REAL_NUMBER = 3
SPLIT = 4
CHAR = 5
STRING = 6
# 仅语法分析阶段
EMPTY_TOKEN = 7

# token类别码表
CATEGORY_DICT = {
    # 特殊类别
    "#": -1,
    "未识别单词": 0,
    "标识符": 1,
    "整数": 2,
    "实数": 3,
    ";": 4,
    "字符": 5,
    "字符串": 6,
    "ε": 7,
    # 字符
    "<=": 11,
    "<": 12,
    ">=": 13,
    ">": 14,
    "==": 15,
    "=": 16,
    "!=": 17,
    "!": 18,
    "+": 19,
    "-": 20,
    "/": 21,
    "*": 22,
    "%": 23,
    ",": 24,
    "(": 25,
    ")": 26,
    "[": 27,
    "]": 28,
    "{": 29,
    "}": 30,
    "'": 31,
    '"': 32,
    '&&': 33,
    '||': 34,

    # 关揵字
    "auto": 100,
    "break": 101,
    "case": 102,
    "char": 103,
    "const": 104,
    "continue": 105,
    "default": 106,
    "do": 107,
    "double": 108,
    "else": 109,
    "enum": 110,
    "extern": 111,
    "float": 112,
    "for": 113,
    "goto": 114,
    "if": 115,
    "int": 116,
    "long": 117,
    "register": 118,
    "return": 119,
    "short": 120,
    "signed": 121,
    "static": 122,
    "sizeof": 123,
    "struct": 124,
    "switch": 125,
    "typedef": 126,
    "union": 127,
    "unsigned": 128,
    "void": 129,
    "volatile": 130,
    "while": 131,
    "true": 132,
    "false": 133,
    "string": 134,
    "return": 135
}

CATEGORY_DICT_REVERSE = dict((v, k) for k, v in CATEGORY_DICT.items())


# 字符集合判断函数


def judge_space(token):
    return token.isspace()


def judge_letter(token):
    return token.isalpha()


def judge_digit(token):
    return token.isdigit()


def judge_letter_or_digit(token):
    return token.isalnum()


def judge_split(token):
    return token == ";"


# 字符集合-判断函数字典
CHARSET_FUNC_DICT = {
    'space': judge_space,
    'letter': judge_letter,
    'digit': judge_digit,
    'split': judge_split
}


# 语法分析器
# 文法变量
@unique
class Grammar(Enum):
    ROOT = auto()  # S'
    PROG_BLOCK = auto()  # S
    FUNC_DEF = auto()
    FUNC = auto()
    FUNC_CALL = auto()
    VAR_DECLARE = auto()
    VAR_ASSIGN = auto()
    VALUE = auto()
    BOOL = auto()
    TYPE = auto()
    CMP_OPT = auto()
    CAL_OPT = auto()
    LOOP = auto()
    BRANCH = auto()
    FORM_PARAM = auto()
    REAL_PARAM = auto()
    CONSTANT = auto()
    RET_VAL = auto()

    def __repr__(self):
        return self.name


# 产生式列表
initial_production_list = [
    # 程序->程序块
    (Grammar.ROOT, [[Grammar.PROG_BLOCK]]),
    # 程序块->函数定义|变量声明 分号|程序块 程序块
    (Grammar.PROG_BLOCK, [[Grammar.FUNC_DEF], [Grammar.VAR_DECLARE, (SPLIT, 0)],
                          [Grammar.PROG_BLOCK, Grammar.PROG_BLOCK]]),
    # 函数定义->类型 标识符 左括号 形式参数 右括号 左大括号 函数块 返回值 右大括号|类型 标识符 左括号 右括号 左大括号 函数块 右大括号
    (Grammar.FUNC_DEF, [
        [Grammar.TYPE, (IDENTIFIER, 0), (25, 0), Grammar.FORM_PARAM, (26, 0), (29, 0),
         Grammar.FUNC, Grammar.RET_VAL, (30, 0)],
        [Grammar.TYPE, (IDENTIFIER, 0), (25, 0), (26, 0), (29, 0), Grammar.FUNC, (30, 0)]]),
    (Grammar.RET_VAL, [[(135, 0), Grammar.VALUE, (4, 0)]]),
    # 变量声明->类型 标识符
    (Grammar.VAR_DECLARE, [[Grammar.TYPE, (IDENTIFIER, 0)]]),
    # 形式参数->类型 标识符|类型 标识符 逗号 形式参数
    (Grammar.FORM_PARAM, [[Grammar.TYPE, (IDENTIFIER, 0)],
                          [Grammar.TYPE, (IDENTIFIER, 0), (24, 0), Grammar.FORM_PARAM]]),
    # 函数块->变量声明 分号|变量赋值 分号|函数调用 分号|循环结构|分支结构|函数块 函数块
    (Grammar.FUNC, [[Grammar.VAR_DECLARE, (SPLIT, 0)], [Grammar.VAR_ASSIGN, (SPLIT, 0)],
                    [Grammar.FUNC_CALL, (SPLIT, 0)], [Grammar.LOOP], [Grammar.BRANCH],
                    [Grammar.FUNC, Grammar.FUNC]]),
    # 变量赋值->标识符 等号 常量
    (Grammar.VAR_ASSIGN, [[(IDENTIFIER, 0), (16, 0), Grammar.CONSTANT]]),
    # 算术表达式->算术表达式 算术运算符 算术表达式|负号 算术表达式|函数调用|左括号 算术表达式 右括号|标识符|整数|实数
    (Grammar.VALUE,
     [[Grammar.VALUE, Grammar.CAL_OPT, Grammar.VALUE],
      [(20, 0), Grammar.VALUE], [Grammar.FUNC_CALL],
      [(25, 0), Grammar.VALUE, (26, 0)], [(IDENTIFIER, 0)], [(INTEGER, 0)], [(REAL_NUMBER, 0)]]),
    # 布尔表达式->算术表达式 比较运算符 算术表达式|布尔表达式 与符号 布尔表达式|布尔表达式 或符号 布尔表达式|非符号 布尔表达式|函数调用|左括号 布尔表达式 右括号|标识符|真|假
    (Grammar.BOOL,
     [[Grammar.VALUE, Grammar.CMP_OPT, Grammar.VALUE],
      [Grammar.BOOL, (33, 0), Grammar.BOOL],
      [Grammar.BOOL, (34, 0), Grammar.BOOL],
      [(18, 0), Grammar.BOOL], [Grammar.FUNC_CALL],
      [(25, 0), Grammar.BOOL, (26, 0)], [(132, 0)], [(133, 0)]]),
    # 函数调用->标识符 左括号 实际参数 右括号|标识符 左括号 右括号
    (Grammar.FUNC_CALL,
     [[(IDENTIFIER, 0), (25, 0), Grammar.REAL_PARAM, (26, 0)], [(IDENTIFIER, 0), (25, 0), (26, 0)]]),
    # 实际参数->标识符|实际参数->常量|实际参数 逗号 实际参数|
    (Grammar.REAL_PARAM,
     [[(IDENTIFIER, 0)], [Grammar.CONSTANT], [Grammar.REAL_PARAM, (24, 0), Grammar.REAL_PARAM]]),
    # 循环结构->关揵字while 左括号 布尔表达式 右括号 左大括号 函数块 右大括号
    (Grammar.LOOP,
     [[(131, 0), (25, 0), Grammar.BOOL, (26, 0), (29, 0), Grammar.FUNC, (30, 0)]]),
    # 分支结构->关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号|关键字if 左括号 布尔表达式 右括号 左大括号 函数块 右大括号 关键字else 左大括号 函数块 右大括号
    (Grammar.BRANCH,
     [[(115, 0), (25, 0), Grammar.BOOL, (26, 0), (29, 0), Grammar.FUNC, (30, 0)],
      [(115, 0), (25, 0), Grammar.BOOL, (26, 0), (29, 0), Grammar.FUNC, (30, 0),
       (109, 0), (29, 0), Grammar.FUNC, (30, 0)]]),
    # 类型->关联字int|关键字char|关键字string|关键字float
    (Grammar.TYPE, [[(116, 0)], [(103, 0)], [(134, 0)], [(112, 0)]]),
    # 算术运算符->加号|减号|乘号|除号|百分号
    (Grammar.CAL_OPT, [[(19, 0)], [(20, 0)], [(21, 0)], [(22, 0)], [(23, 0)]]),
    # 比较运算符->大于|小于|等于|大于等于|小于等于|不等于
    (Grammar.CMP_OPT, [[(14, 0)], [(12, 0)], [(15, 0)], [(13, 0)], [(11, 0)], [(17, 0)]]),
    # 常量->算术表达式|布尔表达式|整数|实数|字符|字符串
    (Grammar.CONSTANT,
     [[Grammar.VALUE], [Grammar.BOOL], [(INTEGER, 0)], [(REAL_NUMBER, 0)],
      [(CHAR, 0)], [(STRING, 0)]])
]


def fill_production(production, pop_token):
    filled_production = (production[0], pop_token)
    return filled_production



def token2str(token):
    if token[0] in [1, 2, 3]:
        return str(token[1])
    if token[0] == 4:
        return '; '
    if token[0] == 5:
        return "'%s'" % token[1]
    if token[0] == 6:
        return '"%s"' % token[1]
    return CATEGORY_DICT_REVERSE[token[0]]



