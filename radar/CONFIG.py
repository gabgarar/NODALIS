RADAR_CONFIGS = {

    # ---------------------------------------------------------
    # 1) SEARCH RÁPIDO (tipo Space Fence)
    # ---------------------------------------------------------
    "search_fast": {
        "bw_az_deg": 1.0,
        "bw_el_deg": 1.0,
        "R": 2_000_000,
        "az_sector": (0, 45),
        "el_sector": (50, 70),
        "scan_speed_deg_s": 20,
        "dwell_time": 0.001,
        "mode": "search",
        "scan_pattern": "raster"
    },

    # ---------------------------------------------------------
    # 2) SEARCH ESTÁNDAR SST
    # ---------------------------------------------------------
    "search_standard": {
        "bw_az_deg": 5.0,
        "bw_el_deg": 5.0,
        "R": 400,
        "az_sector": (90, 180),
        "el_sector": (10, 45),
        "scan_speed_deg_s": 10,
        "dwell_time": 0.003,
        "mode": "search",
        "scan_pattern": "raster"
    },

    # ---------------------------------------------------------
    # 3) SEARCH PROFUNDO (objetos pequeños)
    # ---------------------------------------------------------
    "search_deep": {
        "bw_az_deg": 1.0,
        "bw_el_deg": 1.0,
        "R": 2_000_000,
        "az_sector": (0, 45),
        "el_sector": (50, 70),
        "scan_speed_deg_s": 5,
        "dwell_time": 0.008,
        "mode": "search",
        "scan_pattern": "raster"
    },

    # ---------------------------------------------------------
    # 4) TRACKING (seguimiento de un objeto)
    # ---------------------------------------------------------
    "tracking": {
        "bw_az_deg": 1.0,
        "bw_el_deg": 1.0,
        "R": 2_000_000,
        "az_sector": (20, 25),
        "el_sector": (55, 60),
        "scan_speed_deg_s": 1,
        "dwell_time": 0.02,
        "mode": "tracking",
        "scan_pattern": "pingpong"
    },

    # ---------------------------------------------------------
    # 5) WIDE SEARCH (sector muy amplio)
    # ---------------------------------------------------------
    "wide_search": {
        "bw_az_deg": 1.0,
        "bw_el_deg": 1.0,
        "R": 2_000_000,
        "az_sector": (-30, 60),
        "el_sector": (40, 80),
        "scan_speed_deg_s": 15,
        "dwell_time": 0.002,
        "mode": "search",
        "scan_pattern": "raster"
    },

    # ---------------------------------------------------------
    # 6) HIGH-RES (haz estrecho)
    # ---------------------------------------------------------
    "high_res": {
        "bw_az_deg": 0.5,
        "bw_el_deg": 0.5,
        "R": 2_000_000,
        "az_sector": (0, 45),
        "el_sector": (50, 70),
        "scan_speed_deg_s": 10,
        "dwell_time": 0.002,
        "mode": "search",
        "scan_pattern": "raster"
    },

    # ---------------------------------------------------------
    # 7) LOW-RES (haz estrecho)
    # ---------------------------------------------------------
    "low_res": {
        "bw_az_deg": 10,
        "bw_el_deg": 10,
        "R": 2_000_000,
        "az_sector": (0, 45),
        "el_sector": (50, 70),
        "scan_speed_deg_s": 10,
        "dwell_time": 0.002,
        "mode": "search",
        "scan_pattern": "raster"
    },

    
}
