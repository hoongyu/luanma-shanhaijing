"""全谱一致性 —— 本项目的地基。

别人写图鉴靠记忆和转述；这里每一条都是活的、可执行的、被持续验证的。
考据哪天因环境变化不成立了，这个测试会红。
"""

import pytest

from luanma.loader import load_all
from luanma.repro import REGISTRY

YAOS = load_all()


def test_the_yaopu_is_not_empty():
    assert YAOS


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_every_yao_has_a_registered_repro(y):
    assert y.repro in REGISTRY, f"{y.id} 的复现函数 {y.repro!r} 未注册"


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_every_repro_actually_produces_the_mojibake_it_claims(y):
    assert REGISTRY[y.repro]() == y.expect


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_ids_match_filenames_so_the_registry_stays_navigable(y):
    from luanma.loader import YAO_DIR
    assert (YAO_DIR / f"{y.id}.yaml").exists()


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_the_glyphs_readers_see_are_exactly_what_the_repro_produces(y):
    """妖形即所证。

    glyphs 是读者看到的妖形，也是字体子集化的输入源。它和 expect
    之间原本没有任何约束 —— 把锟斤拷倒序成拷斤锟，测试照样全绿，
    错误的妖形还会一路流进字体产物。
    """
    assert "".join(y.glyphs) == y.expect


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_each_glyph_really_encodes_to_the_bytes_the_yaopu_claims(y):
    """字节级精确。

    README 首句自称「字节级精确」。这条断言让那句话第一次有守卫：
    妖谱里声称的每个十六进制，必须等于那个字真实的 GBK 编码。
    """
    assert len(y.bytes) == len(y.glyphs), (
        f"{y.id}: bytes 有 {len(y.bytes)} 项，glyphs 有 {len(y.glyphs)} 个，对不上"
    )
    for glyph, hexpair in zip(y.glyphs, y.bytes):
        claimed = bytes.fromhex(hexpair.replace(" ", ""))
        actual = glyph.encode("gbk")
        assert actual == claimed, (
            f"{y.id}: {glyph!r} 的真实 GBK 编码是 {actual.hex(' ').upper()}，"
            f"妖谱却声称 {hexpair}"
        )


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_the_out_field_matches_the_glyphs(y):
    assert " ".join(y.glyphs) == y.out


def test_no_orphan_repro_functions():
    """注册了复现函数却没有对应的妖谱条目 —— 多半是删 YAML 时漏了。"""
    used = {y.repro for y in YAOS}
    orphans = sorted(set(REGISTRY) - used)

    assert not orphans, f"这些复现函数没有对应的妖谱条目: {orphans}"
