"""
friction_models.py
==================
문이 쾅 닫힐 때의 회전·마찰 동역학 (Klein et al., AJP 85, 2017) 6개 마찰 모델.

운동방정식:  -I dω/dt = a + bω + cω²
            => dω/dt = -(A + Bω + Cω²),   A=a/I, B=b/I, C=c/I

각 모델은 위 식에서 일부 항을 0으로 둔 특수해이다.
모든 해석해는 (t, ω0, 계수…)를 인자로 받아 ω(t)를 반환한다.
계수는 모두 "관성으로 나눈" 형태(A=a/I 등)로 파라미터화 — curve_fit이 다루기 쉽고
I를 따로 알 필요 없이 a/I, b/I, c/I를 바로 얻는다.

Team solvE · Group 14 · DGIST General Physics
"""
import numpy as np
from scipy.integrate import solve_ivp

# ----------------------------------------------------------------------
# 해석해 (analytical solutions)  —  보고서 §2.4 검증용
# ----------------------------------------------------------------------

def model_D(t, w0, A):
    """건마찰(Dry): 일정 토크 → 선형 감소.  ω = ω0 - A t"""
    return w0 - A * t


def model_S(t, w0, B):
    """스토크스(Stokes): τ∝ω → 지수 감쇠.  ω = ω0 e^(-B t)"""
    return w0 * np.exp(-B * t)


def model_N(t, w0, C):
    """뉴턴 공기저항(Newton): τ∝ω² → 1/t 감쇠.  ω = ω0/(1+C ω0 t)"""
    return w0 / (1.0 + C * w0 * t)


def model_DS(t, w0, A, B):
    """건마찰+스토크스(DS).  ω = (ω0 + A/B) e^(-B t) - A/B"""
    return (w0 + A / B) * np.exp(-B * t) - A / B


def model_DN(t, w0, A, C):
    """건마찰+뉴턴(DN).  ω = √(A/C)·tan( arctan(ω0√(C/A)) - √(AC) t )"""
    rAC = np.sqrt(A * C)
    rRatio = np.sqrt(A / C)
    phi0 = np.arctan(w0 / rRatio)            # = arctan(ω0 √(C/A))
    return rRatio * np.tan(phi0 - rAC * t)


def model_SN(t, w0, B, C):
    """스토크스+뉴턴(SN).  ω = B ω0 / [ (B + C ω0) e^(B t) - C ω0 ]"""
    return (B * w0) / ((B + C * w0) * np.exp(B * t) - C * w0)


# 모델 레지스트리: 이름 -> (함수, 자유계수 라벨, 초기값 추정 함수)
# w0(ω0)는 모든 모델에서 공통 자유계수로 함께 적합한다.
MODELS = {
    "D":  dict(fn=model_D,  coeffs=["A"]),
    "S":  dict(fn=model_S,  coeffs=["B"]),
    "N":  dict(fn=model_N,  coeffs=["C"]),
    "DS": dict(fn=model_DS, coeffs=["A", "B"]),
    "DN": dict(fn=model_DN, coeffs=["A", "C"]),
    "SN": dict(fn=model_SN, coeffs=["B", "C"]),
}

MODEL_LABEL = {
    "D":  "Dry",
    "S":  "Stokes",
    "N":  "Newton (air drag)",
    "DS": "Dry + Stokes",
    "DN": "Dry + Newton",
    "SN": "Stokes + Newton",
}


# ----------------------------------------------------------------------
# 수치 시뮬레이션 (numerical simulation) — 보고서 §4
#   -I dω/dt = a + bω + cω²  를 직접 적분.
#   해석해와 겹쳐 그려 "해석해 == 수치적분" 검증, 그리고 일반 DSN 모델도 처리.
# ----------------------------------------------------------------------

def simulate(t_eval, w0, A=0.0, B=0.0, C=0.0):
    """dω/dt = -(A + Bω + Cω²) 를 solve_ivp로 적분해 ω(t)를 반환.

    A,B,C 중 일부만 주면 해당 부분모델의 수치해가 된다(셋 다 주면 완전 DSN).
    ω이 0 아래로 내려가면(문이 멈춘 뒤) 적분을 중단한다.
    """
    def rhs(t, w):
        return -(A + B * w[0] + C * w[0] ** 2)

    def stop(t, w):           # ω = 0 도달 시 정지(문이 닫혀 멈춤)
        return w[0]
    stop.terminal = True
    stop.direction = -1

    sol = solve_ivp(rhs, (t_eval[0], t_eval[-1]), [w0],
                    t_eval=t_eval, method="RK45",
                    rtol=1e-8, atol=1e-10, events=stop)
    # 정지 이후 구간은 0으로 채움
    w = np.zeros_like(t_eval)
    w[: len(sol.y[0])] = sol.y[0]
    return w
