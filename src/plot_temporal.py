from pathlib import Path
import csv
import math
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
INPUT_CSV = ROOT / "results/temporal/metrics_step250_R100.csv"
OUTPUT_DIR = ROOT / "results/figures"


PLOTS = [
    (
        "temporal_fish_count",
        "Nombre de poissons observés",
        "Nombre de poissons",
        [("number_of_fish", "Poissons observés")],
        None,
    ),
    (
        "temporal_density",
        "Évolution de la densité",
        "Densité",
        [
            ("spatial_density", "Graphe spatial"),
            ("visibility_density", "Graphe de visibilité"),
        ],
        None,
    ),
    (
        "temporal_clustering",
        "Évolution du clustering",
        "Coefficient de clustering",
        [
            ("spatial_clustering", "Graphe spatial"),
            ("visibility_clustering", "Graphe de visibilité"),
        ],
        (0, 1),
    ),
    (
        "temporal_modularity",
        "Évolution de la modularité Louvain",
        "Modularité",
        [
            ("spatial_modularity", "Graphe spatial"),
            ("visibility_modularity", "Graphe de visibilité"),
        ],
        (0, 1),
    ),
    (
        "temporal_connectivity",
        "Part des poissons dans la composante principale",
        "Proportion des poissons",
        [
            (
                "spatial_largest_component_share",
                "Plus grande composante connexe spatiale",
            ),
            (
                "visibility_largest_scc_share",
                "Plus grande composante fortement connexe",
            ),
        ],
        (0, 1.02),
    ),
]


def load_metrics(path):
    print("[1/3] Chargement du CSV...", flush=True)

    with Path(path).open(
        "r", encoding="utf-8", newline=""
    ) as file:
        reader = csv.DictReader(file)

        required = {"frame_id", "time_seconds"}
        for _, _, _, series, _ in PLOTS:
            required.update(column for column, _ in series)

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Colonnes absentes : {sorted(missing)}"
            )

        rows = [
            {column: float(value) for column, value in row.items()
             if column in required}
            for row in reader
        ]

    if not rows:
        raise ValueError("Le CSV ne contient aucune observation.")

    if any(
        not math.isfinite(value)
        for row in rows
        for value in row.values()
    ):
        raise ValueError("Le CSV contient des valeurs non finies.")

    rows.sort(key=lambda row: row["time_seconds"])

    print(f"[OK] {len(rows)} frames chargées.", flush=True)
    return rows


def generate_figures(
    csv_path=INPUT_CSV,
    output_dir=OUTPUT_DIR,
):
    start = time.perf_counter()
    rows = load_metrics(csv_path)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    times = [row["time_seconds"] for row in rows]
    generated = []

    print("[2/3] Génération des graphiques...", flush=True)

    for index, (filename, title, ylabel, series, ylim) in enumerate(
        PLOTS, start=1
    ):
        fig, ax = plt.subplots(figsize=(11, 6))

        for column, label in series:
            values = [row[column] for row in rows]
            ax.plot(
                times,
                values,
                marker="o",
                markersize=4,
                linewidth=1.8,
                label=label,
            )

        ax.set_title(title, fontsize=15)
        ax.set_xlabel("Temps expérimental (secondes)")
        ax.set_ylabel(ylabel)
        ax.grid(True, alpha=0.25)

        if ylim is not None:
            ax.set_ylim(*ylim)
        else:
            ax.set_ylim(bottom=0)

        ax.legend(loc="best", fontsize=9)

        fig.text(
            0.5, 0.025,
            "Données réelles | R = 100 | "
            "Angle mort arrière = 25° | "
            "21 frames échantillonnées",
            ha="center",
            fontsize=9,
        )

        fig.tight_layout(rect=(0, 0.05, 1, 1))

        for extension in ("png", "svg"):
            output = output_dir / f"{filename}.{extension}"
            fig.savefig(
                output,
                dpi=200 if extension == "png" else None,
                bbox_inches="tight",
            )
            if extension == "svg":
                svg = output.read_text(encoding="utf-8")
                output.write_text(
                    "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
                    encoding="utf-8",
                )
            generated.append(output)

        plt.close(fig)

        print(
            f"[FIGURE {index}/{len(PLOTS)}] {title} : OK",
            flush=True,
        )

    print("[3/3] Vérification des exports...", flush=True)

    for output in generated:
        if not output.is_file() or output.stat().st_size == 0:
            raise RuntimeError(f"Figure invalide : {output}")

    print(f"[OK] {len(generated)} fichiers générés.", flush=True)
    print(f"Dossier : {output_dir}", flush=True)
    print(
        f"Durée : {time.perf_counter() - start:.2f} s",
        flush=True,
    )

    return generated


if __name__ == "__main__":
    generate_figures()
