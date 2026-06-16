# report/ — LaTeX 보고서 연동

보고서 본문(`report.tex`)은 **Overleaf**에서 작성하고, 이 폴더의 자동 생성물을 가져다 쓴다.

## 자동 생성물 (cd src && python make_figures.py 로 갱신)

| 파일 | 용도 |
|---|---|
| `results_table.tex` | 6모델 적합 결과표 (fast/slow). `\input{results_table.tex}` 로 삽입 |
| `results.json` | 모든 적합 파라미터·R²·SSE·AIC 원자료 |
| `../figures/*.png` | 보고서 그림. `\includegraphics{../figures/fig_fit_slow.png}` |

## 보고서에 반영할 핵심 (실측 결과)

1. **§Experimental Methodology**: 자이로스코프로 $\omega$ 를 **직접 측정** → 논문의
   $\omega=\sqrt{a_r/r}$ 변환 단계는 불필요했음을 명시.
2. **§Results**: `results_table.tex`(적합) + `validity_table.tex`(물리타당성) 표 +
   `fig_fit_*.png`, `fig3_gof.png`, `fig5_validity.png` 삽입.
3. **결론**: 모델 선택은 R²/SSE가 아니라 **물리적 타당성**으로 — Stokes 기각($b/I$ 10³~10⁴배),
   Dry 기각(함의 μ 9배 불일치), **Newton($\omega^2$) 채택**($c/I$ 가 추정~0.30과 같은 자릿수).
   → 논문과 **일치**. fast 슬램은 구간 짧아 통계 구별 불가(논문도 지적한 한계)임을 명시.
4. **§Computational Simulation**: `fig4_simulation.png` — 해석해와 `solve_ivp`
   수치적분이 $10^{-8}$ 수준으로 일치 → 해석해 유도 검증.

> 본문 전체 초안은 `report.tex` 에 있음 (Overleaf 업로드용, pdfLaTeX 호환).

## 그림 목록
- `fig1_overview.png` — 전체 시계열 + 분석 구간
- `fig_fit_fast.png`, `fig_fit_slow.png` — 6모델 적합
- `fig3_gof.png` — R²·ΔAIC 비교
- `fig4_simulation.png` — 해석해 vs 수치 시뮬레이션
