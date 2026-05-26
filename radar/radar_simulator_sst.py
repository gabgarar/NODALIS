import time
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class RadarSimulator:
    def __init__(self, radar, environment, trail_seconds=10, show_dt=False, show_fov=False):
        self.radar = radar
        self.environment = environment
        self.trail_seconds = trail_seconds

        self.show_dt = show_dt
        self.show_fov = show_fov

        self.history = []

        self.start_time = time.time()
        self.last_time = self.start_time

        plt.ion()
        self.fig = plt.figure(figsize=(10, 8))
        self.ax3d = self.fig.add_subplot(1, 1, 1, projection='3d')

    # ---------------------------------------------------------
    # DIBUJAR FOV
    # ---------------------------------------------------------
    def draw_fov(self, ax):
        if not self.show_fov:
            return

        Xf, Yf, Zf, az_fov, el_fov = self.radar.get_fov()

        ax.plot_surface(
            Xf, Yf, Zf,
            color='cyan',
            alpha=0.10,
            edgecolor='none'
        )

        R = self.radar.R

        # Contorno inferior
        ax.plot(
            R * np.cos(self.radar.el_min) * np.cos(az_fov),
            R * np.cos(self.radar.el_min) * np.sin(az_fov),
            R * np.sin(self.radar.el_min),
            color='cyan', linewidth=1.0
        )

        # Contorno superior
        ax.plot(
            R * np.cos(self.radar.el_max) * np.cos(az_fov),
            R * np.cos(self.radar.el_max) * np.sin(az_fov),
            R * np.sin(self.radar.el_max),
            color='cyan', linewidth=1.0
        )

        # Líneas laterales
        for az_edge in [self.radar.az_min, self.radar.az_max]:
            ax.plot(
                R * np.cos(el_fov) * np.cos(az_edge),
                R * np.cos(el_fov) * np.sin(az_edge),
                R * np.sin(el_fov),
                color='cyan', linewidth=0.8
            )

    # ---------------------------------------------------------
    # STEP
    # ---------------------------------------------------------
    def step(self):

        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if self.show_dt:
            print(f"dt = {dt:.4f} s")

        # Actualizar radar y entorno
        self.radar.update(dt)
        self.environment.update(dt)

        # Eje del haz
        az = self.radar.az0
        el = self.radar.el0

        x_rel = self.radar.R * np.cos(el) * np.cos(az)
        y_rel = self.radar.R * np.cos(el) * np.sin(az)
        z_rel = self.radar.R * np.sin(el)

        # Historial del eje del haz
        self.history.append((now, x_rel, y_rel, z_rel))
        cutoff = now - self.trail_seconds
        self.history = [h for h in self.history if h[0] >= cutoff]

        _, xs, ys, zs = zip(*self.history)

        # ---------------------------------------------------------
        # PLOT 3D ÚNICO
        # ---------------------------------------------------------
        self.ax3d.cla()

        # Prisma del haz
        corners = self.radar.compute_beam_volume()  # coordenadas relativas
        faces = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [0, 1, 5, 4],
            [1, 2, 6, 5],
            [2, 3, 7, 6],
            [3, 0, 4, 7],
        ]
        polygons = [corners[f] for f in faces]

        poly = Poly3DCollection(
            polygons,
            facecolors='cyan',
            edgecolors='none',
            alpha=0.15
        )
        self.ax3d.add_collection3d(poly)

        # Eje del haz
        self.ax3d.plot(
            [0, x_rel],
            [0, y_rel],
            [0, z_rel],
            color='gray',
            linewidth=0.8
        )

        # Radar
        self.ax3d.scatter(0, 0, 0, color='red', s=15)

        # FOV opcional
        self.draw_fov(self.ax3d)

        # Puntos del environment (ya en coordenadas relativas / ENU)
        points = self.environment.get_points()

        inside_mask = np.array([self.radar.point_in_beam(p) for p in points])
        inside = points[inside_mask]
        outside = points[~inside_mask]

        if len(outside) > 0:
            self.ax3d.scatter(
                outside[:, 0], outside[:, 1], outside[:, 2],
                color='magenta', s=3, alpha=0.5
            )

        if len(inside) > 0:
            self.ax3d.scatter(
                inside[:, 0], inside[:, 1], inside[:, 2],
                color='red', s=10
            )

        # Historial del eje del haz
        self.ax3d.scatter(xs, ys, zs, color='blue', alpha=0.05, s=3)

        # Límites
        R = self.radar.R
        self.ax3d.set_xlim(-R, R)
        self.ax3d.set_ylim(-R, R)
        self.ax3d.set_zlim(0, R)

        self.ax3d.set_title("Simulación 3D (coordenadas relativas)")
        self.ax3d.set_xlabel("x' (m)")
        self.ax3d.set_ylabel("y' (m)")
        self.ax3d.set_zlabel("z' (m)")

        # Texto
        self.ax3d.text2D(
            0.05, 0.95,
            f"Azimut: {np.degrees(az):6.2f}°\nElevación: {np.degrees(el):6.2f}°",
            transform=self.ax3d.transAxes,
            fontsize=10,
            color='white',
            bbox=dict(facecolor='black', alpha=0.5, edgecolor='none')
        )

        plt.pause(0.05)

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------
    def run(self):
        sim_dt = self.radar.dwell_time
        last_draw = time.time()

        while True:
            now = time.time()

            while self.last_time + sim_dt <= now:
                self.radar.update(sim_dt)
                self.environment.update(sim_dt)
                self.last_time += sim_dt

                az = self.radar.az0
                el = self.radar.el0
                x_rel = self.radar.R * np.cos(el) * np.cos(az)
                y_rel = self.radar.R * np.cos(el) * np.sin(az)
                z_rel = self.radar.R * np.sin(el)

                self.history.append(
                    (self.last_time, x_rel, y_rel, z_rel)
                )

            if now - last_draw > 0.05:
                self.step()
                last_draw = now