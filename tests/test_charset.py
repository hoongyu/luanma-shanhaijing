from luanma.charset import beast_charset, ui_charset


def test_beast_charset_covers_every_glyph_in_the_yaopu():
    cs = beast_charset()

    for ch in "锟斤拷烫屯":      # 妖形用的简体字
        assert ch in cs
    for ch in "錕燙":            # 妖名用的繁体字：马善政没有，已移交 ui_charset
        assert ch not in cs


def test_beast_charset_is_deduplicated():
    cs = beast_charset()

    assert len(cs) == len(set(cs))


def test_ui_charset_carries_the_field_names_and_punctuation():
    cs = ui_charset()

    for ch in "形現因驗異驅":
        assert ch in cs
    for ch in "「」。，":
        assert ch in cs


def test_ui_charset_carries_the_beast_names():
    cs = ui_charset()

    for ch in "錕燙":            # 只有源流明體有它们
        assert ch in cs
