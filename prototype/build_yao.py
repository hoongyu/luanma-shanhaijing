"""Subset the real fonts for yao.html and inline them.

Two rules the measurements forced on us:
  - Ma Shan Zheng has no vertical metrics tables at all, so it may only
    carry horizontal text (the beast glyphs and the beast's name).
  - Anything set vertically must come from GenRyuMin, which keeps
    vert/vhal/vpal after subsetting.

Subsetting counts as modification under OFL FAQ 2.6, so the CSS family
names are deliberately ours ("YaoBrush"/"YaoSeal") rather than the
originals. Full OFL texts stay in fonts/LICENSES/.
"""
import base64
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).parent
FONTS = HERE / "fonts"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)

# Exactly what each face has to render, nothing more.
JOBS = [
    # css family,  source file,                 characters
    ("YaoBrush", "MaShanZheng-Regular.ttf",
     "锟斤拷烫屯錕燙"),                                   # 妖形 + 妖名，横排
    ("YaoSeal", "GenRyuMin2TW-R.otf",
     "亂碼山海經卷一二三形現因驗異驅闔點其以觀詳已覆核"
     "「」『』。，、（）：；？！—…"),                     # 版式，含竖排
]

faces = []
for family, src, text in JOBS:
    srcp = FONTS / src
    if not srcp.exists():
        sys.exit(f"missing font: {srcp}")
    out = BUILD / f"{family}.woff2"
    subprocess.run(
        ["pyftsubset", str(srcp), f"--text={text}", "--flavor=woff2",
         f"--output-file={out}", "--layout-features=*", "--no-hinting"],
        check=True,
    )
    b64 = base64.b64encode(out.read_bytes()).decode()
    faces.append(
        f"@font-face{{font-family:'{family}';"
        f"src:url(data:font/woff2;base64,{b64}) format('woff2');"
        f"font-display:block}}"
    )
    print(f"  {family:<10} {len(text):>3} chars  {out.stat().st_size:>6} B  <- {src}")

tpl = (HERE / "yao.html").read_text(encoding="utf-8")
if "__FONTFACE__" not in tpl:
    sys.exit("yao.html has no __FONTFACE__ marker")
out = HERE / "yao.built.html"
out.write_text(tpl.replace("__FONTFACE__", "".join(faces)), encoding="utf-8")
print(f"\nwrote {out.name}  {out.stat().st_size/1024:.1f} KB")
