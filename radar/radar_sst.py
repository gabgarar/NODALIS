import numpy as np

# =========================================================
# RADAR SST
# =========================================================
class RadarSST:
    def __init__(
        self,
        position=[0,0,0],
        bw_az_deg=1.0,
        bw_el_deg=1.0,
        R=2000000,
        az_sector=(-30, 30),
        el_sector=(10, 80),
        scan_speed_deg_s=10,
        dwell_time=0.003,
        mode="search",
        scan_pattern="raster"
    ):
        self.position = np.array(position, dtype=float)
        self.dwell_time = dwell_time
        self._dwell_accum = 0.0

        self.bw_az = np.radians(bw_az_deg)
        self.bw_el = np.radians(bw_el_deg)

        self.R = R

        self.az_min = np.radians(az_sector[0])
        self.az_max = np.radians(az_sector[1])
        self.el_min = np.radians(el_sector[0])
        self.el_max = np.radians(el_sector[1])

        self.az0 = self.az_min
        self.el0 = self.el_min

        self.scan_speed = np.radians(scan_speed_deg_s)
        self.scan_dir_az = 1

        self.mode = mode
        self.scan_pattern = scan_pattern


    # =========================================================
    # SEARCH MODE
    # =========================================================
    def update_search(self, dt):
        self._dwell_accum += dt
        if self._dwell_accum < self.dwell_time:
            return
        self._dwell_accum = 0.0

        delta_az = self.scan_dir_az * self.scan_speed * self.dwell_time
        self.az0 += delta_az

        if self.scan_pattern == "raster":
            if self.az0 > self.az_max:
                self.az0 = self.az_min
                self.el0 += self.bw_el * 0.6

            if self.el0 > self.el_max:
                self.el0 = self.el_min

        elif self.scan_pattern == "pingpong":

            if self.az0 > self.az_max:
                self.az0 = self.az_max
                self.scan_dir_az = -1

            elif self.az0 < self.az_min:
                self.az0 = self.az_min
                self.scan_dir_az = 1

            if self.scan_dir_az == 1 and self.az0 == self.az_min:
                self.el0 += self.bw_el * 0.6

            if self.el0 > self.el_max:
                self.el0 = self.el_min


    # =========================================================
    # TRACKING MODE
    # =========================================================
    def point_to(self, target_pos):
        rel = target_pos - self.position
        x, y, z = rel

        self.az0 = np.arctan2(y, x)
        self.el0 = np.arctan2(z, np.sqrt(x*x + y*y))


    # =========================================================
    # UPDATE
    # =========================================================
    def update(self, dt, target_pos=None):
        if self.mode == "search":
            self.update_search(dt)
        elif self.mode == "tracking" and target_pos is not None:
            self.point_to(target_pos)


    # =========================================================
    # BASE ORTONORMAL DEL HAZ (CORREGIDA)
    # =========================================================
    def _beam_basis(self):
        az = self.az0
        el = self.el0

        # Eje del haz
        axis = np.array([
            np.cos(el)*np.cos(az),
            np.cos(el)*np.sin(az),
            np.sin(el)
        ])

        # Vector lateral (azimutal)
        u = np.array([-np.sin(az), np.cos(az), 0.0])
        if np.linalg.norm(u) < 1e-12:
            u = np.array([1.0, 0.0, 0.0])
        u = u / np.linalg.norm(u)

        # Vector vertical (elevación)
        v = np.cross(axis, u)
        if np.linalg.norm(v) < 1e-12:
            v = np.array([0.0, 0.0, 1.0])
        v = v / np.linalg.norm(v)

        return axis, u, v


    # =========================================================
    # TEST DE PUNTO EN HAZ (CORREGIDO)
    # =========================================================
    def point_in_beam(self, p_rel):

        axis, u, v = self._beam_basis()

        d = np.dot(p_rel, axis)
        if d < 0 or d > self.R:
            return False

        # Ancho realista del haz (cónico)
        w = d * np.tan(self.bw_az / 2)
        h = d * np.tan(self.bw_el / 2)

        du = np.dot(p_rel, u)
        dv = np.dot(p_rel, v)

        # Haz elíptico realista
        return (du*du)/(w*w) + (dv*dv)/(h*h) <= 1.0


    # =========================================================
    # BEAM VOLUME (PRISMA 3D) — CORREGIDO
    # =========================================================
    def compute_beam_volume(self):

        axis, u, v = self._beam_basis()

        # Ancho realista en la punta
        w = self.R * np.tan(self.bw_az / 2)
        h = self.R * np.tan(self.bw_el / 2)

        base = np.array([0,0,0])
        tip  = axis * self.R

        b1 = base + u*10 + v*10
        b2 = base - u*10 + v*10
        b3 = base - u*10 - v*10
        b4 = base + u*10 - v*10

        t1 = tip + u*w + v*h
        t2 = tip - u*w + v*h
        t3 = tip - u*w - v*h
        t4 = tip + u*w - v*h

        vertices = np.array([b1,b2,b3,b4,t1,t2,t3,t4], dtype=float)
    

if __name__ == "__main__":
    radar = RadarSST(
        position=[0, 0, 0],
        bw_az_deg=2.0,
        bw_el_deg=2.0,
        R=1_000_000,
        az_sector=(0, 0),
        el_sector=(0, 0)
    )

    radar.az0 = 0.0
    radar.el0 = 0.0

    axis, u, v = radar._beam_basis()
    print("axis:", axis)
    print("u   :", u)
    print("v   :", v)

    # Punto claramente dentro: 500 km en +X
    p_in = np.array([500_000.0, 0.0, 0.0])
    print("IN  :", radar.point_in_beam(p_in - radar.position))

    # Punto claramente fuera en elevación: 500 km en +Z
    p_out_z = np.array([0.0, 0.0, 500_000.0])
    print("OUT Z:", radar.point_in_beam(p_out_z - radar.position))

    # Punto claramente fuera en azimut: 500 km en +Y
    p_out_y = np.array([0.0, 500_000.0, 0.0])
    print("OUT Y:", radar.point_in_beam(p_out_y - radar.position))