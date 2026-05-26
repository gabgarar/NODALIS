"""ping-pong SST demo

→→→→→→→→→→→→→→→→→→→
↑ salto altitud
←←←←←←←←←←←←←←←←←←←
↑ salto
→→→→→→→→→→→→→→→→→→→
↑ salto
←←←←←←←←←←←←←←←←←←←

raster SST demo
→→→→→→→→→→→→→→→→→→→
↑ salto
→→→→→→→→→→→→→→→→→→→
↑ salto
→→→→→→→→→→→→→→→→→→→
↑ salto
→→→→→→→→→→→→→→→→→→→



"""



import numpy as np
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

        # Beamwidth
        self.bw_az = np.radians(bw_az_deg)
        self.bw_el = np.radians(bw_el_deg)

        # Alcance
        self.R = R

        # Sector
        self.az_min = np.radians(az_sector[0])
        self.az_max = np.radians(az_sector[1])
        self.el_min = np.radians(el_sector[0])
        self.el_max = np.radians(el_sector[1])

        # Estado del haz
        self.az0 = self.az_min
        self.el0 = self.el_min

        # Velocidad
        self.scan_speed = np.radians(scan_speed_deg_s)
        self.scan_dir_az = 1

        # Modo de operación
        self.mode = mode
        self.scan_pattern = scan_pattern   # ⭐ NUEVO

    # ---------------------------------------------------------
    # MODO SEARCH: barrido electrónico en sector
    # ---------------------------------------------------------
    def update_search(self, dt):
        # Acumular dwell
        self._dwell_accum += dt
        if self._dwell_accum < self.dwell_time:
            return
        self._dwell_accum = 0.0

        # Paso angular fijo por dwell
        delta_az = self.scan_dir_az * self.scan_speed * self.dwell_time
        self.az0 += delta_az

        # ---------------------------------------------------------
        # ⭐ MODO 1: RASTER (moderno SST)
        # ---------------------------------------------------------
        if self.scan_pattern == "raster":
            if self.az0 > self.az_max:
                self.az0 = self.az_min
                self.el0 += self.bw_el * 0.6

            if self.el0 > self.el_max:
                self.el0 = self.el_min

        # ---------------------------------------------------------
        # ⭐ MODO 2: PING-PONG (clásico)
        # ---------------------------------------------------------
        elif self.scan_pattern == "pingpong":
            # Rebote en el borde derecho
            if self.az0 > self.az_max:
                self.az0 = self.az_max
                self.scan_dir_az = -1

            # Rebote en el borde izquierdo
            elif self.az0 < self.az_min:
                self.az0 = self.az_min
                self.scan_dir_az = 1

            # Salto vertical solo cuando completamos un ciclo
            if self.scan_dir_az == 1 and self.az0 == self.az_min:
                self.el0 += self.bw_el * 0.6

            if self.el0 > self.el_max:
                self.el0 = self.el_min

    # ---------------------------------------------------------
    # MODO TRACKING: apuntar a un objetivo concreto
    # ---------------------------------------------------------
    def point_to(self, target_pos):
        rel = target_pos - self.position
        x, y, z = rel

        self.az0 = np.arctan2(y, x)
        self.el0 = np.arctan2(z, np.sqrt(x*x + y*y))

    # ---------------------------------------------------------
    # UPDATE GENERAL
    # ---------------------------------------------------------
    def update(self, dt, target_pos=None):
        if self.mode == "search":
            self.update_search(dt)
        elif self.mode == "tracking" and target_pos is not None:
            self.point_to(target_pos)

    # ---------------------------------------------------------
    # GEOMETRÍA DEL HAZ (para dibujar)
    # ---------------------------------------------------------
    def compute_beam(self, resolution=20):
        """
        Genera el haz 3D original (parche curvado) usando bw_az y bw_el.
        Devuelve X, Y, Z en coordenadas absolutas.
        """

        az0 = self.az0
        el0 = self.el0

        # Rango angular del haz
        az_span = np.linspace(az0 - self.bw_az/2, az0 + self.bw_az/2, resolution)
        el_span = np.linspace(el0 - self.bw_el/2, el0 + self.bw_el/2, resolution)

        AZ, EL = np.meshgrid(az_span, el_span)

        R = self.R

        # Conversión a coordenadas cartesianas
        X = R * np.cos(EL) * np.cos(AZ)
        Y = R * np.cos(EL) * np.sin(AZ)
        Z = R * np.sin(EL)

        return X, Y, Z

    def set_dwell_time(self, dwell):
        # límites físicos razonables
        if dwell < 0.0005:
            dwell = 0.0005   # 0.5 ms mínimo
        if dwell > 0.02:
            dwell = 0.02     # 20 ms máximo

        self.dwell_time = dwell

    def get_fov(self, resolution=40):
        """
        Devuelve las mallas X, Y, Z del FOV completo del radar.
        No dibuja nada: solo genera los datos.
        """

        import numpy as np

        az_fov = np.linspace(self.az_min, self.az_max, resolution)
        el_fov = np.linspace(self.el_min, self.el_max, resolution)

        AZ, EL = np.meshgrid(az_fov, el_fov)

        R = self.R

        X = R * np.cos(EL) * np.cos(AZ)
        Y = R * np.cos(EL) * np.sin(AZ)
        Z = R * np.sin(EL)

        return X, Y, Z, az_fov, el_fov
    
    def compute_beam_volume(self):
        """
        Devuelve las 8 esquinas del volumen rectangular del haz (prisma 3D)
        en COORDENADAS RELATIVAS al radar (0,0,0).
        """

        az0 = self.az0
        el0 = self.el0

        # Vectores ortogonales al eje del haz
        u = np.array([-np.sin(az0), np.cos(az0), 0])  # horizontal
        v = np.array([
            -np.sin(el0)*np.cos(az0),
            -np.sin(el0)*np.sin(az0),
            np.cos(el0)
        ])  # vertical

        # Tamaño del haz en metros
        w = self.R * self.bw_az
        h = self.R * self.bw_el

        # Centro de la punta del haz (RELATIVO)
        tip = np.array([
            self.R * np.cos(el0) * np.cos(az0),
            self.R * np.cos(el0) * np.sin(az0),
            self.R * np.sin(el0)
        ])

        # Base del haz (en el radar)
        base = np.array([0, 0, 0])

        # Esquinas de la base (pequeñas)
        b1 = base + u*w*0.02 + v*h*0.02
        b2 = base - u*w*0.02 + v*h*0.02
        b3 = base - u*w*0.02 - v*h*0.02
        b4 = base + u*w*0.02 - v*h*0.02

        # Esquinas de la punta (grandes)
        t1 = tip + u*w/2 + v*h/2
        t2 = tip - u*w/2 + v*h/2
        t3 = tip - u*w/2 - v*h/2
        t4 = tip + u*w/2 - v*h/2

        return np.array([b1, b2, b3, b4, t1, t2, t3, t4])
    

    def point_in_beam(self, p_rel):
        """
        p_rel: punto en coordenadas relativas al radar (0,0,0)
        Devuelve True si está dentro del haz rectangular.
        """

        az = self.az0
        el = self.el0

        # Eje del haz
        axis = np.array([
            np.cos(el)*np.cos(az),
            np.cos(el)*np.sin(az),
            np.sin(el)
        ])

        # Vectores ortogonales
        u = np.array([-np.sin(az), np.cos(az), 0])
        v = np.array([
            -np.sin(el)*np.cos(az),
            -np.sin(el)*np.sin(az),
            np.cos(el)
        ])

        # Proyección sobre el eje
        d = np.dot(p_rel, axis)
        if d < 0 or d > self.R:
            return False

        # Proyección lateral
        du = np.dot(p_rel, u)
        dv = np.dot(p_rel, v)

        w = self.R * self.bw_az / 2
        h = self.R * self.bw_el / 2

        return abs(du) <= w and abs(dv) <= h



    def info(self):

        print("\n" + "="*60)
        print("📡  RADAR SST — INFORME DE CONFIGURACIÓN")
        print("="*60)

        # -------------------------
        # 1. Parámetros básicos
        # -------------------------
        print("\n[1] Parámetros básicos")
        print(f"  • Posición: {self.position}")
        print(f"  • Alcance máximo (R): {self.R/1000:.1f} km")
        print(f"  • Modo actual: {self.mode}")
        print(f"  • Patrón de escaneo: {self.scan_pattern}")

        # -------------------------
        # 2. Beamwidth
        # -------------------------
        bw_az_deg = np.degrees(self.bw_az)
        bw_el_deg = np.degrees(self.bw_el)
        print("\n[2] Beamwidth (tamaño del haz)")
        print(f"  • Beamwidth azimut: {bw_az_deg:.2f}°")
        print(f"  • Beamwidth elevación: {bw_el_deg:.2f}°")
        print(f"  • Salto vertical entre líneas: {0.6 * bw_el_deg:.2f}°")

        # -------------------------
        # 3. Sector
        # -------------------------
        az_min_deg = np.degrees(self.az_min)
        az_max_deg = np.degrees(self.az_max)
        el_min_deg = np.degrees(self.el_min)
        el_max_deg = np.degrees(self.el_max)

        print("\n[3] Sector de vigilancia")
        print(f"  • Azimut: {az_min_deg:.1f}° → {az_max_deg:.1f}°")
        print(f"  • Elevación: {el_min_deg:.1f}° → {el_max_deg:.1f}°")
        print(f"  • Ancho sector azimut: {az_max_deg - az_min_deg:.1f}°")
        print(f"  • Ancho sector elevación: {el_max_deg - el_min_deg:.1f}°")

        # -------------------------
        # 4. Escaneo
        # -------------------------
        scan_speed_deg = np.degrees(self.scan_speed)
        delta_az = scan_speed_deg * self.dwell_time

        print("\n[4] Parámetros de escaneo")
        print(f"  • Velocidad del haz: {scan_speed_deg:.2f}°/s")
        print(f"  • Dwell time: {self.dwell_time*1000:.2f} ms")
        print(f"  • Paso angular por dwell (Δaz): {delta_az:.4f}°")

        # -------------------------
        # 5. Oversampling
        # -------------------------
        oversampling = bw_az_deg / delta_az
        print("\n[5] Densidad angular y oversampling")
        print(f"  • Oversampling en azimut: {oversampling:.1f}×")
        if oversampling >= 1.5:
            print("    ✔ Adecuado (sin huecos)")
        else:
            print("    ✘ Bajo (puede dejar huecos)")

        # -------------------------
        # 6. Número de beams
        # -------------------------
        N_az = (az_max_deg - az_min_deg) / delta_az
        N_el = (el_max_deg - el_min_deg) / (0.6 * bw_el_deg)
        N_total = N_az * N_el

        print("\n[6] Número de beams por sector")
        print(f"  • Beams en azimut: {N_az:.0f}")
        print(f"  • Beams en elevación: {N_el:.0f}")
        print(f"  • Total de beams: {N_total:.0f}")

        # -------------------------
        # 7. Tiempo de revisita
        # -------------------------
        T_rev = N_total * self.dwell_time

        print("\n[7] Tiempo de revisita del sector")
        print(f"  • Tiempo total: {T_rev:.2f} s")
        if T_rev <= 10:
            print("    ✔ Dentro del rango típico SST (5–10 s)")
        else:
            print("    ✘ Lento para SST (ideal < 10 s)")

        # -------------------------
        # 8. Estado actual del haz
        # -------------------------
        print("\n[8] Estado actual del haz")
        print(f"  • Azimut actual: {np.degrees(self.az0):.2f}°")
        print(f"  • Elevación actual: {np.degrees(self.el0):.2f}°")

        print("="*60 + "\n")
