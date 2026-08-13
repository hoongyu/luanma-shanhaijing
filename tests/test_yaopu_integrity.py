"""全谱一致性 —— 本项目的地基。

别人写图鉴靠记忆和转述；这里每一条都是活的、可执行的、被持续验证的。
考据哪天因环境变化不成立了，这个测试会红。
"""

import pytest

from luanma.loader import load_all
from luanma.repro import REGISTRY

YAOS = load_all()

# 这些 tag 的成因**就是**「一串字节被当成另一种编码读了」。属于它们的妖
# 必须交出 codec 与 hex_texture，否则字节断言会对它静默跳过 —— 那正是
# 这个项目最怕的事：报告全绿，守卫却是空的。
#
# 判据用白名单而不是黑名单，是刻意的。黑名单（「除了规范化/排序/断行
# 以外都要填字节」）会误伤每一类还没被想到的新妖 —— 第二批 30 只里有
# Unicode 规范化、排序、断行、编码写入失败、UTF-16 码元切割，只要有一类
# 没被写进黑名单，作者就会被逼着给一只没有字节故事的妖编一个出来。
# 白名单只会漏（新造一个 tag 的字节妖不被拦），不会误伤；而漏掉的代价
# 是「少验一条」，误伤的代价是「往妖谱里灌假考据」。后者严重得多。
BYTE_STORY_TAGS = frozenset({"编码误读", "内存填充"})


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
    妖谱里声称的每个十六进制，必须等于那个字在 codec 下真实的编码。

    没有 codec 的妖不是字节类的妖（规范化、排序、断行……），跳过 ——
    显式跳过，让「跳过了」和「验过了」在测试报告里长得不一样。
    """
    if not y.codec:
        pytest.skip(f"{y.id} 没有字节故事（无 codec），字节断言不适用")

    assert len(y.bytes) == len(y.glyphs), (
        f"{y.id}: bytes 有 {len(y.bytes)} 项，glyphs 有 {len(y.glyphs)} 个，对不上"
    )
    for glyph, hexpair in zip(y.glyphs, y.bytes):
        claimed = bytes.fromhex(hexpair.replace(" ", ""))
        actual = glyph.encode(y.codec)
        assert actual == claimed, (
            f"{y.id}: {glyph!r} 的真实 {y.codec} 编码是 {actual.hex(' ').upper()}，"
            f"妖谱却声称 {hexpair}"
        )


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_the_out_field_matches_the_glyphs(y):
    assert " ".join(y.glyphs) == y.out


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_a_yao_whose_tag_promises_a_byte_story_actually_tells_one(y):
    """字节字段可选，但不是「可以随便不填」。

    改成可选之后出现一个新的失效方式：新加一只 GBK 妖时忘了填 codec，
    两条字节断言会安静地 SKIP，测试报告照样没有红色 —— 作者以为它被
    验过了。这条元断言把这个洞堵上：tag 落在 BYTE_STORY_TAGS 里的妖，
    字节故事是必填的。

    反过来不成立：不在名单里的 tag 一律不被要求，因为它们的成因根本
    不在字节层。
    """
    if y.tag not in BYTE_STORY_TAGS:
        pytest.skip(f"{y.id} 的 tag「{y.tag}」不属于字节类，不要求字节故事")

    missing = [f for f in ("codec", "hex_texture") if not getattr(y, f)]

    assert not missing, (
        f"{y.id} 的 tag 是「{y.tag}」—— 这类妖的成因就是字节被当成别的"
        f"编码读，却没填 {', '.join(missing)}。不填的话字节断言会对它"
        f"静默跳过，等于没验"
    )


def test_no_orphan_repro_functions():
    """注册了复现函数却没有对应的妖谱条目 —— 多半是删 YAML 时漏了。"""
    used = {y.repro for y in YAOS}
    orphans = sorted(set(REGISTRY) - used)

    assert not orphans, f"这些复现函数没有对应的妖谱条目: {orphans}"


@pytest.mark.parametrize("y", YAOS, ids=lambda y: y.id)
def test_hex_texture_is_the_byte_unit_that_actually_generates_this_mojibake(y):
    """hex_texture 不是装饰，是生成该乱码的重复字节单元。

    三条妖谱的语义看似不同（锟斤拷是 U+FFFD 的 UTF-8，烫/屯是内存填充
    字节），但抽象是同一个：把这个单元重复若干次按 codec 解，就得到该妖。

    没有 hex_texture 的妖不适用 —— 它们的成因不在字节层。硬要它们填，
    它们只能填 expect 自己的编码，重复一次必然通过，这条断言就退化成
    同义反复：永远绿，不再验证任何东西。
    """
    if not y.hex_texture:
        pytest.skip(f"{y.id} 没有字节故事（无 hex_texture），字节断言不适用")

    unit = bytes.fromhex(y.hex_texture.replace(" ", ""))

    for n in range(1, 13):
        try:
            if (unit * n).decode(y.codec) == y.expect:
                return
        except UnicodeDecodeError:
            continue

    raise AssertionError(
        f"{y.id}: 把 {y.hex_texture} 重复 1..12 次按 {y.codec} 解码，"
        f"没有任何一次得到 {y.expect!r} —— 这个字节单元生成不出这只妖"
    )
