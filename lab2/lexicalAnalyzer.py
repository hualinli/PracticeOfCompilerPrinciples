from .states import STATES
from .utils import *


def token_scan(inputCache):
    """
    token解析函数
    Args:
        inputCache: 输入缓存对象，用于读取输入字符和记录token信息

    Returns:
        一个元组，包含token的类别码和值。
        如果解析过程中发生错误，则返回(UNRECOGNIZED_TOKEN_CATEGORY, inputCache.pop_token())
        如果读取到文件末尾，返回(EOF_TOKEN_CATEGORY, 0)
    """
    state_now = 0
    # 如果是非终结状态，则继续读取字符进行状态转移
    while STATES[state_now].state_type() == NORMAL_TYPE:
        ch = inputCache.getchar()
        state_now = STATES[state_now].next_state(ch)
        # 到达文件末尾，退出循环处理最后一个输入单词
        if ch == EOF:
            break
        # 如果转移到了出错状态，返回表示出错的特殊token
        if state_now == ERROR_STATE:
            return UNRECOGNIZED_TOKEN_CATEGORY, inputCache.pop_token()
    # 如果由最后一个输入单词转移到了终止状态，调用该状态的token生成方法
    if STATES[state_now].state_type() == FINAL_TYPE:
        return STATES[state_now].get_value(inputCache.pop_token())
    # 如果由最后一个输入单词转移到了需要回退的终止状态，先回退读入指针再生成token
    if STATES[state_now].state_type() == ROLLBACK_FINAL_TYPE:
        inputCache.retract(1)
        return STATES[state_now].get_value(inputCache.pop_token())
    # 否则当前没有任何token可识别，返回表示文件结束的特殊token
    return EOF_TOKEN_CATEGORY, 0
