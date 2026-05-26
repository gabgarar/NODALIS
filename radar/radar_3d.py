import matplotlib
matplotlib.use("TkAgg")

import numpy as np
import matplotlib.pyplot as plt


class Radar3D:
    def __init__(self, position, az0_deg, el0_deg, bw_az_deg, bw_el_deg,
                 R, rpm, el_min_deg, el_max_deg):

        self.position = np.array(position, dtype=float)

        # Dirección inicial
        self.az0 = np.radians(az0_deg)
        self.el0 = np.radians(el0_deg)

        # Límites de elevación
        self.el_min = np.radians(el_min_deg)
        self.el_max = np.radians(el_max_deg)

        # Beamwidth
        self.bw_az = np.radians(bw_az_deg)
        self.bw_el = np.radians(bw_el_deg)

        # Alcance
        self.R = R

        # Velocidad angular (rad/s)
        self.rpm = rpm
        self.angular_speed = 2 * np.pi * (rpm / 60.0)

    @staticmethod
    def spherical_to_cartesian(r, az, el):
        x = r * np.cos(el) * np.cos(az)
        y = r * np.cos(el) * np.sin(az)
        z = r * np.sin(el)
        return x, y, z

    def compute_beam(self, n=40):
        az = np.linspace(self.az0 - self.bw_az/2,
                         self.az0 + self.bw_az/2, n)
        el = np.linspace(self.el0 - self.bw_el/2,
                         self.el0 + self.bw_el/2, n)

        AZ, EL = np.meshgrid(az, el)
        X, Y, Z = self.spherical_to_cartesian(self.R, AZ, EL)

        return X + self.position[0], Y + self.position[1], Z + self.position[2]

    def update(self, dt):
        # Giro en azimut
        prev_az = self.az0
        self.az0 += self.angular_speed * dt
        self.az0 = self.az0 % (2 * np.pi)

        # Detectar si se completó una vuelta
        completed_turn = (prev_az > self.az0)

        if completed_turn:
            # Subir un paso igual al beamwidth en elevación
            step = self.bw_el  # tamaño del haz en elevación
            self.el0 += step

            # Reinicio si se pasa del máximo
            if self.el0 > self.el_max:
                self.el0 = self.el_min