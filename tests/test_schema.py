import pytest

from luanma.schema import Yao, SchemaError

MINIMAL = {
    "id": "kunjinkao",
    "name": "錕斤拷",
    "tag": "编码误读",
    "glyphs": ["锟", "斤", "拷"],
    "hex_texture": "EF BF BD",
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
