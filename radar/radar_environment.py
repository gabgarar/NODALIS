
import numpy as np

# =========================================================
# ORBITAL TARGET (SATÉLITES LEO)
# =========================================================
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

        self.n = np.sqrt(mu / a**3)

    def update(self, dt):
        self.nu = (self.nu + self.n * dt) % (2*np.pi)

    def get_position(self):
        a, e, i, raan, argp, nu = self.a, self.e, self.i, self.raan, self.argp, self.nu

        r = a * (1 - e**2) / (1 + e * np.cos(nu))

        x_orb = r * np.cos(nu)
        y_orb = r * np.sin(nu)
        z_orb = 0.0

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

# =========================================================
# ENVIRONMENT: PUNTOS + SATÉLITES LEO
# =========================================================
class RadarEnvironment:
    def __init__(self, radar, n_points=2000, n_sats=0, radius=6371000.0):
        self.radar = radar
        self.targets = []

        self.points = self.generate_points_in_fov(n_points)

        if n_sats > 0:
            self.generate_leo_satellites(n_sats, radius)

    def generate_points_in_fov(self, n):
        az = np.random.uniform(self.radar.az_min, self.radar.az_max, n)
        el = np.random.uniform(self.radar.el_min, self.radar.el_max, n)
        r  = np.random.uniform(0, self.radar.R, n)

        x = r * np.cos(el) * np.cos(az)
        y = r * np.cos(el) * np.sin(az)
        z = r * np.sin(el)

        return np.vstack((x, y, z)).T

    def generate_leo_satellites(self, n, Re):
        mu = 3.986004418e14

        for _ in range(n):
            a = Re + np.random.uniform(400e3, 1200e3)
            e = np.random.uniform(0.0, 0.01)
            i = np.radians(np.random.uniform(0, 98))
            raan = np.random.uniform(0, 2*np.pi)
            argp = np.random.uniform(0, 2*np.pi)
            nu0  = np.random.uniform(0, 2*np.pi)

            sat = OrbitalTarget(a, e, i, raan, argp, nu0, mu)
            self.targets.append(sat)

    def update(self, dt):
        for t in self.targets:
            t.update(dt)

    def get_points(self):
        return self.points

    def get_satellite_positions(self):
        return [t.get_position() for t in self.targets]