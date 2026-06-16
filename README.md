<div align="center">

# 🚪 Rotational and Frictional Dynamics of a Slamming Door

**Reproducing Klein _et al._ (Am. J. Phys. 85, 30, 2017) with a smartphone gyroscope**

<p>
<a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white"></a>
<img src="https://img.shields.io/badge/SciPy-curve__fit%20%2B%20solve__ivp-8CAAE6?logo=scipy&logoColor=white">
<img src="https://img.shields.io/badge/Matplotlib-SciencePlots-11557C">
<img src="https://img.shields.io/badge/LaTeX-report-008080?logo=latex&logoColor=white">
<a href="https://doi.org/10.1119/1.4964134"><img src="https://img.shields.io/badge/AJP-10.1119%2F1.4964134-b31b1b"></a>
</p>

**English** · [한국어](README.ko.md)

<em>Team solvE (Group 14) · DGIST General Physics</em>

</div>

---

## Overview

When a door is slammed it rotates about its hinges, decelerates, and stops. Klein _et al._
asked which of three friction laws governs that motion, the constant (**dry**), the linear
(**Stokes**), or the quadratic (**Newtonian air drag**) one. We reproduce their study on a
real door. The angular velocity $\omega(t)$ is measured **directly with a smartphone
gyroscope**, so the $\omega=\sqrt{a_r/r}$ conversion used in the original paper is not
needed. All six friction models are fitted to the data, and the analytical solutions are
checked against a numerical integration of the equation of motion.

The main lesson of the paper is that **a good fit does not prove a model**. What settles the
question is whether each fitted coefficient is physically reasonable.

## Key Result

> Judged by the **physical plausibility** of the fitted coefficients (not by $R^2$),
> Stokes and dry friction are rejected, and **Newtonian $\omega^2$ air drag is the only
> consistent mechanism**. This agrees with the original paper.

| Coefficient | Fitted (fast / slow) | Physical estimate | Verdict |
|---|---|---|---|
| $a/I$ (Dry) | 1.09 / 0.12 → μ = 0.031 / 0.0034 | $3\mu g/w$ | ❌ μ inconsistent by 9× |
| $b/I$ (Stokes) | 0.54 / 0.29 | $\sim 6\times10^{-5}$ | ❌ $10^3$–$10^4$× too large |
| $c/I$ (Newton) | 0.27 / 0.68 | $\lesssim 0.30$ | ✅ **same order — accepted** |

<div align="center">
<img src="figures/fig5_validity.png" width="85%">
</div>

- A nested **F-test** on the slow slam rejects a purely linear (dry) law, with $F_{D\to DN}\approx4\times10^{3}$ ($p<0.001$).
- The analytic solutions match a direct `solve_ivp` integration to about $10^{-8}$ rad/s.

## Repository Structure

```
physics-door-slam/
├── data/                     # raw gyroscope data (fast / slow) + setup
├── src/
│   ├── friction_models.py    # 6 analytic solutions + solve_ivp simulation
│   ├── analysis.py           # window extraction · curve_fit · R²/SSE/AIC · validity
│   └── make_figures.py       # journal-style figures + LaTeX tables
├── notebooks/analysis.ipynb  # full walkthrough (renders inline on GitHub)
├── figures/                  # generated PNGs (300 DPI)
└── report/                   # LaTeX report (EN + KO) and compiled PDFs
```

## Getting Started

```bash
pip install -r requirements.txt

# regenerate all figures and LaTeX tables
cd src && python make_figures.py

# or open the notebook
jupyter notebook notebooks/analysis.ipynb
```

The report is built with [Tectonic](https://tectonic-typesetting.github.io/) (XeTeX):

```bash
cd report && tectonic report.tex      # English
                tectonic report_ko.tex  # Korean
```

## How it works

1. **Measure.** Phyphox gyroscope on a real door, two slams (large and small spin), about 460 Hz.
2. **Segment.** Fit only the free-rotation phase and drop the near-frame air-cushion spike.
3. **Fit.** Six friction models with `scipy.optimize.curve_fit`, reporting $R^2$, SSE, and AIC.
4. **Validate.** Compare the fitted $a/I, b/I, c/I$ with order-of-magnitude physical estimates.
5. **Simulate.** Integrate the equation of motion with `solve_ivp` to check the analytics.

## Team

| Member | Role |
|---|---|
| Eunwoo Chae | Data analysis · GitHub · Report (LaTeX) |
| Seongmin Kang | Report (LaTeX) · Simulation |
| Minseok Jang | Experiment · Data acquisition |
| Solbi Joo | Presentation · Video |

## Reference

P. Klein, A. Müller, S. Gröber, A. Molz, J. Kuhn,
_"Rotational and frictional dynamics of the slamming of a door,"_
**Am. J. Phys. 85, 30–37 (2017).** [doi:10.1119/1.4964134](https://doi.org/10.1119/1.4964134)
