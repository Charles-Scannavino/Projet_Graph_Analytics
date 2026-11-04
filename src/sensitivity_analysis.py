from pathlib import Path
import csv
import math
import statistics
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RADII = (60, 80, 100, 120, 140)

METRICS = (
    "number_of_fish",
    "spatial_communities",
    "visibility_communities",
    "spatial_density",
    "visibility_density",
    "spatial_clustering",
    "visibility_clustering",
    "spatial_modularity",
    "visibility_modularity",
    "spatial_largest_component_share",
    "visibility_largest_scc_share",
    "visible_arc_fraction",
)

PLOTS = (
    (
        "communities",
        "Communautés Louvain selon le rayon",
        "Nombre moyen de communautés",
        ("spatial_communities", "visibility_communities"),
    ),
    (
        "density",
        "Densité moyenne selon le rayon",
        "Densité moyenne",
        ("spatial_density", "visibility_density"),
    ),
    (
        "clustering",
        "Clustering moyen selon le rayon",
        "Coefficient moyen de clustering",
        ("spatial_clustering", "visibility_clustering"),
    ),
    (
        "modularity",
        "Modularité Louvain selon le rayon",
        "Modularité moyenne",
        ("spatial_modularity", "visibility_modularity"),
    ),
    (
        "connectivity",
        "Connectivité des composantes principales",
        "Proportion moyenne de poissons",
        (
            "spatial_largest_component_share",
            "visibility_largest_scc_share",
        ),
    ),
)


def load_csv(path):
    print(f"[LECTURE] {path.name}", flush=True)

    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        required = set(METRICS) | {"frame_id", "time_seconds"}

        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{path.name} : colonnes absentes {sorted(missing)}"
            )

        rows = []
        for raw in reader:
            row = {
                key: float(raw[key])
                for key in required
            }
            if not all(math.isfinite(value) for value in row.values()):
                raise ValueError(f"Valeur non finie dans {path.name}")
            rows.append(row)

    if not rows:
        raise ValueError(f"CSV vide : {path.name}")

    rows.sort(key=lambda row: row["frame_id"])

    frames = [row["frame_id"] for row in rows]
    if len(set(frames)) != len(frames):
        raise ValueError(f"Frames dupliquées : {path.name}")

    return rows


def summarize(input_dir, output_dir, radii=RADII):
    print("=== ÉTUDE DE SENSIBILITÉ AU RAYON ===", flush=True)
    print("Angle mort arrière fixe : 25°", flush=True)

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    results = []
    reference = None

    for radius in radii:
        path = (
            input_dir
            / f"metrics_step250_R{radius}.csv"
        )
        rows = load_csv(path)

        current = [
            (
                row["frame_id"],
                row["time_seconds"],
                row["number_of_fish"],
            )
            for row in rows
        ]

        if reference is None:
            reference = current
        elif current != reference:
            raise ValueError(
                f"Frames ou poissons incohérents pour R={radius}"
            )

        summary = {
            "radius": radius,
            "frames": len(rows),
        }

        for metric in METRICS:
            summary[f"mean_{metric}"] = round(
                statistics.fmean(row[metric] for row in rows),
                5,
            )

        results.append(summary)

        print(
            f"[OK] R={radius} | "
            f"communautés spatiales moyennes="
            f"{summary['mean_spatial_communities']:.2f} | "
            f"densité moyenne="
            f"{summary['mean_spatial_density']:.4f}",
            flush=True,
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / "summary_step250.csv"

    with output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(results[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(results)

    print(f"[OK] Tableau comparatif : {output}", flush=True)

    return results


def plot_sensitivity(results, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    radii = [row["radius"] for row in results]
    generated = []

    for index, (name, title, ylabel, columns) in enumerate(
        PLOTS, start=1
    ):
        fig, ax = plt.subplots(figsize=(11, 6))

        for column in columns:
            values = [
                row[f"mean_{column}"]
                for row in results
            ]

            label = {
                "spatial_largest_component_share":
                    "Plus grande composante connexe spatiale",
                "visibility_largest_scc_share":
                    "Plus grande composante fortement connexe",
            }.get(
                column,
                "Spatial" if column.startswith("spatial")
                else "Visibilité (25°)",
            )

            ax.plot(
                radii,
                values,
                marker="o",
                linewidth=2,
                label=label,
            )

        ax.set_title(title)
        ax.set_xlabel("Rayon R (unités des coordonnées)")
        ax.set_ylabel(ylabel)
        ax.set_xticks(radii)
        ax.set_ylim(bottom=0)
        ax.grid(True, alpha=0.3)
        ax.legend()

        fig.text(
            0.5,
            0.025,
            "21 frames identiques | "
            "Données réelles | Angle mort = 25°",
            ha="center",
            fontsize=9,
        )

        fig.tight_layout(rect=(0, 0.05, 1, 1))

        for extension in ("png", "svg"):
            output = (
                output_dir
                / f"sensitivity_{name}.{extension}"
            )
            fig.savefig(output, dpi=200, bbox_inches="tight")

            if extension == "svg":
                text = output.read_text(encoding="utf-8")
                output.write_text(
                    "\n".join(
                        line.rstrip()
                        for line in text.splitlines()
                    ) + "\n",
                    encoding="utf-8",
                )

            generated.append(output)

        plt.close(fig)
        print(
            f"[FIGURE {index}/{len(PLOTS)}] {title} : OK",
            flush=True,
        )

    print(
        f"[OK] {len(generated)} fichiers PNG/SVG générés",
        flush=True,
    )
    return generated


def main():
    start = time.perf_counter()

    summaries = summarize(
        ROOT / "results/temporal",
        ROOT / "results/sensitivity",
    )

    plot_sensitivity(
        summaries,
        ROOT / "results/figures",
    )

    print(
        f"[TERMINÉ] Durée : "
        f"{time.perf_counter() - start:.2f} s",
        flush=True,
    )


if __name__ == "__main__":
    main()
