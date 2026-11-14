"""The two figures of study 3, drawn from the result CSVs of the comparison notebook (no computation).

    d4_logical_error.png   output error of D4 code switching vs physical error rate (data, intervals, fitted model)
    cost_comparison.png    output error vs space-time volume: D4 code switching against 15-to-1 distillation

Every number shown is read from the CSVs written by `noisy_cost_comparison.ipynb`
(`data_intervals`, `model_curves`, `factory_candidates`, `cost_comparison`); nothing is fitted or decided here.
The module is embedded in the notebook (its last cell calls `make_all`) and can be run alone:

    python figures_v13.py [--results results_v13] [--figures figures_v13] [--suffix ''] [--pdf]   -- a few seconds
"""
import argparse
import os

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

VERSION = "v13"

# Colours: categorical slots 1 and 2 of a palette validated for colour-vision deficiency (blue = D4 code switching,
# orange = distillation); the diagnostic is a counterfactual, not a result, and is drawn in neutral grey.
C_SWITCH, C_DISTILL, C_DIAG, C_REF = '#2a78d6', '#eb6834', '#7a7974', '#52514e'
C_SIZE = {3: '#86b6ef', 5: '#3987e5', 7: '#1c5cab', 9: '#0d366b'}      # one hue, light -> dark with the size d
M_SIZE = {3: 'o', 5: 's', 7: '^', 9: 'D'}                              # second encoding of d (not colour alone)
SURFACE, INK, INK2, GRID = '#ffffff', '#0b0b0b', '#52514e', '#e4e3df'
STYLE = {'figure.facecolor': SURFACE, 'axes.facecolor': SURFACE, 'savefig.facecolor': SURFACE,
         'axes.edgecolor': INK2, 'axes.labelcolor': INK, 'text.color': INK, 'xtick.color': INK2, 'ytick.color': INK2,
         'axes.grid': True, 'axes.axisbelow': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
         'axes.spines.top': False, 'axes.spines.right': False, 'font.size': 10, 'axes.titlesize': 10,
         'axes.labelsize': 10, 'legend.frameon': False, 'legend.fontsize': 8.5, 'mathtext.default': 'regular'}
SCENARIO_TEXT = {'A': 'with idle noise ($p_{idle} = p$)', 'B': 'no idle noise ($p_{idle} = 0$)'}
INTERVAL_TEXT = '95% confidence interval, simultaneous over the sizes $d$ at that $p$'
DODGE = 0.022      # markers of different d at the same p are separated by this many decades of p (display only)


def load(results, suffix=''):
    """The four result tables the figures are drawn from."""
    read = lambda name: pd.read_csv(os.path.join(results, f'{name}{suffix}.csv'))
    return dict(intervals=read('data_intervals'), curves=read('model_curves'),
                factories=read('factory_candidates'), comparison=read('cost_comparison'))


def sci(x):
    """1e-4 -> $10^{-4}$, 3e-4 -> $3\\times10^{-4}$ (mathtext)."""
    exponent = int(np.floor(np.log10(x) + 1e-9))
    mantissa = x / 10.0 ** exponent
    if abs(mantissa - 1) < 1e-9:
        return rf'$10^{{{exponent}}}$'
    return rf'${mantissa:g}\times10^{{{exponent}}}$'


def same(series, value):
    return np.isclose(series, value, rtol=1e-9, atol=0)


def standard_points(intervals, scenario, window):
    """Simulated points with the standard numbers of rounds (kappa = 1), one row per (d, p)."""
    k1 = (intervals.kappa0 == 1) & (intervals.kappa_in == 1) & (intervals.kappa_out == 1)
    return intervals[k1 & (intervals.scenario == scenario) & (intervals.window == window)].sort_values(['d', 'p'])


def pareto_front(candidates):
    """Candidates that are not beaten in both volume and output error, by increasing volume."""
    best, keep = np.inf, []
    for index, row in candidates.sort_values(['volume_steps', 'eps']).iterrows():
        if row.eps < best:
            best = row.eps
            keep.append(index)
    return candidates.loc[keep]


def draw_points(ax, x, rows, color, marker, size=6.5, zorder=4):
    """Estimate with its interval; a point without any failure is an open triangle at the upper end of the interval."""
    x = np.asarray(x, float)
    seen = (rows.s > 0).to_numpy()
    if seen.any():
        r = rows[seen]
        ax.errorbar(x[seen], r.eps, yerr=[r.eps - r.lower_decision, r.upper_decision - r.eps], fmt='none',
                    ecolor=color, elinewidth=1.1, capsize=2.2, capthick=1.1, zorder=zorder)
        ax.plot(x[seen], r.eps, marker, color=color, ms=size, mec=SURFACE, mew=0.9, ls='none', zorder=zorder + 1)
    if (~seen).any():
        r = rows[~seen]
        ax.plot(x[~seen], r.upper_decision, 'v', color=color, ms=size + 0.5, mfc=SURFACE, mew=1.3, ls='none',
                zorder=zorder + 1)


def fig_logical_error(frames):
    """2 x 2 panels: rows = full simulation / diagnostic (switching window noise-free), columns = scenario."""
    intervals, curves = frames['intervals'], frames['curves']
    curves = curves[curves.curve == 'vs_p']
    scenarios = sorted(intervals.scenario.unique())
    windows = [('noisy', 'full simulation'), ('quiet', 'diagnostic: switching window noise-free')]
    sizes = sorted(intervals.d.unique())
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(2, len(scenarios), figsize=(5.4 * len(scenarios), 8.2), sharex=True, sharey=True,
                                 squeeze=False)
        for i, (window, window_text) in enumerate(windows):
            for j, scenario in enumerate(scenarios):
                ax = axes[i, j]
                points = standard_points(intervals, scenario, window)
                for k, d in enumerate(sizes):
                    color, marker = C_SIZE.get(d, INK), M_SIZE.get(d, 'o')
                    line = curves[(curves.scenario == scenario) & (curves.window == window) & (curves.d == d)
                                  & curves.in_fit_domain].sort_values('p')
                    if len(line):
                        ax.plot(line.p, line.eps_model, '-', color=color, lw=1.3, alpha=0.9, zorder=3)
                    rows = points[points.d == d]
                    draw_points(ax, rows.p * 10.0 ** (DODGE * (k - (len(sizes) - 1) / 2)), rows, color, marker)
                p_line = np.array([curves.p.min(), curves.p.max()])
                ax.plot(p_line, p_line, ':', color=C_REF, lw=1.1, zorder=2)
                ax.set_xscale('log'); ax.set_yscale('log')
                ax.set_title(f'Scenario {scenario}, {window_text}', loc='left')
                fitted = sorted(curves[(curves.scenario == scenario) & (curves.window == window)
                                       & curves.in_fit_domain].d.unique())
                note = (f'curves: model fitted to $d \\geq {fitted[0]}$\n(the curves of $d$ = '
                        + ', '.join(str(d) for d in fitted) + ' nearly coincide)') if window == 'noisy' and fitted else \
                    'curves: model of the errors outside the window'
                ax.text(0.97, 0.04, note, transform=ax.transAxes, ha='right', va='bottom', fontsize=8, color=INK2)
                if i == 1:
                    ax.set_xlabel('physical error rate $p$')
                if j == 0:
                    ax.set_ylabel(r'output error of one $T$ state, $\varepsilon_K(d, p)$')
        low = intervals.lower_decision[intervals.lower_decision > 0].min()
        axes[0, 0].set_ylim(10.0 ** np.floor(np.log10(low)), 1.0)
        axes[0, 0].set_xlim(curves.p.min(), curves.p.max())
        handles = [Line2D([], [], marker=M_SIZE.get(d, 'o'), color=C_SIZE.get(d, INK), mec=SURFACE, mew=0.9, ms=7,
                          lw=1.3, label=f'$d$ = {d}') for d in sizes]
        handles += [Line2D([], [], marker='v', color=INK2, mfc=SURFACE, mew=1.3, ms=7, ls='none',
                           label='no failure observed: upper end of the interval'),
                    Line2D([], [], ls=':', color=C_REF, lw=1.1, label=r'$\varepsilon_K = p$')]
        fig.legend(handles=handles, loc='upper center', ncol=len(handles), bbox_to_anchor=(0.5, 0.945),
                   handletextpad=0.5, columnspacing=1.6)
        fig.suptitle('D4 code switching: markers = simulation (bars: ' + INTERVAL_TEXT + '), curves = fitted model\n'
                     f'markers of different $d$ at the same $p$ are drawn side by side (shifted by up to '
                     f'{100 * (10 ** (DODGE * (len(sizes) - 1) / 2) - 1):.0f}% in $p$)', fontsize=9.5, y=0.995)
        fig.tight_layout(rect=(0, 0, 1, 0.955))
    return fig


def target_note(row):
    """What the comparison table says about one row (one scenario, p and target); no decision is made here."""
    head = f'for $\\varepsilon \\leq$ {sci(row.target)}:  '
    if row.kobayashi_status == 'data_certified':
        tail = '' if row.kobayashi_minimum_resolved else ' (smaller $d$ not excluded)'
        return head + f'$d$ = {int(row.kobayashi_d)} certified by data,\n' \
                      f'{row.ratio_kobayashi_over_litinski:.2f}$\\times$ the distillation volume' + tail
    return head + f'no $d \\leq 9$ certified;\n$d \\geq {int(row.kobayashi_d_low)}$ costs $\\geq$ ' \
                  f'{row.ratio_kobayashi_low_over_litinski:.2f}$\\times$ the distillation volume'


def fig_cost_comparison(frames, show_p=(1e-4, 3e-4, 1e-3), target=1e-4, y_min=1e-12):
    """rows = scenario, columns = p: output error against space-time volume (lower left is better)."""
    intervals, curves = frames['intervals'], frames['curves']
    factories, comparison = frames['factories'], frames['comparison']
    curves = curves[curves.curve == 'vs_d']
    scenarios = sorted(intervals.scenario.unique())
    volume_of = curves.drop_duplicates('d').set_index('d').volume
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(len(scenarios), len(show_p), figsize=(4.3 * len(show_p), 3.75 * len(scenarios) + 0.9),
                                 sharex=True, sharey=True, squeeze=False)
        for i, scenario in enumerate(scenarios):
            for j, p in enumerate(show_p):
                ax = axes[i, j]
                ax.axhline(p, color=C_REF, ls=':', lw=1.0, zorder=2)
                front = pareto_front(factories[(factories.scenario == scenario) & same(factories.p, p)])
                ax.step(front.volume_steps, front.eps, where='post', color=C_DISTILL, lw=2.0, zorder=3)
                here = curves[(curves.scenario == scenario) & same(curves.p, p)].sort_values('d')
                diagnostic = here[here.window == 'quiet']
                ax.plot(diagnostic.volume, diagnostic.eps_model, '--', color=C_DIAG, lw=1.4, dashes=(5, 2.5), zorder=3)
                model = here[(here.window == 'noisy') & here.in_fit_domain]
                inside = model[~model.d_extrapolated]
                outside = model[model.d >= inside.d.max()] if len(inside) else model
                ax.plot(inside.volume, inside.eps_model, '-', color=C_SWITCH, lw=1.3, zorder=4)
                ax.plot(outside.volume, outside.eps_model, '-', color=C_SWITCH, lw=1.3, dashes=(2.2, 1.6), zorder=4)
                points = standard_points(intervals, scenario, 'noisy')
                points = points[same(points.p, p)]
                x = points.d.map(volume_of).to_numpy()
                draw_points(ax, x, points, C_SWITCH, 'o', size=7.5)
                for k, (xv, (_, r)) in enumerate(zip(x, points.iterrows())):
                    top = r.upper_decision
                    ax.annotate(f'$d$={int(r.d)}' if k == 0 else f'{int(r.d)}', (xv, top), xytext=(0, 5 if r.s > 0 else 7),
                                textcoords='offset points', ha='center', va='bottom', fontsize=8, color=INK2)
                ax.set_xscale('log'); ax.set_yscale('log')
                ax.set_title(f'Scenario {scenario},  $p$ = {sci(p)}', loc='left', pad=33)
                row = comparison[(comparison.scenario == scenario) & same(comparison.p, p) & same(comparison.target, target)]
                if len(row) == 1:
                    ax.text(0, 1.02, target_note(row.iloc[0]), transform=ax.transAxes, ha='left', va='bottom',
                            fontsize=8, color=INK2, linespacing=1.3).set_in_layout(False)
                if j == len(show_p) - 1:
                    ax.annotate(r'$\varepsilon = p$', (1, p), xycoords=('axes fraction', 'data'), xytext=(-3, -3),
                                textcoords='offset points', ha='right', va='top', fontsize=8, color=INK2)
                if j == 0:
                    ax.set_ylabel(f'Scenario {scenario}: {SCENARIO_TEXT.get(scenario, "")}\n'
                                  r'output error of one $T$ state, $\varepsilon$')
                if i == len(scenarios) - 1:
                    ax.set_xlabel('space-time volume  [physical qubits $\\times$ time steps]')
        axes[0, 0].set_ylim(y_min, 1.0)
        axes[0, 0].set_xlim(1e4, 3e8)
        handles = [
            Line2D([], [], color=C_DISTILL, lw=2.0, label='15-to-1 distillation: best factories (Pareto front of the candidates)'),
            Line2D([], [], marker='o', color=C_SWITCH, mec=SURFACE, mew=0.9, ms=7.5, lw=1.1,
                   label='D4 code switching: simulation, $d$ = 3–9 (bars: 95% confidence interval)'),
            Line2D([], [], marker='v', color=C_SWITCH, mfc=SURFACE, mew=1.3, ms=7.5, ls='none',
                   label='D4 code switching: no failure observed (upper end of the interval)'),
            Line2D([], [], color=C_SWITCH, lw=1.3, dashes=(2.2, 1.6),
                   label='D4 code switching: model extrapolated to $d$ > 9 (fitted to $d \\geq 7$)'),
            Line2D([], [], color=C_DIAG, lw=1.4, dashes=(5, 2.5),
                   label='diagnostic: model with a noise-free switching window (not a bound)')]
        fig.legend(handles=handles, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 0.995), columnspacing=2.0)
        fig.tight_layout(rect=(0, 0, 1, 0.9))
    return fig


def make_all(results='results_v13', figures='figures_v13', suffix='', pdf=False, show=False, dpi=200):
    """Read the CSVs in `results` and write both figures to `figures`; returns the list of files written."""
    frames = load(results, suffix)
    os.makedirs(figures, exist_ok=True)
    written = []
    for name, draw in (('d4_logical_error', fig_logical_error), ('cost_comparison', fig_cost_comparison)):
        fig = draw(frames)
        for ext in ('png', 'pdf') if pdf else ('png',):
            path = os.path.join(figures, f'{name}{suffix}.{ext}')
            fig.savefig(path, dpi=dpi, facecolor=SURFACE)     # independent of the caller's rcParams
            written.append(path)
        if show:
            plt.show()
        else:
            plt.close(fig)
    return written


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--results', default='results_v13')
    parser.add_argument('--figures', default='figures_v13')
    parser.add_argument('--suffix', default='')
    parser.add_argument('--pdf', action='store_true', help='also write vector PDFs')
    args = parser.parse_args()
    matplotlib.use('Agg')
    for path in make_all(args.results, args.figures, args.suffix, args.pdf):
        print('wrote', path)
