"""Interface interactive : poissons réels, inertie et Boids.

Fenêtres disponibles : 1–32, 2000–2031, 4000–4031.
Simulation sans utilisation des positions futures.
Cohorte fixe : poissons présents pendant toute la fenêtre.
"""

from dataclasses import replace

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.widgets import Button, TextBox

from src.leader_display import (
    load_leaders,
    selected_leaders,
    fish_colors,
)

from src.boids_pilot import (
    BoidsParameters,
    initial_state,
    load_observations,
    positions_from_frame,
    step_boids,
    step_persistence,
)
from src.compare_boids_graphs import make_frame
from src.graph_builder import build_graph
from src.validate_boids_windows import load_windows


HORIZON = 30
RADIUS = 100
WINDOW_STARTS = (1, 2000, 4000)


def prepare_paths(start, params, frames=None, horizon=HORIZON):
    if start not in WINDOW_STARTS:
        raise ValueError(
            "Fenêtre autorisée : 1, 2000 ou 4000."
        )

    params.validate()

    if frames is None:
        if start == 1:
            frames = load_observations(horizon=horizon)
        else:
            frames = load_windows(
                starts=(start,),
                horizon=horizon,
            )[start]

    ids, initial_xy, initial_v = initial_state(
        frames[1], frames[2]
    )

    survivors = set(map(int, ids))
    positions = {}

    for k in range(1, horizon + 3):
        fish_ids, xy = positions_from_frame(frames[k])
        positions[k] = {
            int(fish_id): p
            for fish_id, p in zip(fish_ids, xy)
        }
        survivors.intersection_update(positions[k])

    if not survivors:
        raise ValueError(
            "Aucune trajectoire continue."
        )

    selected = np.array([
        i for i, fish_id in enumerate(ids)
        if int(fish_id) in survivors
    ], dtype=int)

    ids = ids[selected]
    initial_xy = initial_xy[selected]
    initial_v = initial_v[selected]

    real = np.stack([
        np.stack([
            positions[k][int(fish_id)]
            for fish_id in ids
        ])
        for k in range(1, horizon + 3)
    ])

    inertia = [real[0].copy(), real[1].copy()]
    boids = [real[0].copy(), real[1].copy()]

    inertial_xy = initial_xy.copy()
    inertial_v = initial_v.copy()
    boids_xy = initial_xy.copy()
    boids_v = initial_v.copy()

    for _ in range(horizon):
        inertial_xy, inertial_v = step_persistence(
            inertial_xy, inertial_v
        )
        boids_xy, boids_v = step_boids(
            boids_xy, boids_v, params
        )
        inertia.append(inertial_xy.copy())
        boids.append(boids_xy.copy())

    return ids, (
        real,
        np.stack(inertia),
        np.stack(boids),
    )


def interface_metrics(positions, previous_positions, radius=RADIUS):
    """Polarisation et degré moyen sur la cohorte affichée."""
    velocity = positions - previous_positions
    speed = np.linalg.norm(velocity, axis=1)
    moving = speed > 1e-12

    if np.any(moving):
        directions = velocity[moving] / speed[moving, None]
        polarization = float(np.linalg.norm(directions.mean(axis=0)))
    else:
        polarization = float("nan")

    delta = positions[:, None, :] - positions[None, :, :]
    distances = np.linalg.norm(delta, axis=2)
    adjacency = distances < radius
    np.fill_diagonal(adjacency, False)
    mean_degree = float(adjacency.sum(axis=1).mean())

    return polarization, mean_degree


def interface_angular_error(real_velocity, simulated_velocity):
    """Erreur angulaire moyenne, en degrés, hors vitesses nulles."""
    real_speed = np.linalg.norm(real_velocity, axis=1)
    sim_speed = np.linalg.norm(simulated_velocity, axis=1)
    valid = (real_speed > 1e-12) & (sim_speed > 1e-12)

    if not np.any(valid):
        return float("nan")

    cosines = np.sum(
        real_velocity[valid] * simulated_velocity[valid],
        axis=1,
    ) / (real_speed[valid] * sim_speed[valid])

    return float(np.degrees(
        np.arccos(np.clip(cosines, -1.0, 1.0))
    ).mean())



def fish_triangles(positions, velocities, length=16.0, width=9.0):
    """Triangles orientés selon le déplacement de chaque poisson."""
    positions = np.asarray(positions, dtype=float)
    velocities = np.asarray(velocities, dtype=float)

    if positions.shape != velocities.shape:
        raise ValueError("Positions et vitesses incompatibles.")
    if positions.ndim != 2 or positions.shape[1] != 2:
        raise ValueError("Tableaux de forme (N, 2) attendus.")

    speed = np.linalg.norm(velocities, axis=1)
    direction = np.zeros_like(velocities)

    moving = speed > 1e-12
    direction[moving] = (
        velocities[moving] / speed[moving, None]
    )

    # Orientation par défaut si le poisson est immobile.
    direction[~moving] = [1.0, 0.0]

    perpendicular = np.column_stack((
        -direction[:, 1],
        direction[:, 0],
    ))

    tip = positions + direction * (length * 0.65)
    rear = positions - direction * (length * 0.35)

    left = rear + perpendicular * (width / 2)
    right = rear - perpendicular * (width / 2)

    return np.stack((tip, left, right), axis=1)


class BoidsInterface:
    def __init__(self):
        self.start = 1
        self.horizon = HORIZON
        self.cache = {}
        self.show_edges = True
        self.leader_mode = "OFF"
        self.leader_phases, self.persistent_leaders = load_leaders()
        self.playing = True
        self.index = 1

        self.fig, self.axes = plt.subplots(
            1, 3, figsize=(15, 7)
        )

        self.fig.subplots_adjust(
            left=0.045,
            right=0.985,
            top=0.87,
            bottom=0.38,
            wspace=0.17,
        )

        self.scatters = []
        self.lines = []
        self.leader_markers = []
        self.leader_labels = []

        for ax in self.axes:
            marker = ax.scatter(
                [], [],
                s=110,
                c="#dc2626",
                edgecolors="#7f1d1d",
                linewidths=1.0,
                marker="^",
                zorder=10,
            )
            self.leader_markers.append(marker)
            self.leader_labels.append([])

        for ax in self.axes:
            ax.set_aspect("equal", adjustable="box")
            ax.set_xlabel("x (unité native)")
            ax.set_ylabel("y (unité native)")
            ax.grid(alpha=0.15)

            line = LineCollection(
                [], linewidths=0.4, alpha=0.30
            )
            ax.add_collection(line)

            scatter = PolyCollection(
                [],
                facecolors="#1f77b4",
                edgecolors="#155a8a",
                linewidths=0.35,
                zorder=3,
            )
            ax.add_collection(scatter)

            self.lines.append(line)
            self.scatters.append(scatter)

        fields = (
            ("Séparation", 0.055, "0.005"),
            ("Alignement", 0.245, "0.05"),
            ("Cohésion", 0.435, "0.005"),
            ("Début", 0.625, "1"),
        )

        self.textboxes = []

        for label, x, value in fields:
            self.fig.text(x, 0.197, label, fontsize=9)
            box = TextBox(
                self.fig.add_axes([
                    x, 0.13, 0.13, 0.055
                ]),
                "",
                initial=value,
            )
            self.textboxes.append(box)

        self.fig.text(
            0.055, 0.113, "Horizon (frames)", fontsize=9
        )
        self.horizon_box = TextBox(
            self.fig.add_axes([0.055, 0.065, 0.13, 0.045]),
            "",
            initial="150",
        )

        self.restart_button = Button(
            self.fig.add_axes([
                0.815, 0.13, 0.15, 0.055
            ]),
            "Redémarrer",
        )

        self.pause_button = Button(
            self.fig.add_axes([
                0.815, 0.065, 0.15, 0.045
            ]),
            "Pause",
        )

        self.edges_button = Button(
            self.fig.add_axes([
                0.585, 0.065, 0.19, 0.045
            ]),
            "Arêtes spatiales : ON",
        )

        self.calibrated_button = Button(
            self.fig.add_axes([0.345, 0.065, 0.205, 0.045]),
            "Paramètres calibrés",
        )

        self.leaders_button = Button(
            self.fig.add_axes([0.585, 0.012, 0.38, 0.042]),
            "Leaders : OFF",
        )
        self.leaders_button.on_clicked(self.toggle_leaders)

        self.calibrated_button.on_clicked(
            self.restore_calibrated
        )

        self.restart_button.on_clicked(self.restart)
        self.pause_button.on_clicked(self.toggle_pause)
        self.edges_button.on_clicked(self.toggle_edges)

        self.status = self.fig.text(
            0.05, 0.94, "", fontsize=10
        )

        self.fig.text(
            0.05, 0.035,
            "R réseau = 100 | Angle mort arrière = 25° | "
            "Simulation sans frontières",
            fontsize=9,
        )

        self.metrics_text = self.fig.text(
            0.05, 0.335, "",
            fontsize=9,
            va="top",
            family="monospace",
        )

        self.angular_text = self.fig.text(
            0.05, 0.255, "",
            fontsize=9,
            va="top",
        )

        self.restart(None)

        self.timer = self.fig.canvas.new_timer(
            interval=180
        )
        self.timer.add_callback(self.advance)
        self.timer.start()

    def frames_for(self, start, horizon):
        key = (start, horizon)
        if key not in self.cache:
            if start == 1:
                frames = load_observations(
                    horizon=horizon
                )
            else:
                frames = load_windows(
                    starts=(start,),
                    horizon=horizon,
                )[start]

            self.cache[key] = frames

        return self.cache[key]

    def restart(self, _):
        try:
            start = int(
                self.textboxes[3].text.strip()
            )

            horizon = int(self.horizon_box.text.strip())

            if horizon not in (30, 60, 150, 300):
                raise ValueError(
                    "Horizon autorisé : 30, 60, 150 ou 300."
                )

            if start + horizon + 1 > 5000:
                raise ValueError(
                    "Fenêtre dépassant les 5000 frames."
                )

            weights = [
                float(box.text.strip())
                for box in self.textboxes[:3]
            ]

            params = replace(
                BoidsParameters(),
                weight_separation=weights[0],
                weight_alignment=weights[1],
                weight_cohesion=weights[2],
            )

            params.validate()

            self.status.set_text(
                "Chargement et simulation..."
            )
            self.fig.canvas.draw_idle()

            ids, paths = prepare_paths(
                start,
                params,
                self.frames_for(start, horizon),
                horizon=horizon,
            )

            self.ids = ids
            self.paths = paths
            self.start = start
            self.horizon = horizon

            self.id_index = {
                int(fish_id): i
                for i, fish_id in enumerate(ids)
            }

            all_xy = np.concatenate([
                arr.reshape(-1, 2)
                for arr in paths
            ])

            mins = all_xy.min(axis=0)
            maxs = all_xy.max(axis=0)
            margins = np.maximum(
                (maxs - mins) * 0.06, 1.0
            )

            for ax in self.axes:
                ax.set_xlim(
                    mins[0] - margins[0],
                    maxs[0] + margins[0],
                )
                ax.set_ylim(
                    mins[1] - margins[1],
                    maxs[1] + margins[1],
                )

            self.index = 1
            self.playing = True
            self.pause_button.label.set_text(
                "Pause"
            )
            self.render()

        except (ValueError, OSError, KeyError) as exc:
            self.status.set_text(
                f"Erreur : {exc}"
            )
            self.fig.canvas.draw_idle()

    def render(self):
        labels = (
            "Inertie",
            "Observations réelles",
            "Boids interactif",
        )

        display_order = (1, 0, 2)

        active_leaders = selected_leaders(
            self.leader_mode,
            self.start + self.index,
            self.start,
            self.horizon,
            self.leader_phases,
            self.persistent_leaders,
        )
        colors = fish_colors(self.ids, active_leaders)

        for ax, scatter, line, path_index, name in zip(
            self.axes,
            self.scatters,
            self.lines,
            display_order,
            labels,
        ):
            paths = self.paths[path_index]
            xy = paths[self.index]

            if self.index > 0:
                velocity = (
                    paths[self.index]
                    - paths[self.index - 1]
                )
            else:
                velocity = paths[1] - paths[0]

            # Poissons ordinaires : triangles bleus agrandis.
            triangles = fish_triangles(
                xy, velocity,
                length=24.0,
                width=13.5,
            )

            # Leaders : même triangle orienté, mais plus grand.
            leader_indices = [
                i for i, fish_id in enumerate(self.ids)
                if int(fish_id) in active_leaders
            ]

            if leader_indices:
                leader_triangles = fish_triangles(
                    xy[leader_indices],
                    velocity[leader_indices],
                    length=35.0,
                    width=20.0,
                )
                triangles[leader_indices] = leader_triangles

            scatter.set_verts(triangles)
            scatter.set_facecolors(colors)
            scatter.set_edgecolors([
                "#991b1b" if int(fish_id) in active_leaders
                else "#155a8a"
                for fish_id in self.ids
            ])

            panel_index = list(self.axes).index(ax)

            for label in self.leader_labels[panel_index]:
                label.remove()

            self.leader_labels[panel_index] = []

            leader_indices = [
                i for i, fish_id in enumerate(self.ids)
                if int(fish_id) in active_leaders
            ]

            if leader_indices:
                leader_xy = xy[leader_indices]
            else:
                leader_xy = np.empty((0, 2))

            # Désactiver le marqueur rouge fixe :
            # le triangle orienté est désormais coloré directement.
            self.leader_markers[panel_index].set_offsets(
                np.empty((0, 2))
            )

            for i in leader_indices:
                label = ax.annotate(
                    str(int(self.ids[i])),
                    xy=xy[i],
                    xytext=(7, 7),
                    textcoords="offset points",
                    fontsize=8,
                    fontweight="bold",
                    color="#b91c1c",
                    zorder=11,
                )
                self.leader_labels[panel_index].append(label)

            if self.show_edges:
                frame = make_frame(
                    self.ids,
                    xy,
                    np.zeros_like(xy),
                )

                graph = build_graph(
                    frame, radius=RADIUS
                )

                segments = [
                    xy[[
                        self.id_index[u],
                        self.id_index[v],
                    ]]
                    for u, v in graph.edges()
                ]

                line.set_segments(segments)
            else:
                line.set_segments([])

            ax.set_title(name)

        truth = self.paths[0][self.index]

        inertia_error = np.linalg.norm(
            self.paths[1][self.index] - truth,
            axis=1,
        ).mean()

        boids_error = np.linalg.norm(
            self.paths[2][self.index] - truth,
            axis=1,
        ).mean()

        self.status.set_text(
            f"Frame {self.start + self.index} | "
            f"{len(self.ids)} poissons | "
            f"Horizon {self.horizon} frames | "
            f"Erreur inertie : {inertia_error:.2f} | "
            f"Erreur Boids : {boids_error:.2f}"
        )

        if self.index >= 1:
            metrics = []

            for paths in self.paths:
                current = paths[self.index]
                previous = paths[self.index - 1]
                metrics.append(
                    interface_metrics(current, previous)
                )

            display_metrics = [
                metrics[i] for i in (1, 0, 2)
            ]

            self.metrics_text.set_text(
                "Polarisation : "
                + " | ".join(
                    f"{value[0]:.3f}" for value in display_metrics
                )
                + "\nDegré moyen  : "
                + " | ".join(
                    f"{value[1]:.2f}" for value in display_metrics
                )
                + "\nOrdre : Inertie | Réel | Boids"
            )

            real_velocity = (
                self.paths[0][self.index]
                - self.paths[0][self.index - 1]
            )

            inertial_velocity = (
                self.paths[1][self.index]
                - self.paths[1][self.index - 1]
            )

            boids_velocity = (
                self.paths[2][self.index]
                - self.paths[2][self.index - 1]
            )

            inertia_angle = interface_angular_error(
                real_velocity, inertial_velocity
            )
            boids_angle = interface_angular_error(
                real_velocity, boids_velocity
            )

            self.angular_text.set_text(
                f"Erreur angulaire : "
                f"Inertie {inertia_angle:.2f}° | "
                f"Boids {boids_angle:.2f}°"
            )

        self.fig.canvas.draw_idle()

    def advance(self):
        if self.playing:
            self.index = (
                self.index + 1
            ) % len(self.paths[0])

            self.render()

    def restore_calibrated(self, _):
        """Alterner entre les configurations optimisées."""
        presets = (
            ("Jaccard", ("0.005", "0.05", "0.005")),
            ("Position H30", ("0.025", "0.3", "0.01")),
            ("Ancienne", ("0", "0.15", "0")),
        )

        current = tuple(
            box.text.strip() for box in self.textboxes[:3]
        )

        current_index = next(
            (
                i for i, (_, values) in enumerate(presets)
                if values == current
            ),
            -1,
        )

        next_index = (current_index + 1) % len(presets)
        name, values = presets[next_index]

        for box, value in zip(self.textboxes[:3], values):
            box.set_val(value)

        self.status.set_text(
            f"Configuration {name} chargée : "
            "cliquer sur Redémarrer pour l'appliquer."
        )
        self.fig.canvas.draw_idle()

    def toggle_pause(self, _):
        self.playing = not self.playing

        self.pause_button.label.set_text(
            "Pause" if self.playing
            else "Reprendre"
        )

        self.fig.canvas.draw_idle()

    def toggle_leaders(self, _):
        modes = ("OFF", "Phase", "Persistants")
        index = modes.index(self.leader_mode)
        self.leader_mode = modes[(index + 1) % len(modes)]

        self.leaders_button.label.set_text(
            f"Leaders : {self.leader_mode}"
        )
        self.render()

    def toggle_edges(self, _):
        self.show_edges = not self.show_edges

        self.edges_button.label.set_text(
            "Arêtes spatiales : ON"
            if self.show_edges
            else "Arêtes spatiales : OFF"
        )

        self.render()


def main():
    if plt.get_backend().lower() in {"agg", "pdf", "svg", "ps", "template"}:
        raise RuntimeError(
            "Backend Matplotlib non interactif. "
            "Lancer depuis le Terminal macOS."
        )

    app = BoidsInterface()
    plt.show(block=True)
    return app


if __name__ == "__main__":
    main()
