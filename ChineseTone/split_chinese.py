from __future__ import unicode_literals
import re
text_type = str
bytes_type = bytes
RE_HANS = re.compile(  # pragma: no cover
    r'^(?:['
    r'\u3007'  # 〇
    r'\u3400-\u4dbf'  # CJK扩展A:[3400-4DBF]
    r'\u4e00-\u9fff'  # CJK基本:[4E00-9FFF]
    r'\uf900-\ufaff'  # CJK兼容:[F900-FAFF]
    r'])+$'
)
def _seg(chars):
    """按是否是汉字进行分词"""
    s = ''  # 保存一个词
    ret = []  # 分词结果
    flag = 0  # 上一个字符是什么? 0: 汉字, 1: 不是汉字

    for n, c in enumerate(chars):
        if RE_HANS.match(c):  # 汉字, 确定 flag 的初始值
            if n == 0:  # 第一个字符
                flag = 0

            if flag == 0:
                s += c
            else:  # 上一个字符不是汉字, 分词
                ret.append(s)
                flag = 0
                s = c

        else:  # 不是汉字
            if n == 0:  # 第一个字符, 确定 flag 的初始值
                flag = 1

            if flag == 1:
                s += c
            else:  # 上一个字符是汉字, 分词
                ret.append(s)
                flag = 1
                s = c

    ret.append(s)  # 最后的词
    return ret
def simple_seg(hans):
    """将传入的字符串按是否是汉字来分割"""
    assert not isinstance(hans, bytes_type), \
        'must be unicode string or [unicode, ...] list'

    if isinstance(hans, text_type):
        return _seg(hans)
# print(simple_seg('I like china!'))