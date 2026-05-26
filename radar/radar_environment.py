import numpy as np
import matplotlib.pyplot as plt
import time

import matplotlib
matplotlib.use("TkAgg")



class OrbitalTarget:
    def __init__(self, a, e, i, raan, argp, nu0, mu=3.986004418e14):
        """
        a     = semieje mayor (m)
        e     = excentricidad
        i     = inclinación (rad)
        raan  = ascensión recta nodo ascendente (rad)
        argp  = argumento del perigeo (rad)
        nu0   = anomalía verdadera inicial (rad)
        mu    = parámetro gravitacional de la Tierra
        """
        self.a = a
        self.e = e
        self.i = i
        self.raan = raan
        self.argp = argp
        self.nu = nu0
        self.mu = mu

        # Velocidad angular media
        self.n = np.sqrt(mu / a**3)

    def update(self, dt):
        """Propaga la anomalía verdadera usando Kepler 2-body."""
        self.nu += self.n * dt
        self.nu = self.nu % (2*np.pi)

    def get_position(self):
        """Devuelve la posición ECI del satélite."""
        a, e, i, raan, argp, nu = self.a, self.e, self.i, self.raan, self.argp, self.nu

        # Distancia radial
        r = a * (1 - e**2) / (1 + e * np.cos(nu))

        # Coordenadas en el plano orbital
        x_orb = r * np.cos(nu)
        y_orb = r * np.sin(nu)
        z_orb = 0

        # Rotaciones: argp → i → raan
        R3_w = np.array([
            [np.cos(argp), -np.sin(argp), 0],
            [np.sin(argp),  np.cos(argp), 0],
            [0, 0, 1]
        ])

        R1_i = np.array([
            [1, 0, 0],
            [0, np.cos(i), -np.sin(i)],
            [0, np.sin(i),  np.cos(i)]
        ])

        R3_O = np.array([
            [np.cos(raan), -np.sin(raan), 0],
            [np.sin(raan),  np.cos(raan), 0],
            [0, 0, 1]
        ])

        R = R3_O @ R1_i @ R3_w
        return R @ np.array([x_orb, y_orb, z_orb])
    
class RadarEnvironment:
    def __init__(self, radar, earth_radius=6371000):
        self.radar = radar
        self.targets = []
        self.Re = earth_radius

    def add_target(self, target):
        self.targets.append(target)

    def update(self, dt):
        for t in self.targets:
            t.update(dt)

    def get_detections(self):
        detections = []

        for t in self.targets:
            pos_eci = t.get_position()

            # Convertir radar pos (local) a ECI si quieres más realismo
            radar_pos = self.radar.position

            rel = pos_eci - radar_pos
            x, y, z = rel

            rng = np.linalg.norm(rel)
            az = np.arctan2(y, x)
            el = np.arctan2(z, np.sqrt(x*x + y*y))

            # Comprobar si está dentro del haz
            if abs(az - self.radar.az0) < self.radar.bw_az/2 and \
               abs(el - self.radar.el0) < self.radar.bw_el/2 and \
               rng < self.radar.R:

                detections.append({
                    "target": t,
                    "range": rng,
                    "az": az,
                    "el": el,
                    "pos": pos_eci
                })

        return detections
    

