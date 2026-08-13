"""源码里不许出现字面的替换字符。

这个项目讲的是「字符在搬运途中损坏」，而它自己的源码要经过编辑器、
JSON 工具调用层、git、CI 四道搬运。实施期间已发生三次真实污染，
根因都是转义序列在某一层被提前解码成了真字符。

注意：本文件刻意用 chr(0xFFFD) 构造目标字符，绝不写它的转义序列 ——
否则这个测试会检测到自己。
"""

import pathlib

import pytest

REPLACEMENT_CHAR = chr(0xFFFD)

SCANNED = sorted(
    p
    # README 与设计文档都复述了同一段考据，它们同样会被污染 ——
    # 审查实测：污染 README 后全套测试照样全绿。
    for pat in (
        "src/**/*.py",
        "tests/**/*.py",
        "scripts/**/*.py",
        "yao/**/*.yaml",
        "*.md",
        "docs/**/*.md",
        ".github/**/*.yml",
        "*.toml",
    )
    for p in pathlib.Path(__file__).resolve().parents[1].glob(pat)
)


def test_there_are_files_to_scan():
    assert SCANNED, "扫描列表为空，说明路径写错了，这个守卫会形同虚设"


@pytest.mark.parametrize("path", SCANNED, ids=lambda p: p.name)
def test_no_literal_replacement_char_in_source(path):
    text = path.read_text(encoding="utf-8")
    count = text.count(REPLACEMENT_CHAR)

    assert count == 0, (
        f"{path} 含 {count} 个字面替换字符。"
        f"表示 U+FFFD 请用转义序列或 chr(0xFFFD)，不要写字面字符。"
    )
