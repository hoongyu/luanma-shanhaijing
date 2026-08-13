"""每只妖的复现代码。

这些不是示例，是断言。全谱一致性测试会调用每一个，
并要求它确实产出该妖的乱码 —— 考据哪天不成立了，CI 会红。
"""

REGISTRY = {}


def repro(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


@repro("kunjinkao")
def kunjinkao():
    """U+FFFD 的 UTF-8 是 EF BF BD；两枚相连按 GBK 双字节切开 = 锟斤拷。"""
    return ("\ufffd" * 2).encode("utf-8").decode("gbk")
