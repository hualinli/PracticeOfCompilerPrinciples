import re, os
from enum import Enum
from collections import defaultdict


class TokenType(Enum):
    KEYWORD = 1
    DELIMITER = 2
    IDENTIFIER = 3
    NUMBER = 4
    STRING = 5
    OPERATOR = 6
    CHAR = 7


class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value

    def __str__(self):
        if self.type == TokenType.KEYWORD:
            return f'<{self.value}>'
        elif self.type == TokenType.DELIMITER:
            return f'<{self.value}>'
        elif self.type == TokenType.IDENTIFIER:
            return f'<id, {self.value}>'
        elif self.type == TokenType.NUMBER:
            return f'<num, {self.value}>'
        elif self.type == TokenType.STRING:
            return f'<str, {self.value}>'
        elif self.type == TokenType.OPERATOR:
            return f'<{self.value}>'
        elif self.type == TokenType.CHAR:
            return f'<{self.value}>'
        else:
            return f'<unknown, {self.value}>'

    def __eq__(self, other):
        return self.type == other.type and self.value == other.value


class LexicalParser:
    """Define the keywords, delimiters, operators, etc."""
    _keywords = [
        "int", "float", "double", "char", "void",
        "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return",
        "const", "static", "extern", "register", "auto", "volatile",
        "typedef", "struct", "union", "enum",
        "true", "false", "NULL",
    ]

    _delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", ".", ":"]
    _single_char_operators = ["+", "-", "*", "/", "%", "=", "!", "&", "|", "^", "~", "<", ">", "?"]
    _double_char_operators = ["++", "--", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>", "->"]

    _number_pattern = re.compile(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
    _string_pattern = re.compile(r'"[^"]*[^\n]"')
    _unfinished_string_pattern = re.compile(r'"[^"]*\n')
    _identifier_pattern = re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*")
    _char_pattern = re.compile(r"'.'")
    _unfinished_char_pattern = re.compile(r"'.\n")
    _new_line_pattern = re.compile('\n')
    _preprocessor_pattern = re.compile(r"#.*")
    _comment_pattern = re.compile(r"//.*")
    _multi_line_comment_pattern = re.compile(r"/\*.*?\*/", re.DOTALL)

    def __init__(self, code: str) -> None:
        self.code = code
        self.tokens = []

    def parse(self) -> list[Token]:
        code = self.code
        code = re.sub(self._preprocessor_pattern, "", code)
        code = re.sub(self._comment_pattern, "", code)
        code = re.sub(self._multi_line_comment_pattern, "", code)

        i = 0
        n = len(code)
        while i < n:
            ch = code[i]
            i += 1
            if ch.isspace():
                continue
            elif ch in self._delimiters:
                self.tokens.append(Token(TokenType.DELIMITER, ch))
            elif ch in self._single_char_operators:
                if i < n and ch + code[i] in self._double_char_operators:
                    self.tokens.append(Token(TokenType.OPERATOR, ch + code[i]))
                    i += 1
                else:
                    self.tokens.append(Token(TokenType.OPERATOR, ch))
            elif ch == '"':
                match = re.match(self._string_pattern, code[i - 1:])
                if match:
                    self.tokens.append(Token(TokenType.STRING, match.group()))
                    i += len(match.group()) - 1
                else:
                    match = re.search('\n', code[i - 1:])
                    if match:
                        print("Unfinished string: %s" % code[i - 1:match.end()])
                        i += match.end() - 1
            elif ch == "'":
                match = re.match(self._char_pattern, code[i - 1:])
                if match:
                    self.tokens.append(Token(TokenType.CHAR, match.group()))
                    i += len(match.group()) - 1
                else:
                    match = re.search('\n', code[i - 1:])
                    if match:
                        print("Unfinished char: %s" % code[i - 1:match.end()])
                        i += match.end() - 1
            elif ch.isdigit():
                match = re.match(self._number_pattern, code[i - 1:])
                if match:
                    self.tokens.append(Token(TokenType.NUMBER, match.group()))
                    i += len(match.group()) - 1
            elif ch.isalpha() or ch == "_":
                match = re.match(self._identifier_pattern, code[i - 1:])
                if match:
                    word = match.group().lower()
                    if word in self._keywords:
                        self.tokens.append(Token(TokenType.KEYWORD, word))
                    else:
                        self.tokens.append(Token(TokenType.IDENTIFIER, word))
                    i += len(match.group()) - 1
            else:
                print("Unknown character: %s" % ch)

        return self.tokens


def generate_symbol_list(tokens):
    keyword_list = defaultdict(int)
    identifier_list = defaultdict(int)
    number_list = defaultdict(int)

    for token in tokens:
        if token.type == TokenType.KEYWORD:
            keyword_list[token.value] += 1
        elif token.type == TokenType.IDENTIFIER:
            identifier_list[token.value] += 1
        elif token.type == TokenType.NUMBER:
            number_list[token.value] += 1

    symbol_list = {
        'KEYWORD': [k for k, count in keyword_list.items() if count > 0],
        'IDENTIFIER': [i for i, count in identifier_list.items() if count > 0],
        'NUMBER': [n for n, count in number_list.items() if count > 0],
    }
    output_dir = os.path.join('output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'symbols.sym')

    with open(output_file, 'w') as f:
        for symbol_type, values in symbol_list.items():
            for value in values:
                f.write(f'{symbol_type} {value}\n')
    return output_file


def lexer(input_file):
    with open(input_file, 'r') as f:
        code = f.read()

    parser = LexicalParser(code)
    tokens = parser.parse()
    sym_file = generate_symbol_list(tokens)

    output_dir = os.path.join('output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'tokens.txt')

    with open(output_file, 'w') as f:
        for token in tokens:
            f.write(f'{token}\n')
    return output_file, sym_file


if __name__ == '__main__':
    print(lexer('uploads/test.c'))
