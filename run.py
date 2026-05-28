# ============================================================
# SIMULACIÓN SST COMPLETA (RadarSST + RadarSimulator + Environment)
# ============================================================


import os
from vispy import app

os.environ["VISPY_DEFAULT_BACKEND"] = "pyqt6"
os.environ["QT_OPENGL"] = "desktop"

# ------------------------------------------------------------
# IMPORTAR TUS CLASES
# ------------------------------------------------------------
from radar.radar_sst import RadarSST
from radar.radar_simulator_sst import RadarSimulator
from radar.radar_environment import RadarEnvironment
from radar.CONFIG import RADAR_CONFIGS

def create_radar_from_config(name):
    cfg = RADAR_CONFIGS[name]

    return RadarSST(
        position=[0, 0, 0],
        bw_az_deg=1,
        bw_el_deg=1,
        R=cfg["R"],
        az_sector=(10, 30),
        el_sector=(10, 40),
        scan_speed_deg_s=cfg["scan_speed_deg_s"],
        dwell_time=cfg["dwell_time"],
        mode=cfg["mode"],
        scan_pattern=cfg["scan_pattern"]
    )



# ------------------------------------------------------------
# CONFIGURACIÓN DEL RADAR SST
# ------------------------------------------------------------
radar = create_radar_from_config("scanLEO")

# ------------------------------------------------------------
# ENTORNO ORBITAL
# ------------------------------------------------------------
env = RadarEnvironment(radar, n_points=0, n_sats=3000, radius=800)

# ------------------------------------------------------------
# SIMULADOR
# ------------------------------------------------------------
# Puedes ajustar el número de satélites LEO aquí
sim = RadarSimulator(
    radar=radar,            # pasar el radar al simulador
    environment=env,        # pasar el entorno al simulador
    trail_seconds=100,       # mostrar estela de 10 segundos
    show_fov=True,          # mostrar el FOV completo en cada frame
    show_dt=False,           # mostrar tiempo entre frames en consola
)
 

app.run()