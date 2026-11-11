"""Figures of the integrated paper (v11) from the stored production data of the repository.

Run from the repository root:  python 論文草稿/統合論文_v12/scripts/make_figures.py
Inputs (read only):
  1_D4閾値/データ_v7本番/メインコード実行結果/9までやった(pheno)/d4_v7_X_memory_phenomenological_twisted_frame.csv
  2_CodeSwitching論理誤り率/本番結果/chsc_v9_results/chsc_v9_*.csv, chsc_v3_results/chsc_v3_in_T_out_ideal.csv
  3_魔法状態蒸留との比較/results_v12/data_intervals.csv
Outputs: 論文草稿/統合論文_v12/figures/fig_{memory,switching,epsK}.pdf
No simulation is run here.
"""
import os
import unicodedata

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "論文草稿", "統合論文_v12", "figures")
os.makedirs(OUT, exist_ok=True)

# categorical slots 1-4 of the reference palette (adjacent-pair validated); markers as secondary encoding
COL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MRK = ["o", "s", "^", "D", "v"]
INK, INK2, GRID = "#0b0b0b", "#52514e", "#d9d8d4"

plt.rcParams.update({
    "font.size": 7.5, "axes.labelsize": 7.5, "legend.fontsize": 6.5, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.linewidth": 0.6, "lines.linewidth": 1.2, "lines.markersize": 3.5, "pdf.fonttype": 42,
    "axes.spines.top": False, "axes.spines.right": False,
})


def _find_dir(parent, needle):
    """Folder names may be stored in NFD; match after NFC normalisation."""
    for name in os.listdir(parent):
        if needle in unicodedata.normalize("NFC", name) and os.path.isdir(os.path.join(parent, name)):
            return os.path.join(parent, name)
    raise FileNotFoundError(needle)


def _grid(ax):
    ax.grid(True, which="major", color=GRID, lw=0.4)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- Fig. memory (study 1, phenomenological)
def fig_memory():
    base = ROOT
    for part in ("1_D4閾値", "データ_v7本番", "メインコード実行結果"):
        base = os.path.join(base, _nfc_child(base, part))
    d = _find_dir(base, "(pheno)")
    df = pd.read_csv(os.path.join(d, "d4_v7_X_memory_phenomenological_twisted_frame.csv"))
    fig, ax = plt.subplots(figsize=(3.35, 2.25))
    for i, L in enumerate([3, 5, 7, 9]):
        s = df[df.L == L].sort_values("p")
        yerr = [s.ler_charge - s.ler_charge_lower, s.ler_charge_upper - s.ler_charge]
        ax.errorbar(100 * s.p, s.ler_charge, yerr=yerr, color=COL[i], marker=MRK[i], lw=1.2, capsize=1.5,
                    elinewidth=0.6, label=f"$L={L}$")
        ax.plot(100 * s.p, s.ler_flux.where(s.ler_flux > 0), color=COL[i], marker=MRK[i], lw=0.8, ls="--",
                mfc="white", alpha=0.9)
    ax.set_yscale("log")
    ax.set_xlabel("physical error rate $p$ (%)")
    ax.set_ylabel("failure probability")
    h, lab = ax.get_legend_handles_labels()
    h += [plt.Line2D([], [], color=INK2, lw=1.2), plt.Line2D([], [], color=INK2, lw=0.8, ls="--")]
    lab += [r"$P_{\rm charge}$", r"$P_{\rm flux}$"]
    ax.legend(h, lab, loc="lower right", frameon=False, ncol=3)
    _grid(ax)
    fig.tight_layout(pad=0.3)
    fig.savefig(os.path.join(OUT, "fig_memory.pdf"))
    plt.close(fig)


def _nfc_child(parent, target):
    for name in os.listdir(parent):
        if unicodedata.normalize("NFC", name) == unicodedata.normalize("NFC", target):
            return name
    raise FileNotFoundError(target)


# ---------------------------------------------------------------- Fig. switching (study 2)
def fig_switching():
    r2 = os.path.join(ROOT, _nfc_child(ROOT, "2_CodeSwitching論理誤り率"))
    res = os.path.join(r2, _nfc_child(r2, "本番結果"))
    files = {("in_only", "ideal"): "chsc_v9_results/chsc_v9_in_only_ideal.csv",
             ("in_only", "noisy"): "chsc_v9_results/chsc_v9_in_only_noisy.csv",
             ("in_out", "ideal"): "chsc_v9_results/chsc_v9_in_out_ideal.csv",
             ("in_out", "noisy"): "chsc_v9_results/chsc_v9_in_out_noisy.csv",
             ("in_T_out", "ideal"): "chsc_v3_results/chsc_v3_in_T_out_ideal.csv",
             ("in_T_out", "noisy"): "chsc_v9_results/chsc_v9_in_T_out_noisy.csv"}
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2), sharey=True)
    titles = {"in_only": "(a) in_only", "in_out": "(b) in_out (no U)", "in_T_out": "(c) in_T_out"}
    for ax, case in zip(axes, ["in_only", "in_out", "in_T_out"]):
        for bnd, ls, mfc in [("ideal", "-", None), ("noisy", "--", "white")]:
            df = pd.read_csv(os.path.join(res, files[(case, bnd)]))
            for i, dd in enumerate([3, 5, 7]):
                s = df[df.d == dd].sort_values("p")
                ax.errorbar(100 * s.p, s.P_L, yerr=[s.P_L - s.P_L_lower, s.P_L_upper - s.P_L], color=COL[i],
                            marker=MRK[i], ls=ls, mfc=mfc or COL[i], capsize=1.2, elinewidth=0.5,
                            label=f"$d={dd}$" if bnd == "ideal" else None)
        ax.set_xscale("log"); ax.set_yscale("log")
        ax.set_xticks([1, 2, 3, 5]); ax.set_xticklabels(["1", "2", "3", "5"])
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_title(titles[case], fontsize=7.5, color=INK)
        ax.set_xlabel("$p$ (%)")
        _grid(ax)
    axes[0].set_ylabel(r"$P_L=1-P(I)$")
    axes[0].legend(loc="lower right", frameon=False)
    axes[2].text(0.98, 0.04, "solid: ideal boundary\ndashed: noisy boundary", transform=axes[2].transAxes,
                 ha="right", va="bottom", color=INK2, fontsize=6.2)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(os.path.join(OUT, "fig_switching.pdf"))
    plt.close(fig)


# ---------------------------------------------------------------- Fig. eps_K (study 3)
def fig_epsK():
    r3 = os.path.join(ROOT, _nfc_child(ROOT, "3_魔法状態蒸留との比較"))
    di = pd.read_csv(os.path.join(r3, "results_v12", "data_intervals.csv"))
    di = di[di.window == "noisy"]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.3), sharey=True)
    ps = [1e-4, 2e-4, 3e-4, 5e-4, 1e-3]
    PLAB = [r"$p=10^{-4}$", r"$p=2\times10^{-4}$", r"$p=3\times10^{-4}$", r"$p=5\times10^{-4}$", r"$p=10^{-3}$"]
    for ax, sc, ttl in zip(axes, ["B", "A"], ["(a) scenario B (no idle noise)", "(b) scenario A (idle noise)"]):
        for i, p in enumerate(ps):
            s = di[(di.scenario == sc) & np.isclose(di.p, p)].sort_values("d")
            if s.empty:
                continue
            x = s.d + (i - 2) * 0.1
            y = s.eps.where(s.eps > 0)
            lo = np.maximum(s.lower_decision, 1e-7)
            ax.vlines(x, lo, s.upper_decision, color=COL[i], lw=0.8)
            ax.plot(x, y, color=COL[i], marker=MRK[i], lw=1.0, label=PLAB[i])
            z = s[s.eps <= 0]
            ax.plot(z.d + (i - 2) * 0.1, z.upper_decision, ls="none", marker="1", color=COL[i], ms=6)
        ax.axhline(1e-4, color=INK2, lw=0.7, ls=":")
        ax.text(2.62, 1.15e-4, r"target $10^{-4}$", ha="left", va="bottom", color=INK2, fontsize=6.2)
        ax.set_yscale("log"); ax.set_ylim(3e-6, 1.5)
        ax.set_xticks([3, 5, 7, 9]); ax.set_xlabel("$d$")
        ax.set_title(ttl, fontsize=7.5, color=INK)
        _grid(ax)
    axes[0].set_ylabel(r"output infidelity $\varepsilon_K$")
    axes[0].legend(loc="upper right", frameon=False, ncol=3, fontsize=6)
    fig.tight_layout(pad=0.3, w_pad=0.6)
    fig.savefig(os.path.join(OUT, "fig_epsK.pdf"))
    plt.close(fig)


if __name__ == "__main__":
    fig_memory()
    fig_switching()
    fig_epsK()
    print("figures written to", OUT)
