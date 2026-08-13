import pytest

from luanma.schema import Yao, SchemaError

MINIMAL = {
    "id": "kunjinkao",
    "name": "錕斤拷",
    "tag": "编码误读",
    "glyphs": ["锟", "斤", "拷"],
    "hex_texture": "EF BF BD",
    "codec": "gbk",
    "why": "它是伤上加伤。",
    "notes": [["現", "UTF-8 被当作 GBK 解读"]],
    "repro": "kunjinkao",
    "expect": "锟斤拷",
}


def test_builds_a_yao_from_a_complete_entry():
    y = Yao.from_dict(MINIMAL)

    assert y.id == "kunjinkao"
    assert y.glyphs == ["锟", "斤", "拷"]
    assert y.expect == "锟斤拷"


def test_rejects_an_entry_with_no_repro_because_that_is_the_admission_bar():
    broken = {k: v for k, v in MINIMAL.items() if k != "repro"}

    with pytest.raises(SchemaError, match="repro"):
        Yao.from_dict(broken)


def test_rejects_glyphs_that_is_a_string_instead_of_a_list():
    """YAML 里写 glyphs: 锟斤拷（忘了方括号）会被解析成字符串。

    不拦的话它会一路绿到字体产物 —— 字符集抽取对字符串同样能迭代。
    """
    broken = dict(MINIMAL, glyphs="锟斤拷")

    with pytest.raises(SchemaError, match="glyphs"):
        Yao.from_dict(broken)


def test_rejects_notes_that_is_not_a_list():
    broken = dict(MINIMAL, notes=5)

    with pytest.raises(SchemaError, match="notes"):
        Yao.from_dict(broken)


def test_accepts_a_yao_with_no_byte_story_at_all():
    """不是每只妖都由「字节被误读」造成。

    规范化类、排序类、断行类的妖没有字节故事。逼它们填 hex_texture，
    它们只能填自己 expect 的编码 —— 重复一次必然通过，断言退化成
    同义反复，永远绿，不再验证任何东西。所以字节字段必须可缺。
    """
    no_bytes = {
        k: v for k, v in MINIMAL.items() if k not in ("hex_texture", "codec")
    }

    y = Yao.from_dict(no_bytes)

    assert y.hex_texture == ""
    assert y.codec == ""


def test_rejects_hex_texture_without_codec():
    """半填比不填更危险：有字节却没说按什么编码读，断言无从下手。"""
    half = {k: v for k, v in MINIMAL.items() if k != "codec"}

    with pytest.raises(SchemaError, match="codec"):
        Yao.from_dict(half)


def test_rejects_codec_without_hex_texture():
    half = {k: v for k, v in MINIMAL.items() if k != "hex_texture"}

    with pytest.raises(SchemaError, match="hex_texture"):
        Yao.from_dict(half)


def test_a_complete_byte_story_carries_both_fields():
    y = Yao.from_dict(MINIMAL)

    assert y.codec == "gbk"
    assert y.hex_texture == "EF BF BD"
