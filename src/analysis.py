"""
analysis.py
===========
Phyphox 자이로스코프로 측정한 문 슬램 데이터를 6개 마찰 모델로 적합(fit)하고,
적합도(R², SSE, AIC)를 계산해 보고서·노트북에서 쓸 결과/그림을 생성한다.

- 자이로스코프는 각속도 ω(t)를 직접 측정 → 논문의 ω=√(aᵣ/r) 변환 불필요.
- 자유회전(감속) 구간만 잘라 적합한다. 충돌(임팩트) 진동 구간은 제외.

Team solvE · Group 14 · DGIST General Physics
"""
import os, json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

# repo 루트 (이 파일은 src/ 에 있음) — CSV·그림 경로를 루트 기준으로 해석
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def _abs(p):
    return p if os.path.isabs(p) else os.path.join(REPO_ROOT, p)

from friction_models import MODELS, MODEL_LABEL, simulate

# ----------------------------------------------------------------------
# 0. 그림 스타일: 물리 저널 스타일(SciencePlots, 영어 라벨)
#    no-latex 변형 — 시스템 LaTeX 없이 mathtext 로 렌더.
# ----------------------------------------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import scienceplots  # noqa: F401  (스타일 등록)

plt.style.use(["science", "no-latex"])
plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "axes.unicode_minus": False,
    "font.size": 9,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
})

# 모델 색 (저널풍: 무채색 데이터 + 구분되는 라인색)
C_DATA = "#333333"
PALETTE = {
    "D":  "#d1495b",   # red
    "S":  "#edae49",   # amber
    "N":  "#1f5e5b",   # teal (Newton, 결론)
    "DS": "#8a4f7d",   # purple
    "DN": "#00798c",   # blue-teal
    "SN": "#6b6b6b",   # grey
}
CASE_COLOR = {"fast": "#d1495b", "slow": "#1f5e5b"}

# ----------------------------------------------------------------------
# 1. 실험 상수 (실험세팅값.md)
# ----------------------------------------------------------------------
M_DOOR = 13.7          # kg
W_DOOR = 0.833         # m (가로)
H_DOOR = 2.031         # m (세로)
R_PHONE = 0.759        # m (회전축~스마트폰)
I_DOOR = (1.0 / 3.0) * M_DOOR * W_DOOR ** 2     # 얇은 판 근사 I=⅓mw²

# 차원(order-of-magnitude) 추정용 물리 상수 (논문 Table IV)
G_ACC = 9.8        # m/s²
RHO_AIR = 1.3      # kg/m³  공기 밀도
ETA_AIR = 1.7e-5   # Pa·s   공기 점성
CD_PLATE = 1.5     # 직사각판 항력계수 (1~2)
A_DOOR = H_DOOR * W_DOOR    # 정사영 면적 (m²)

# 자유회전(감속, phase 3) 구간만 적합. dω/dt 가 후반에 급해지는 구간
# (프레임 근접 air-cushion = phase 4)은 어떤 마찰모델로도 설명 안 되므로 제외.
# (논문도 phase 4 를 정량분석에서 제외 — Klein et al. §III B)
CASES = {
    "fast": dict(
        csv="data/fast_slam.csv", label="Fast slam",
        win=(7.69, 8.00), color=CASE_COLOR["fast"],
    ),
    "slow": dict(
        csv="data/slow_slam.csv", label="Slow slam",
        win=(8.90, 11.50), color=CASE_COLOR["slow"],
    ),
}


# ----------------------------------------------------------------------
# 2. 데이터 로드 & 구간 추출
# ----------------------------------------------------------------------
def load_segment(csv, win, col="Absolute (rad/s)"):
    """CSV에서 [t_start,t_end] 구간을 잘라 (t', ω) 반환. t'는 구간 시작=0으로 재설정."""
    d = pd.read_csv(_abs(csv))
    t = d["Time (s)"].values
    w = d[col].values
    m = (t >= win[0]) & (t <= win[1])
    t_seg = t[m] - win[0]
    w_seg = w[m]
    return t_seg, w_seg


# ----------------------------------------------------------------------
# 3. 모델 적합
# ----------------------------------------------------------------------
def _p0_bounds(key, t, w):
    """모델별 초기값·경계. 계수는 모두 ≥0(물리적), ω0는 관측 피크 부근."""
    w0g = float(w[0])
    # 대략적 감쇠율 추정 (선형근사 기울기)
    slope = max((w[0] - w[-1]) / (t[-1] - t[0] + 1e-9), 1e-4)
    guesses = {"A": slope, "B": slope / max(w0g, 1e-3), "C": slope / max(w0g**2, 1e-3)}
    coeffs = MODELS[key]["coeffs"]
    p0 = [w0g] + [guesses[c] for c in coeffs]
    lo = [0.3 * w0g] + [0.0] * len(coeffs)
    hi = [1.5 * w0g] + [np.inf] * len(coeffs)
    return p0, (lo, hi)


def fit_model(key, t, w):
    """단일 모델 적합 → dict(params, R2, SSE, AIC, pred)."""
    fn = MODELS[key]["fn"]
    coeffs = MODELS[key]["coeffs"]
    p0, bounds = _p0_bounds(key, t, w)
    try:
        popt, _ = curve_fit(fn, t, w, p0=p0, bounds=bounds, maxfev=200000)
    except Exception as e:
        return dict(key=key, ok=False, err=str(e))
    pred = fn(t, *popt)
    resid = w - pred
    sse = float(np.sum(resid ** 2))
    sst = float(np.sum((w - np.mean(w)) ** 2))
    r2 = 1.0 - sse / sst if sst > 0 else float("nan")
    n = len(w); k = len(popt)
    # AIC (가우시안 잔차 가정): n·ln(SSE/n) + 2k
    aic = n * np.log(sse / n) + 2 * k if sse > 0 else float("-inf")
    params = {"w0": popt[0]}
    for name, val in zip(coeffs, popt[1:]):
        params[name] = float(val)        # 이미 A=a/I 형태 (관성으로 나뉜 값)
    return dict(key=key, ok=True, params=params, R2=r2, SSE=sse, AIC=aic,
                n=n, k=k, pred=pred)


def fit_all(t, w):
    res = {key: fit_model(key, t, w) for key in MODELS}
    ok = [r for r in res.values() if r.get("ok")]
    best = min(ok, key=lambda r: r["AIC"]) if ok else None
    return res, (best["key"] if best else None)


# ----------------------------------------------------------------------
# 3b. 물리적 타당성 (논문의 결정 기준) + F-검정
#   논문 §II/III: 같은 파라미터 수 모델(D·S·N)은 SSE가 아니라
#   "적합 계수가 차원분석 추정과 맞는가(scientific appropriateness)"로 판정.
# ----------------------------------------------------------------------
def theory_estimates():
    """차원 추정값 (논문 식 9·10·11). 우리 문 numbers 기준."""
    aI = lambda mu: 3 * mu * G_ACC / W_DOOR              # a/I = 3μg/w
    bI = 18 * np.pi * ETA_AIR * W_DOOR / M_DOOR          # b/I 상한 (Stokes)
    cI = 1.5 * CD_PLATE * RHO_AIR * A_DOOR * W_DOOR / M_DOOR  # c/I 상한 (Newton)
    return {"aI_mu": aI, "bI": float(bI), "cI": float(cI)}


def physical_validity(out):
    """각 케이스의 D/S/N 적합 계수를 이론 추정과 대조해 타당성 판정."""
    th = theory_estimates()
    verdict = {"theory": {"bI_Stokes": th["bI"], "cI_Newton": th["cI"],
                          "aI_dry_mu0.01": th["aI_mu"](0.01),
                          "aI_dry_mu0.1": th["aI_mu"](0.1)}, "cases": {}}
    for name, cd in out["cases"].items():
        f = cd["fits"]
        aI = f["D"]["params"]["A"]; bI = f["S"]["params"]["B"]; cI = f["N"]["params"]["C"]
        mu_implied = aI * W_DOOR / (3 * G_ACC)          # a/I=3μg/w → μ
        dry_torque = aI * I_DOOR                          # a = (a/I)·I  [N·m]
        verdict["cases"][name] = dict(
            aI=aI, bI=bI, cI=cI,
            mu_implied=float(mu_implied), dry_torque=float(dry_torque),
            bI_ratio=float(bI / th["bI"]),               # Stokes: 이론 대비 배수
            cI_ratio=float(cI / th["cI"]),               # Newton: 이론 대비 배수
        )
    # Dry 자기일관성: 두 케이스 μ 비
    mus = [verdict["cases"][n]["mu_implied"] for n in out["cases"]]
    verdict["mu_inconsistency"] = float(max(mus) / min(mus)) if min(mus) > 0 else None
    return verdict


def f_test(sse_r, sse_f, p_r, p_f, n):
    """nested model F-검정. p=파라미터 수(ω0 포함)."""
    num = (sse_r - sse_f) / (p_f - p_r)
    den = sse_f / (n - p_f)
    return float(num / den) if den > 0 else float("nan")


def nested_ftests(out):
    """D→DN, S→SN, N→DN F-검정 (각 케이스)."""
    res = {}
    for name, cd in out["cases"].items():
        f = cd["fits"]; n = cd["n"]
        res[name] = dict(
            D_to_DN=f_test(f["D"]["SSE"], f["DN"]["SSE"], 2, 3, n),
            S_to_SN=f_test(f["S"]["SSE"], f["SN"]["SSE"], 2, 3, n),
            N_to_DN=f_test(f["N"]["SSE"], f["DN"]["SSE"], 2, 3, n),
        )
    return res


# ----------------------------------------------------------------------
# 4. 실행: 두 케이스 적합 → 결과 dict
# ----------------------------------------------------------------------
def run():
    out = {"I_door": I_DOOR, "constants": dict(
        m=M_DOOR, w=W_DOOR, h=H_DOOR, r=R_PHONE, I=I_DOOR,
        A=A_DOOR, cD=CD_PLATE, rho=RHO_AIR, eta=ETA_AIR), "cases": {}}
    for name, cfg in CASES.items():
        t, w = load_segment(cfg["csv"], cfg["win"])
        res, best = fit_all(t, w)
        out["cases"][name] = dict(
            label=cfg["label"], win=cfg["win"], n=len(t),
            w0_obs=float(w[0]), w_end=float(w[-1]), best=best,
            fits={k: {kk: vv for kk, vv in r.items() if kk != "pred"}
                  for k, r in res.items()},
        )
    out["physical_validity"] = physical_validity(out)
    out["f_tests"] = nested_ftests(out)
    return out


if __name__ == "__main__":
    r = run()
    print(json.dumps(r, indent=2, ensure_ascii=False))
