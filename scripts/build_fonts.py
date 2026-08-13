"""从妖谱生成子集化字体。

上游原件下载（不进仓库，见 .gitignore）：
  马善政毛笔楷书  https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf
  源流明體 TW-R   https://github.com/ButTaiwan/genryu-font/releases  (GenRyuMin2TW-otf.zip)

两条不能违反的规则：
  1. --layout-features="*"  —— 写成 "" 会静默毁掉竖排标点
  2. CSS family 必须改名 —— 子集化在 OFL FAQ 2.6 下算 modification
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

VERT_FEATURES = {"vert", "vrt2", "valt", "vpal", "vhal", "halt", "palt"}


def features_of(path):
    ft = TTFont(path)
    found = set()
    for tag in ("GSUB", "GPOS"):
        if tag in ft and ft[tag].table.FeatureList:
            found |= {r.FeatureTag for r in ft[tag].table.FeatureList.FeatureRecord}
    return found


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
