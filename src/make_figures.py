"""
make_figures.py
===============
analysis.run() 결과로 보고서/노트북용 그림(물리 저널 스타일, 영어 라벨)과
LaTeX 표 조각을 생성한다. 그림 제목은 넣지 않고(저널 관례) LaTeX \\caption 이
설명을 담당하며, 다중 패널은 (a)(b)(c) 로 표기한다.

출력: figures/*.png, report/results_table.tex, report/validity_table.tex, report/results.json
Team solvE · Group 14
"""
import os, json
import numpy as np
import pandas as pd

import analysis as A
from analysis import (plt, PALETTE, CASES, MODELS, MODEL_LABEL,
                      load_segment, fit_all, simulate, _abs, I_DOOR)
from friction_models import MODELS as M

FIG = _abs("figures")
REP = _abs("report")
os.makedirs(FIG, exist_ok=True)
os.makedirs(REP, exist_ok=True)

XLAB = r"Time $t$ (s)"
YLAB = r"Angular velocity $\omega$ (rad s$^{-1}$)"


def _panel(ax, letter):
    ax.text(0.025, 0.96, f"({letter})", transform=ax.transAxes,
            va="top", ha="left", fontweight="bold", fontsize=10)


def fig_overview():
    """Fig 1: full traces with the free-rotation window shaded."""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.7))
    for ax, lett, (name, cfg) in zip(axes, "ab", CASES.items()):
        d = pd.read_csv(_abs(cfg["csv"]))
        t, w = d["Time (s)"].values, d["Absolute (rad/s)"].values
        ax.plot(t, w, lw=0.4, color="#888")
        ax.axvspan(cfg["win"][0], cfg["win"][1], color=cfg["color"], alpha=0.18,
                   label="free-rotation window")
        ax.set_xlabel(XLAB); ax.set_ylabel(YLAB)
        ax.legend(loc="upper right", fontsize=7)
        _panel(ax, lett)
        ax.set_title(cfg["label"], fontsize=9)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig1_overview.png"); plt.close(fig)


def fig_fits(name, cfg, res):
    """Fig: measured data + six model fits for one slam."""
    t, w = load_segment(cfg["csv"], cfg["win"])
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    ax.scatter(t, w, s=4, color="#444", alpha=0.30, label="measured", zorder=1)
    tt = np.linspace(t.min(), t.max(), 400)
    for key in MODELS:
        r = res[key]
        if not r.get("ok"):
            continue
        fn = M[key]["fn"]
        p = [r["params"]["w0"]] + [r["params"][c] for c in M[key]["coeffs"]]
        best = key == cfg["best"]
        ax.plot(tt, fn(tt, *p), lw=1.8 if best else 1.0, ls="-" if best else "--",
                color=PALETTE[key], zorder=3,
                label=f"{MODEL_LABEL[key]} ($R^2$={r['R2']:.3f})")
    ax.set_xlabel(XLAB); ax.set_ylabel(YLAB)
    ax.legend(fontsize=6.0, loc="best", handlelength=1.6)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig_fit_{name}.png"); plt.close(fig)


def fig_gof(out):
    """Fig 3: R^2 and Delta-AIC per model."""
    fig, axes = plt.subplots(1, 2, figsize=(6.6, 2.8))
    keys = list(MODELS.keys()); x = np.arange(len(keys)); wd = 0.38
    for j, (name, cd) in enumerate(out["cases"].items()):
        r2 = [cd["fits"][k]["R2"] for k in keys]
        axes[0].bar(x + (j - 0.5) * wd, r2, wd, label=cd["label"],
                    color=CASES[name]["color"], alpha=0.85)
    axes[0].set_xticks(x); axes[0].set_xticklabels(keys)
    axes[0].set_ylabel(r"$R^2$"); axes[0].set_ylim(0.7, 1.0)
    axes[0].legend(fontsize=7); _panel(axes[0], "a")
    axes[0].set_title("coefficient of determination", fontsize=8.5)
    for j, (name, cd) in enumerate(out["cases"].items()):
        aic = np.array([cd["fits"][k]["AIC"] for k in keys])
        axes[1].bar(x + (j - 0.5) * wd, aic - aic.min(), wd, label=cd["label"],
                    color=CASES[name]["color"], alpha=0.85)
    axes[1].set_xticks(x); axes[1].set_xticklabels(keys)
    axes[1].set_ylabel(r"$\Delta$AIC"); axes[1].legend(fontsize=7)
    _panel(axes[1], "b")
    axes[1].set_title("information criterion (0 = best)", fontsize=8.5)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig3_gof.png"); plt.close(fig)


def fig_simulation(out):
    """Fig 4: analytic solution vs solve_ivp (validation)."""
    name = "slow"; cfg = CASES[name]; cd = out["cases"][name]; best = cd["best"]
    p = cd["fits"][best]["params"]; w0 = p["w0"]
    A_ = p.get("A", 0.0); B_ = p.get("B", 0.0); C_ = p.get("C", 0.0)
    t, w = load_segment(cfg["csv"], cfg["win"]); tt = np.linspace(0, t.max(), 500)
    fn = M[best]["fn"]
    analytic = fn(tt, *([w0] + [p[c] for c in M[best]["coeffs"]]))
    numeric = simulate(tt, w0, A=A_, B=B_, C=C_)
    err = float(np.max(np.abs(analytic - numeric)))
    fig, ax = plt.subplots(figsize=(3.7, 2.9))
    ax.scatter(t, w, s=4, color="#bbb", alpha=0.4, label="measured")
    ax.plot(tt, analytic, lw=1.8, color="#1f5e5b",
            label=f"analytic ({MODEL_LABEL[best]})")
    ax.plot(tt, numeric, lw=1.1, ls=":", color="#d1495b", label="numerical (solve_ivp)")
    ax.set_xlabel(XLAB); ax.set_ylabel(YLAB); ax.legend(fontsize=7)
    ax.text(0.03, 0.06, f"max difference $=$ {err:.1e} rad s$^{{-1}}$",
            transform=ax.transAxes, fontsize=7, color="#555")
    fig.tight_layout(); fig.savefig(f"{FIG}/fig4_simulation.png"); plt.close(fig)
    return err


def fig_validity(out):
    """Fig 5: fitted coefficients vs order-of-magnitude estimates."""
    pv = out["physical_validity"]; th = pv["theory"]
    names = list(out["cases"].keys())
    cols = [CASES[n]["color"] for n in names]
    labs = [CASES[n]["label"] for n in names]
    fig, ax = plt.subplots(1, 3, figsize=(6.6, 2.7)); x = np.arange(len(names))

    cI = [pv["cases"][n]["cI"] for n in names]
    ax[0].bar(x, cI, color=cols, alpha=0.85)
    ax[0].axhline(th["cI_Newton"], color="#1f5e5b", ls="--", lw=1.5,
                  label=f"estimate $\\approx${th['cI_Newton']:.2f}")
    ax[0].set_ylabel(r"$c/I$"); ax[0].legend(fontsize=7)
    ax[0].set_title("Newton: matches", fontsize=8.5); _panel(ax[0], "a")

    bI = [pv["cases"][n]["bI"] for n in names]
    ax[1].bar(x, bI, color=cols, alpha=0.85)
    ax[1].axhline(th["bI_Stokes"], color="#d1495b", ls="--", lw=1.5,
                  label=f"estimate $\\approx${th['bI_Stokes']:.0e}")
    ax[1].set_yscale("log"); ax[1].set_ylabel(r"$b/I$ (s$^{-1}$)")
    ax[1].legend(fontsize=7); ax[1].set_title(r"Stokes: $10^3$–$10^4\times$ off", fontsize=8.5)
    _panel(ax[1], "b")

    mu = [pv["cases"][n]["mu_implied"] for n in names]
    ax[2].bar(x, mu, color=cols, alpha=0.85)
    ax[2].set_ylabel(r"implied $\mu$")
    ax[2].set_title(f"Dry: {pv['mu_inconsistency']:.0f}$\\times$ inconsistent", fontsize=8.5)
    _panel(ax[2], "c")
    for xi, m in zip(x, mu):
        ax[2].text(xi, m, f"{m:.4f}", ha="center", va="bottom", fontsize=7)

    for a in ax:
        a.set_xticks(x); a.set_xticklabels(labs, fontsize=7.5)
    fig.tight_layout(); fig.savefig(f"{FIG}/fig5_validity.png"); plt.close(fig)


# ----------------------------------------------------------------------
# LaTeX 표
# ----------------------------------------------------------------------
def latex_validity_table(out):
    pv = out["physical_validity"]; th = pv["theory"]
    cf = pv["cases"]["fast"]; cs = pv["cases"]["slow"]
    L = [r"\begin{table}[h]\centering",
         r"\caption{Order-of-magnitude validity of the fitted friction coefficients (cf. Klein et al.).}",
         r"\label{tab:validity}",
         r"\begin{tabular}{llll}", r"\toprule",
         r"Coefficient & Fitted (fast / slow) & Theoretical estimate & Verdict \\", r"\midrule",
         rf"$a/I$ (Dry) & {cf['aI']:.3f} / {cs['aI']:.3f} & $3\mu g/w$, "
         rf"$\mu$={cf['mu_implied']:.3f}/{cs['mu_implied']:.4f} & "
         rf"Rejected ($\mu$ {pv['mu_inconsistency']:.0f}$\times$ inconsistent) \\",
         rf"$b/I$ (Stokes) & {cf['bI']:.3f} / {cs['bI']:.3f} & "
         rf"$\sim 6\times10^{{-5}}$ & Rejected ($10^3$--$10^4\times$ too large) \\",
         rf"$c/I$ (Newton) & {cf['cI']:.3f} / {cs['cI']:.3f} & "
         rf"$\lesssim {th['cI_Newton']:.2f}$ & \textbf{{Accepted (same order)}} \\",
         r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    with open(f"{REP}/validity_table.tex", "w") as f:
        f.write("\n".join(L))


def latex_table(out):
    lines = []
    for name, cd in out["cases"].items():
        lines += [f"% --- {cd['label']} (window {cd['win'][0]}-{cd['win'][1]} s, n={cd['n']}) ---",
                  r"\begin{table}[h]\centering",
                  r"\caption{Fitting parameters and goodness-of-fit --- " + name + r" slam.}",
                  rf"\label{{tab:fits_{name}}}",
                  r"\begin{tabular}{lcccccc}", r"\toprule",
                  r"Model & $a/I$ & $b/I$ & $c/I$ & $R^2$ & SSE & $\Delta$AIC \\", r"\midrule"]
        aic_min = min(cd["fits"][k]["AIC"] for k in MODELS)
        for k in MODELS:
            f = cd["fits"][k]; p = f["params"]
            a = f"{p['A']:.4g}" if "A" in p else "--"
            b = f"{p['B']:.4g}" if "B" in p else "--"
            c = f"{p['C']:.4g}" if "C" in p else "--"
            st = r"\textbf{" if k == cd["best"] else ""; en = "}" if k == cd["best"] else ""
            lines.append(f"{st}{k}{en} & {a} & {b} & {c} & {f['R2']:.4f} & {f['SSE']:.4g} & {f['AIC']-aic_min:.1f} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    with open(f"{REP}/results_table.tex", "w") as f:
        f.write("\n".join(lines))


def latex_validity_table_ko(out):
    pv = out["physical_validity"]; th = pv["theory"]
    cf = pv["cases"]["fast"]; cs = pv["cases"]["slow"]
    L = [r"\begin{table}[h]\centering",
         r"\caption{적합 계수의 차원분석 타당성 (Klein et al. 참조).}",
         r"\label{tab:validity}",
         r"\begin{tabular}{llll}", r"\toprule",
         r"계수 & 적합값 (빠름 / 느림) & 이론 추정 & 판정 \\", r"\midrule",
         rf"$a/I$ (건마찰) & {cf['aI']:.3f} / {cs['aI']:.3f} & $3\mu g/w$, "
         rf"$\mu$={cf['mu_implied']:.3f}/{cs['mu_implied']:.4f} & "
         rf"기각 ($\mu$ {pv['mu_inconsistency']:.0f}배 불일치) \\",
         rf"$b/I$ (스토크스) & {cf['bI']:.3f} / {cs['bI']:.3f} & "
         rf"$\sim 6\times10^{{-5}}$ & 기각 ($10^3$--$10^4$배 과대) \\",
         rf"$c/I$ (뉴턴) & {cf['cI']:.3f} / {cs['cI']:.3f} & "
         rf"$\lesssim {th['cI_Newton']:.2f}$ & \textbf{{채택 (같은 자릿수)}} \\",
         r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    with open(f"{REP}/validity_table_ko.tex", "w") as f:
        f.write("\n".join(L))


def latex_table_ko(out):
    ko = {"fast": "빠른 슬램", "slow": "느린 슬램"}
    lines = []
    for name, cd in out["cases"].items():
        lines += [r"\begin{table}[h]\centering",
                  r"\caption{적합 파라미터 및 적합도 --- " + ko[name] + r".}",
                  rf"\label{{tab:fits_{name}}}",
                  r"\begin{tabular}{lcccccc}", r"\toprule",
                  r"모델 & $a/I$ & $b/I$ & $c/I$ & $R^2$ & SSE & $\Delta$AIC \\", r"\midrule"]
        aic_min = min(cd["fits"][k]["AIC"] for k in MODELS)
        for k in MODELS:
            f = cd["fits"][k]; p = f["params"]
            a = f"{p['A']:.4g}" if "A" in p else "--"
            b = f"{p['B']:.4g}" if "B" in p else "--"
            c = f"{p['C']:.4g}" if "C" in p else "--"
            st = r"\textbf{" if k == cd["best"] else ""; en = "}" if k == cd["best"] else ""
            lines.append(f"{st}{k}{en} & {a} & {b} & {c} & {f['R2']:.4f} & {f['SSE']:.4g} & {f['AIC']-aic_min:.1f} \\\\")
        lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}", ""]
    with open(f"{REP}/results_table_ko.tex", "w") as f:
        f.write("\n".join(lines))


def main():
    out = A.run()
    fig_overview()
    for name, cfg in CASES.items():
        t, w = load_segment(cfg["csv"], cfg["win"])
        res, best = fit_all(t, w)
        cfg["best"] = best; out["cases"][name]["best"] = best
        fig_fits(name, cfg, res)
    fig_gof(out)
    sim_err = fig_simulation(out)
    fig_validity(out)
    latex_table(out); latex_validity_table(out)
    latex_table_ko(out); latex_validity_table_ko(out)
    with open(f"{REP}/results.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    pv = out["physical_validity"]
    print("=== done ===")
    for name, cd in out["cases"].items():
        c = pv["cases"][name]
        print(f"{name:5s}: AIC-best={cd['best']}  R2(N)={cd['fits']['N']['R2']:.4f}  "
              f"c/I={c['cI']:.3f}(est {pv['theory']['cI_Newton']:.2f})  mu={c['mu_implied']:.4f}")
    print(f"Dry mu inconsistency: {pv['mu_inconsistency']:.1f}x  | sim err {sim_err:.1e}")
    print("figs:", sorted(os.listdir(FIG)))


if __name__ == "__main__":
    main()
