import matplotlib
matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt
import time


class RadarSimulator:
    def __init__(self, radar, environment, trail_seconds=5):
        self.radar = radar
        self.environment = environment

        plt.ion()
        self.fig = plt.figure(figsize=(10, 7))
        self.ax = self.fig.add_subplot(111, projection='3d')

        self.start_time = time.time()
        self.last_time = self.start_time

        # Rastro del haz (lista de (t, punto))
        self.trail = []
        self.trail_seconds = trail_seconds

    def step(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        sim_time = now - self.start_time

        # Actualizar radar
        self.radar.update(dt)

        # Calcular punto final del eje del haz
        az = self.radar.az0
        el = self.radar.el0

        x_end = self.radar.R * np.cos(el) * np.cos(az)
        y_end = self.radar.R * np.cos(el) * np.sin(az)
        z_end = self.radar.R * np.sin(el)

        end_point = np.array([
            self.radar.position[0] + x_end,
            self.radar.position[1] + y_end,
            self.radar.position[2] + z_end
        ])

        # Añadir al rastro con timestamp
        self.trail.append((sim_time, end_point))

        # Eliminar puntos más antiguos que trail_seconds
        self.trail = [(t, p) for (t, p) in self.trail if sim_time - t <= self.trail_seconds]

        # Dibujar escena
        self.ax.cla()

        # Haz actual
        X, Y, Z = self.radar.compute_beam()
        self.ax.plot_surface(X, Y, Z, alpha=0.25, color='cyan', edgecolor='k')

        # Línea actual
        self.ax.plot(
            [self.radar.position[0], end_point[0]],
            [self.radar.position[1], end_point[1]],
            [self.radar.position[2], end_point[2]],
            color='yellow',
            linewidth=0.8
        )

        # Dibujar rastro
        for (_, p) in self.trail:
            self.ax.plot(
                [self.radar.position[0], p[0]],
                [self.radar.position[1], p[1]],
                [self.radar.position[2], p[2]],
                color='gray',
                linewidth=0.3,
                alpha=0.4
            )

        # Actualizar órbitas
        self.environment.update(dt)

        # Obtener detecciones
        detections = self.environment.get_detections()

        # Dibujar targets
        for t in self.environment.targets:
            pos = t.get_position()
            self.ax.scatter(pos[0], pos[1], pos[2], color='blue', s=20)

        # Dibujar detecciones
        for d in detections:
            pos = d["pos"]
            self.ax.scatter(pos[0], pos[1], pos[2], color='red', s=60)

        # Radar
        self.ax.scatter(*self.radar.position, color='red', s=80)

        # Límites
        self.ax.set_xlim(-self.radar.R, self.radar.R)
        self.ax.set_ylim(-self.radar.R, self.radar.R)
        self.ax.set_zlim(0, self.radar.R)

        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_zlabel("Z (m)")

        self.ax.set_title(
            f"Radar girando a {self.radar.rpm} RPM\n"
            f"Tiempo de simulación: {sim_time:.2f} s\n"
            f"Elevación actual: {np.degrees(self.radar.el0):.1f}°"
        )

        plt.pause(0.01)
    
    def run(self):
        """Ejecuta la simulación completa en bucle infinito."""
        while True:
            self.step()