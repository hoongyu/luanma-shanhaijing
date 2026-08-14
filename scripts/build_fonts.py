"""从妖谱生成子集化字体。

上游原件下载（不进仓库，见 .gitignore）：
  马善政毛笔楷书  https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf
  源流明體 TW-R   https://github.com/ButTaiwan/genryu-font/releases  (GenRyuMin2TW-otf.zip)

三条不能违反的规则：
  1. --layout-features="*"  —— 写成 "" 会静默毁掉竖排标点
  2. CSS family 必须改名 —— 子集化在 OFL FAQ 2.6 下算 modification
  3. 请求的字必须全在产物 cmap 里 —— 原件缺字时 pyftsubset 既不报错
     也不警告，退出码照样是 0，只有最终页面上会出现方框
"""

import pathlib
import subprocess
import sys

from fontTools.ttLib import TTFont

from luanma.charset import beast_charset, ui_charset

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "fonts" / "source"
OUT = ROOT / "public" / "fonts"

# family 名刻意不是原名：子集化算 modification，OFL 要求改名。
JOBS = [
    ("YaoBrush", "MaShanZheng-Regular.ttf", beast_charset, False),
    ("YaoSeal", "GenRyuMin2TW-R.otf", ui_charset, True),
]

# 只认 vert/vrt2 —— 做竖排标点替换的就是它们。
# 原先这里还混着 halt/palt，那是横排 feature（竖排对应物是 vhal/vpal），
# 而断言是「命中任意一个即通过」，于是零个竖排 feature 也能过关。
VERT_FEATURES = {"vert", "vrt2"}


def features_of(path):
    ft = TTFont(path)
    found = set()
    for tag in ("GSUB", "GPOS"):
        if tag in ft and ft[tag].table.FeatureList:
            found |= {r.FeatureTag for r in ft[tag].table.FeatureList.FeatureRecord}
    return found


def codepoints_of(path):
    ft = TTFont(path)
    found = set()
    for t in ft["cmap"].tables:
        found |= set(t.cmap)
    return found


def missing_from(path, text):
    """请求了但产物里没有的字。原件 cmap 缺字就会落到这里。"""
    covered = codepoints_of(path)
    return [ch for ch in text if ord(ch) not in covered]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    failures = []
    for family, src, chars_fn, needs_vertical in JOBS:
        srcp = SRC / src
        if not srcp.exists():
            sys.exit(f"缺少字体原件: {srcp}\n见本文件 docstring 里的下载地址")
        text = chars_fn()
        outp = OUT / f"{family}.woff2"
        subprocess.run(
            ["pyftsubset", str(srcp), f"--text={text}", "--flavor=woff2",
             f"--output-file={outp}", "--layout-features=*", "--no-hinting"],
            check=True,
        )
        size = outp.stat().st_size
        feats = features_of(outp)
        print(f"  {family:<10} {len(text):>3} 字  {size:>6} B  -> {outp.name}")

        # 码位而不是字符 —— 终端多半是 GBK，直接打这些字只会打出乱码。
        missing = missing_from(outp, text)
        if missing:
            failures.append(
                f"{family} 缺 {len(missing)}/{len(text)} 字: "
                + " ".join(f"U+{ord(ch):04X}" for ch in missing)
                + f" —— 原件 {src} 的 cmap 里没有这些字，"
                f"pyftsubset 对缺字不报错也不警告。"
                f"换原件，或把这些字挪到有它们的那个 family"
            )
        else:
            print(f"             覆盖: {len(text)}/{len(text)} 字，零缺失")

        if needs_vertical:
            got = feats & VERT_FEATURES
            if not got:
                failures.append(
                    f"{family} 丢失了全部竖排 feature —— "
                    f"检查 --layout-features 是否被写成了空字符串"
                )
            else:
                print(f"             竖排 feature: {','.join(sorted(got))}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}", file=sys.stderr)
        sys.exit(1)
    print("\n字体产物就绪。")


if __name__ == "__main__":
    main()
