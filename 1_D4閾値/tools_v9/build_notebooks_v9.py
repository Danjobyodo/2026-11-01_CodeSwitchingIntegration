"""Build D4_v9_main.ipynb and D4_v9_validation.ipynb from the cell sources in tools_v9/cells/.

The code cells shared by the two notebooks (Cell 2 CFG and Cells 3-9) are taken from the SAME files, so the
validation notebook always runs exactly the code of the main notebook (v7 kept two hand-synchronised copies).

usage (from 1_D4閾値/):  python tools_v9/build_notebooks_v9.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = os.path.join(HERE, "cells")
OUT_DIR = os.path.dirname(HERE)

MAIN_STRIP = re.compile(r'\nif __name__ == "__main__":\n(    .*\n?)+\Z')


def read(name):
    with open(os.path.join(CELLS, name), encoding="utf-8") as fh:
        return fh.read()


def code_src(name):
    src = read(name).rstrip() + "\n"
    src = MAIN_STRIP.sub("\n", src)          # the run lines are added as explicit cells
    return src.rstrip() + "\n"


def md(text):
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip("\n").splitlines(keepends=True)}


def code(text):
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [],
            "source": text.strip("\n").splitlines(keepends=True)}


def notebook(cells, gpu=False):
    meta = {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"}}
    if gpu:
        meta["accelerator"] = "GPU"
        meta["colab"]["gpuType"] = "T4"
    return {"cells": cells, "metadata": meta, "nbformat": 4, "nbformat_minor": 0}


# (markdown, code) of Cells 3-9, shared by both notebooks
SHARED = [
    ("m03_geometry.md", "c03_geometry.py"),
    ("m04_depol.md", "c04_depol.py"),
    ("m05_pheno.md", "c05_pheno.py"),
    ("m06_cl.md", "c06_cl.py"),
    ("m07_tf.md", "c07_tf.py"),
    ("m08_protocol.md", "c08_protocol.py"),
    ("m09_dispatch.md", "c09_dispatch.py"),
]

RUN_MAIN_MD = """[Cell 10] 実行

`run_experiments()` は Cell 2 の `CFG` の 1 条件（`noise_model`, `dressing_treatment`）を実行します。
本番（3 雑音モデル × D4 と対照実験、同じ L・ショット数・交点付近の p）は次のセルの `run_production()` です。"""

RUN_MAIN = """results = run_experiments()"""

PROD_MD = """[Cell 11] 本番の一括実行（v9、R1-2・R1-4・R1-5）

長時間かかるので、雑音モデルごとに分けて実行し、終わるたびに `CFG["out_dir"]` を保存してください（Colab ではランタイムの終了で消えます）。
最後に D4 と対照実験の重ね描き `d4_v9_treatment_comparison_<model>_charge.png` を作ります。"""

PROD = """# 例: 1 モデルずつ（全部まとめるなら引数なし）
# prod = run_production(noise_models=["phenomenological"])
# prod = run_production(noise_models=["depolarizing"])
# prod = run_production(noise_models=["circuit_level"])
# 既にある CSV から重ね描きだけ作る:
# plot_treatment_comparison("phenomenological")"""

SAVE_MD = """[Cell 12] 出力の保存（任意）

`out_dir` を zip にまとめます。Colab ならブラウザにダウンロードします（Google Drive に保存する場合は、Drive をマウントしてコピーしてください）。"""

SAVE = """import shutil
os.makedirs(CFG["out_dir"], exist_ok=True)
zip_path = shutil.make_archive(CFG["out_dir"], "zip", CFG["out_dir"])
print("created", zip_path, sorted(os.listdir(CFG["out_dir"])))
try:
    from google.colab import files
    files.download(zip_path)
except ImportError:
    print("not running on Colab: download skipped")"""

RUN_VAL_MD = """[Cell 12] 実行（`VCFG["noise_models"]` の順に (A)(B)(C)(D)）"""

RUN_VAL = """vresults = {}
for _m in VCFG["noise_models"]:
    VCFG["noise_model"] = _m
    vresults[_m] = run_validation()"""


def build_main():
    nb = [md(read("m00_title_main.md")), md(read("m01_install.md")), code(code_src("c01_install_main.py")),
          md(read("m02_config_main.md")), code(code_src("c02_config_main.py"))]
    for m, c in SHARED:
        nb += [md(read(m)), code(code_src(c))]
    nb += [md(RUN_MAIN_MD), code(RUN_MAIN), md(PROD_MD), code(PROD), md(SAVE_MD), code(SAVE),
           md(read("m10_howto_main.md"))]
    return notebook(nb)


def build_val():
    nb = [md(read("v00_title_val.md")), md(read("v01_install.md")), code(code_src("v01_install_val.py")),
          md("[Cell 2] Setup & Config（メインと同一のソース）\n\n" + read("m02_config_main.md").split("\n", 1)[1]),
          code(code_src("c02_config_main.py")),
          md(read("v02_config_val.md")), code(code_src("v02_config_val.py"))]
    for m, c in SHARED:
        title = read(m).split("\n", 1)[0].strip()
        nb += [md(title + "（メインと同一のソース）"), code(code_src(c))]
    nb += [md(read("v10_dense.md")), code(code_src("v10_dense.py")),
           md(read("v11_run.md")), code(code_src("v11_run.py")),
           md(RUN_VAL_MD), code(RUN_VAL), md(read("v12_howto_val.md"))]
    return notebook(nb, gpu=True)


def script(which):
    """Plain-Python version of a notebook (for local tests; the !pip line is dropped)."""
    nb = build_main() if which == "main" else build_val()
    parts = []
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        src = "".join(c["source"])
        if src.lstrip().startswith("!"):
            continue
        parts.append(src)
    return "\n\n".join(parts) + "\n"


if __name__ == "__main__":
    out_main = os.path.join(OUT_DIR, "D4_v9_main.ipynb")
    out_val = os.path.join(OUT_DIR, "D4_v9_validation.ipynb")
    for path, nb in ((out_main, build_main()), (out_val, build_val())):
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(nb, fh, ensure_ascii=False, indent=1)
        print("wrote", path, len(nb["cells"]), "cells")
    if len(sys.argv) > 1 and sys.argv[1] == "--scripts":
        for which in ("main", "val"):
            p = os.path.join(sys.argv[2] if len(sys.argv) > 2 else ".", f"d4_v9_{which}_script.py")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(script(which))
            print("wrote", p)
