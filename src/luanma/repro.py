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


@repro("tangtangtang")
def tangtangtang():
    """MSVC 调试版把未初始化的栈内存填成 0xCC；CC CC 在 GBK 中是「烫」。"""
    return (b"\xcc" * 6).decode("gbk")


@repro("tuntuntun")
def tuntuntun():
    """同上，堆内存填 0xCD；CD CD 是「屯」。见烫知栈，见屯知堆。"""
    return (b"\xcd" * 6).decode("gbk")
