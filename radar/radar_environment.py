import numpy as np

class RadarEnvironment:
    def __init__(self, radar, n_points=2000):
        self.radar = radar
        self.targets = []

        # Generar puntos aleatorios dentro del FOV
        self.points = self.generate_points_in_fov(n_points)

    def generate_points_in_fov(self, n):
        az = np.random.uniform(self.radar.az_min, self.radar.az_max, n)
        el = np.random.uniform(self.radar.el_min, self.radar.el_max, n)
        r  = np.random.uniform(0, self.radar.R, n)

        # Convertir a ENU relativo al radar
        x = r * np.cos(el) * np.cos(az)
        y = r * np.cos(el) * np.sin(az)
        z = r * np.sin(el)

        return np.vstack((x, y, z)).T

    def add_target(self, target):
        self.targets.append(target)

    def update(self, dt):
        for t in self.targets:
            t.update(dt)

    def get_points(self):
        return self.points