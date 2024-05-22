import queue
from .SLR1Analyzer import *
from .lexicalAnalyzer import *


class TokenReceiveCache:
    """
    token接收缓存
    queue: 需要进行语法分析的token队列
    count: 记录已读入的token数量
    """

    def __init__(self, q):
        self.queue = q
        self.count = 0

    def gettoken(self):
        self.count += 1
        return self.queue.get()


class InputCache:
    """
    输入缓存类（按行缓存）
    属性:
    f: 输入文件
    cache: 行读入缓存
    beginning: 当前token起始位置
    forward: 待读取字符位置
    方法:
    getchar(): 从输入缓冲区中将下一个输入字符读入ch，并将读入指针前移。
    retract(num=1): 将数据缓冲区读入指针向前回退num个字符。
    pop_token(): 返回输入缓冲区开始指针到读入指针之间的字符串，并将开始指针与读入指针放到下一个token的位置。
    """

    def __init__(self, file):
        self.__cache = ""
        self.__beginning = 0
        self.__forward = 0
        self.__f = open(file, "r")

    def __del__(self):
        self.__f.close()

    def getchar(self):
        if self.__forward == len(self.__cache):
            if self.__beginning == self.__forward:
                self.__cache = self.__f.readline().strip()
                self.__beginning = 0
                self.__forward = 0
            else:
                self.__forward += 1
                return ""
        if not self.__cache:
            return EOF
        ch = self.__cache[self.__forward]
        self.__forward += 1
        return ch

    def retract(self, num=1):
        if self.__forward:
            self.__forward -= num

    def pop_token(self):
        token = self.__cache[self.__beginning: self.__forward]
        self.__beginning = self.__forward
        self.__forward = self.__beginning
        return token.lstrip()


def lexical_analyze(q, input_file, e):
    inputCache = InputCache(input_file)
    token = token_scan(inputCache)
    # 读入token直到到达文件末尾
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)

    token_file = os.path.join(output_dir, 'tokens.txt')
    with open(token_file, 'w') as f:
        while token[0] != EOF_TOKEN_CATEGORY:
            # 忽略识别失败的单词并输出
            # print(token, end=" ")
            f.write(str(token) + '\n')
            while token[0] == UNRECOGNIZED_TOKEN_CATEGORY:
                e.write(f"[ERROR] 检测到词法错误, 无法识别单词{token[1]}\n")
                token = token_scan(inputCache)
            # 将识别成功的token放入队列进行语法分析
            q.put(token)
            token = token_scan(inputCache)
        # 将结束符放入队列
        q.put((EOF_TOKEN_CATEGORY, 0))


def syntax_analyze(q, e):
    tokenReceiveCache = TokenReceiveCache(q)
    token_analysis(tokenReceiveCache, e)


def parser(input_file):
    output_dir = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_dir, exist_ok=True)
    error_file = os.path.join(output_dir, 'error.txt')
    with open(error_file, 'w') as e:
        q = queue.Queue()
        lexical_analyze(q, input_file, e)
        syntax_analyze(q, e)
