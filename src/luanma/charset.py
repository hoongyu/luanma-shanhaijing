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
    """妖形用字：只取 glyphs，**不取妖名**。横排，走马善政。

    妖名曾经也在这里，直到实测发现马善政的 cmap 缺「錕」「燙」——
    而 pyftsubset 对缺字不报错、不警告、退出码 0，所以那两个字
    从第一批入库起就一直在产物里缺席，没人发现。妖名已改由
    ui_charset() 承担（源流明體有这两个字）。

    往回加妖名之前先确认马善政有那些字，否则 scripts/build_fonts.py
    的覆盖断言会拦住你 —— 那正是它存在的理由。
    """
    seen = []
    for y in yaos if yaos is not None else load_all():
        for ch in y.glyphs:
            if ch not in seen:
                seen.append(ch)
    return "".join(seen)


def ui_charset(yaos=None):
    """版式用字：固定的书名版心字段名，**外加全部妖名**。含竖排，走源流明體。

    妖名在这里而不在 beast_charset，是因为马善政缺「錕」「燙」。
    源流明體字符集大得多，且本就承担竖排——古籍版式里题名与
    正文用不同字体是常态，所以这个安排不是将就。
    """
    seen = []
    for ch in UI_FIXED:
        if ch not in seen:
            seen.append(ch)
    for y in yaos if yaos is not None else load_all():
        for ch in y.name:
            if ch not in seen:
                seen.append(ch)
    return "".join(seen)
