import time
import numpy as np

from vispy import app, scene
from vispy.scene import visuals


class RadarSimulator:

    def __init__(
        self,
        radar,
        environment,
        trail_seconds=10,
        show_dt=False,
        show_fov=False
    ):
        self.radar = radar
        self.environment = environment

        self.trail_seconds = trail_seconds
        self.show_dt = show_dt
        self.show_fov = show_fov

        self.history = []

        self.start_time = time.time()
        self.last_time = self.start_time

        self.SCALE = 1e-6

        # Canvas
        self.canvas = scene.SceneCanvas(
            keys='interactive',
            bgcolor='black',
            size=(1200, 900),
            show=True
        )
        self.view = self.canvas.central_widget.add_view()
        self.canvas.context.set_state(
            blend=True,
            depth_test=False,
            cull_face=False
        )

        # Cámara
        self.view.camera = scene.cameras.TurntableCamera(
            fov=45,
            azimuth=45,
            elevation=30,
            distance=self.radar.R * self.SCALE * 2.0
        )
        visuals.XYZAxis(parent=self.view.scene)

        # Visuales
        self.trail_scatter = visuals.Markers(parent=self.view.scene)

        self.radar_origin = visuals.Markers(parent=self.view.scene)
        self.radar_origin.set_data(
            pos=np.array([[0.0, 0.0, 0.0]]),
            face_color='red',
            size=12
        )

        self.beam_mesh = visuals.Mesh(
            parent=self.view.scene,
            color=(0.4, 1.0, 1.0, 0.35),
            shading='smooth'
        )

        self.points_scatter = visuals.Markers(parent=self.view.scene)
        self.sat_scatter = visuals.Markers(parent=self.view.scene)

        # Precomputar caras del cono (N fijo)
        self.N_BEAM = 32
        faces = []
        for i in range(self.N_BEAM):
            i1 = i + 1
            i2 = 1 if i == self.N_BEAM - 1 else i + 2
            faces.append([0, i1, i2])
        self._beam_faces = np.array(faces, dtype=np.int32)

        # Timer
        self.timer = app.Timer(
            interval=0.05,
            connect=self._on_timer,
            start=True
        )

    def _on_timer(self, event):
        self.step()
        self.canvas.update()

    def _update_beam_mesh(self):
        axis, u, v = self.radar._beam_basis()

        base = np.array([0.0, 0.0, 0.0])
        tip = axis * self.radar.R

        radius_az = self.radar.R * np.tan(self.radar.bw_az / 2.0)
        radius_el = self.radar.R * np.tan(self.radar.bw_el / 2.0)

        i = np.arange(self.N_BEAM)
        ang = 2.0 * np.pi * i / self.N_BEAM
        cos_a = np.cos(ang)
        sin_a = np.sin(ang)

        circle = (
            tip
            + np.outer(cos_a * radius_az, u)
            + np.outer(sin_a * radius_el, v)
        )

        vertices = np.vstack([base, circle])
        vertices = (vertices + self.radar.position) * self.SCALE

        self.beam_mesh.set_data(
            vertices=vertices,
            faces=self._beam_faces,
            color=(0.4, 1.0, 1.0, 0.35)
        )

    def _update_trail(self, now):
        now_pos = np.array([
            self.radar.R * np.cos(self.radar.el0) * np.cos(self.radar.az0),
            self.radar.R * np.cos(self.radar.el0) * np.sin(self.radar.az0),
            self.radar.R * np.sin(self.radar.el0)
        ])

        self.history.append([now, *now_pos])
        cutoff = now - self.trail_seconds
        self.history = [h for h in self.history if h[0] >= cutoff]

        if self.history:
            hist = np.array(self.history)
            trail = hist[:, 1:4] * self.SCALE
        else:
            trail = np.empty((0, 3))

        self.trail_scatter.set_data(
            pos=trail,
            face_color='blue',
            edge_color=None,
            size=5
        )

    def _update_points(self):
        pts = self.environment.get_points()
        if len(pts) == 0:
            self.points_scatter.set_data(pos=np.empty((0, 3)))
            return

        pts = np.asarray(pts)
        pts_rel = pts - self.radar.position

        inside = np.array([self.radar.point_in_beam(pr) for pr in pts_rel])

        detected_pts = pts[inside] * self.SCALE
        nondetected_pts = pts[~inside] * self.SCALE

        all_pos = np.vstack((nondetected_pts, detected_pts))

        colors_nd = np.tile((1.0, 0.6, 0.2, 0.6), (len(nondetected_pts), 1))
        colors_d  = np.tile((1.0, 0.0, 0.0, 1.0), (len(detected_pts), 1))
        all_colors = np.vstack((colors_nd, colors_d))

        sizes_nd = np.full(len(nondetected_pts), 3)
        sizes_d  = np.full(len(detected_pts), 10)
        all_sizes = np.hstack((sizes_nd, sizes_d))

        self.points_scatter.set_data(
            pos=all_pos,
            face_color=all_colors,
            size=all_sizes,
            edge_color=None
        )

    def _update_sats(self):
        sats = self.environment.get_satellite_positions()
        if len(sats) == 0:
            self.sat_scatter.set_data(pos=np.empty((0, 3)))
            return

        sats = np.asarray(sats)
        sats_rel = sats - self.radar.position

        inside = np.array([self.radar.point_in_beam(sr) for sr in sats_rel])

        detected_sats = sats[inside] * self.SCALE
        nondetected_sats = sats[~inside] * self.SCALE

        all_pos = np.vstack((nondetected_sats, detected_sats))

        colors_nd = np.tile((1.0, 0.6, 0.2, 0.6), (len(nondetected_sats), 1))
        colors_d  = np.tile((1.0, 0.0, 0.0, 1.0), (len(detected_sats), 1))
        all_colors = np.vstack((colors_nd, colors_d))

        sizes_nd = np.full(len(nondetected_sats), 8)
        sizes_d  = np.full(len(detected_sats), 14)
        all_sizes = np.hstack((sizes_nd, sizes_d))

        self.sat_scatter.set_data(
            pos=all_pos,
            face_color=all_colors,
            size=all_sizes,
            edge_color=None,
            symbol='+'
        )

    def step(self):
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        if self.show_dt:
            print(f"dt = {dt:.4f} s")

        self.radar.update(dt)
        self.environment.update(dt)

        self._update_beam_mesh()
        self._update_trail(now)
        self._update_points()
        self._update_sats()

        self.radar_origin.set_data(
            pos=np.array([[0.0, 0.0, 0.0]]),
            face_color='red',
            size=12
        )
