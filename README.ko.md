<div align="center">

# 🚪 문 닫힘의 회전 및 마찰 역학 분석

**스마트폰 자이로스코프를 이용한 Klein _et al._ (Am. J. Phys. 85, 30, 2017) 연구 재현**

<p>
<a href="https://www.python.org"><img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white"></a>
<img src="https://img.shields.io/badge/SciPy-curve__fit%20%2B%20solve__ivp-8CAAE6?logo=scipy&logoColor=white">
<img src="https://img.shields.io/badge/Matplotlib-SciencePlots-11557C">
<img src="https://img.shields.io/badge/LaTeX-report-008080?logo=latex&logoColor=white">
<a href="https://doi.org/10.1119/1.4964134"><img src="https://img.shields.io/badge/AJP-10.1119%2F1.4964134-b31b1b"></a>
</p>

[English](README.md) · **한국어**

<em>Team solvE (14조) · DGIST 일반물리학</em>

</div>

---

## 프로젝트 개요

문이 닫힐 때 힌지를 중심으로 회전하며 감속하다가 멈추는 현상을 분석합니다. Klein _et al._ 연구는 세 가지 마찰 법칙(상수 마찰인 **건마찰**, 선형 마찰인 **스토크스 마찰**, 속도의 제곱에 비례하는 **뉴턴 공기 저항**) 중 어떤 모델이 실제 문 닫힘을 가장 잘 설명하는지 탐구했습니다.

본 프로젝트에서는 실제 문을 대상으로 정밀한 측정을 수행하여 해당 연구를 재현했습니다. 기존 연구와 달리 스마트폰 자이로스코프를 이용해 각속도 $\omega(t)$를 **직접 측정**하여 데이터의 정확성을 높였으며, 6가지 마찰 모델 전체에 대한 수치 시뮬레이션을 수행하여 이론적 유도 과정을 검증했습니다.

## 주요 특징

*   **직접 측정:** Phyphox 앱을 활용한 고주파수(460 Hz) 자이로스코프 데이터 수집.
*   **정밀한 설정:** **문을 직접 분리**하여 질량($m$), 너비($w$), 높이($h$) 등 물리적 변수를 정확히 측정.
*   **포괄적 모델링:** 6가지 마찰 모델(D, S, N, DS, DN, SN)에 대한 적합 분석.
*   **수치적 검증:** 해석적 해와 `solve_ivp` 적분을 비교하여 유도 과정의 정밀도 확인(오차 $\sim 10^{-8}$ rad/s).
*   **비교 시뮬레이션:** 모든 모델의 장기 거동을 시뮬레이션하여 감쇄 특성 시각화.

## 핵심 결과

> 적합도($R^2$)뿐만 아니라 **물리적 타당성**을 기준으로 판단했을 때, 스토크스와 건마찰 모델은 기각되었으며 **뉴턴 공기 저항($\omega^2$) 모델만이 유일하게 일관된 물리량을 제시**했습니다. 이는 Klein et al.의 결론과 일치합니다.

| 마찰 계수 | 적합값 (빠름 / 느림) | 이론적 추정치 | 판정 |
|---|---|---|---|
| $a/I$ (건마찰) | 1.09 / 0.12 → μ = 0.031 / 0.0034 | $3\mu g/w$ | ❌ μ 값의 9배 불일치 |
| $b/I$ (스토크스) | 0.54 / 0.29 | $\sim 6\times10^{-5}$ | ❌ 이론치보다 $10^3$–$10^4$배 큼 |
| $c/I$ (뉴턴) | 0.27 / 0.68 | $\lesssim 0.30$ | ✅ **동일 자릿수 — 채택** |

<div align="center">
<img src="figures/fig_fit_slow.png" width="45%"> <img src="figures/fig6_sim_models.png" width="45%">
</div>

## 저장소 구조

```
physics-door-slam/
├── data/
│   ├── simulation/           # 7가지 시뮬레이션 모델의 원본 CSV 데이터
│   ├── fast_slam.csv         # 측정된 자이로스코프 데이터 (빠른 슬램)
│   └── slow_slam.csv         # 측정된 자이로스코프 데이터 (느린 슬램)
├── src/
│   ├── analysis.py           # 곡선 적합, 통계 분석 (AIC, R²)
│   ├── friction_models.py    # 해석적 해(Analytic solution) 구현
│   ├── simulation.py         # 수치 적합 및 애니메이션 로직
│   └── make_figures.py       # 저널 스타일 그래프 생성
├── report/                   # LaTeX 소스 및 컴파일된 PDF 리포트
├── figures/                  # 고해상도 그래프 및 실험 사진
└── notebooks/                # 단계별 분석 워크스루
```

## 시작하기

1.  **의존성 설치:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **결과물 생성:**
    ```bash
    cd src && python make_figures.py
    ```
3.  **리포트 빌드:**
    LaTeX 패키지 자동 관리를 위해 [Tectonic](https://tectonic-typesetting.github.io/) 사용을 권장합니다.
    ```bash
    cd report && tectonic report.tex
    ```

## 팀 solvE (14조)

*   **채은우:** 데이터 분석 · GitHub · 리포트 (LaTeX)
*   **성강민:** 리포트 (LaTeX) · 시뮬레이션
*   **장민석:** 실험 · 데이터 획득
*   **주솔비:** 발표 · 영상

## 참고 문헌

P. Klein, A. Müller, S. Gröber, A. Molz, J. Kuhn,
_"Rotational and frictional dynamics of the slamming of a door,"_
**Am. J. Phys. 85, 30–37 (2017).** [doi:10.1119/1.4964134](https://doi.org/10.1119/1.4964134)
