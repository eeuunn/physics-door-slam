import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# =========================
# 1. Physical parameters
# =========================

m = 50.0          # door mass [kg]
w = 1.0           # door width [m]
I = (1/3) * m * w**2   # moment of inertia [kg m^2]

theta0 = np.deg2rad(100)   # initial open angle [rad]
omega0 = 2.6               # initial angular velocity [rad/s]

# N model parameter from paper Table III, large spin case
# c/I = 0.11
c_over_I = 0.11            # dimensionless in this formulation

# =========================
# 2. N model equations
# =========================

def omega_N(t):
    """Angular velocity for Newtonian drag model."""
    return omega0 / (1 + c_over_I * omega0 * t)

def theta_N(t):
    """
    Remaining door angle for Newtonian drag model.
    theta decreases because the door is closing.
    """
    return theta0 - (1 / c_over_I) * np.log(1 + c_over_I * omega0 * t)

# =========================
# 3. Determine simulation end time
# =========================

# Door closes when theta(t) = 0.
# theta0 = (1/c_over_I) ln(1 + c_over_I*omega0*t)
# exp(c_over_I*theta0) = 1 + c_over_I*omega0*t

t_close = (np.exp(c_over_I * theta0) - 1) / (c_over_I * omega0)
t_end = t_close

# =========================
# 4. Generate time data
# =========================

dt = 0.01
t = np.arange(0, t_end + dt, dt)

omega = omega_N(t)
theta = theta_N(t)
theta = np.maximum(theta, 0)
theta_deg = np.rad2deg(theta)

# =========================
# 5. Save angular velocity data
# =========================

data = pd.DataFrame({
    "time_s": t,
    "omega_rad_s": omega,
    "theta_rad": theta,
    "theta_deg": theta_deg
})

data.to_csv("N_model_angular_velocity_data.csv", index=False)
data.to_excel("N_model_angular_velocity_data.xlsx", index=False)

print("Saved:")
print("N_model_angular_velocity_data.csv")
print("N_model_angular_velocity_data.xlsx")

print("\nFirst 10 rows:")
print(data.head(10))

print("\nLast 10 rows:")
print(data.tail(10))

# =========================
# 6. Door animation only
# =========================

fig, ax = plt.subplots(figsize=(5, 5))

ax.set_aspect("equal")
ax.set_xlim(-0.2, 1.2)
ax.set_ylim(-0.2, 1.2)
ax.set_title("N Model: Door Motion")
ax.set_xlabel("x [m]")
ax.set_ylabel("y [m]")

# Wall
ax.plot([0, 0], [0, 1.1], linewidth=4)

# Door
door_line, = ax.plot([], [], linewidth=6)
angle_text = ax.text(0.05, 1.05, "", fontsize=10)
time_text = ax.text(0.05, 0.98, "", fontsize=10)

def update(frame):
    th = theta[frame]

    x_end = w * np.sin(th)
    y_end = w * np.cos(th)

    door_line.set_data([0, x_end], [0, y_end])
    angle_text.set_text(f"theta = {np.rad2deg(th):.1f} deg")
    time_text.set_text(f"t = {t[frame]:.2f} s, omega = {omega[frame]:.2f} rad/s")

    return door_line, angle_text, time_text

ani = FuncAnimation(fig, update, frames=len(t), interval=20, blit=True)

ani.save("N_model_door_motion.gif", writer=PillowWriter(fps=30))

plt.show()
