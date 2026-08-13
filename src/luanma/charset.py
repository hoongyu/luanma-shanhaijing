"""按字体角色抽取用字。

分开抽是硬要求：马善政没有竖排度量表，只能承担横排的妖形与妖名；
竖排版式必须走源流明體。两者的字符集因此不同。
"""

from .loader import load_all

# 版式固定用字：书名、卷次、字段名、导航、以及竖排会用到的标点。
UI_FIXED = (
    "亂碼山海經"
    "卷一二三四五六七八九十"
    "形現因驗異驅"
    "闔點其以觀詳已覆核"
    "「」『』。，、（）：；？！—…"
)


def beast_charset(yaos=None):
    """妖形与妖名用字。横排，走马善政。"""
    seen = []
    for y in yaos if yaos is not None else load_all():
        for ch in "".join(y.glyphs) + y.name:
            if ch not in seen:
                seen.append(ch)
    return "".join(seen)


def ui_charset():
    """版式用字。含竖排，走源流明體。"""
    seen = []
    for ch in UI_FIXED:
        if ch not in seen:
            seen.append(ch)
    return "".join(seen)
