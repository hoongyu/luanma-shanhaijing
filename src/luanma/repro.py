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


@repro("wenhao")
def wenhao():
    """GBK 装不下扩展 A 区的字，errors='replace' 拿 ASCII 问号顶上。姓名当场缺一个字。"""
    name = "".join(chr(c) for c in (0x5218, 0x4DAE))
    return name.encode("gbk", errors="replace").decode("gbk")


@repro("qiwenhao")
def qiwenhao():
    """同一家四口走 GBK 管道：errors='replace' 逐码位替换，连三枚不可见的 ZWJ 也各换一个问号。"""
    z = chr(0x200D)
    fam = (chr(0x1F468) + z + chr(0x1F469) + z
           + chr(0x1F467) + z + chr(0x1F466))
    return fam.encode("gbk", errors="replace").decode("gbk")


@repro("nfd_lv")
def nfd_lv():
    """拼音 lv4 的预组合形式 GBK 编得出来，分解形式的两枚组合符号 GBK 根本没有。"""
    import unicodedata
    nfc = "l" + chr(0x01DC)
    nfd = unicodedata.normalize("NFD", nfc)
    return nfd.encode("gbk", errors="replace").decode("gbk")


@repro("shen")
def shen():
    """CJK 兼容汉字带单例规范分解，单例分解永不重组，所以连 NFC 都会把它换掉。"""
    import unicodedata
    return unicodedata.normalize("NFC", chr(0xFA19))
