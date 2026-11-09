"""Figures scientifiques : graphes réels, Boids et inertie."""

from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/simulation/graph_comparison_h30_R100.json"
OUTPUT = ROOT / "results/figures"

MODELS = {
    "real": ("Réel", "o"),
    "boids": ("Boids", "s"),
    "inertia": ("Inertie", "^"),
}


def generate_figures(input_path=INPUT, output_dir=OUTPUT):
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    data = json.loads(
        input_path.read_text(encoding="utf-8")
    )

    rows = data["results"]
    output_dir.mkdir(parents=True, exist_ok=True)

    generated = []

    for graph_type in ("spatial", "visibility"):
        for metric, title, ylabel in (
            (
                "edge_jaccard_vs_real",
                "Recouvrement des relations avec le réseau réel",
                "Jaccard des arêtes / arcs",
            ),
            (
                "clustering",
                "Comparaison du clustering",
                "Coefficient de clustering",
            ),
        ):
            fig, ax = plt.subplots(figsize=(10, 6))

            selected_models = (
                ("boids", "inertia")
                if metric == "edge_jaccard_vs_real"
                else ("real", "boids", "inertia")
            )

            for model in selected_models:
                points = sorted(
                    (
                        r["horizon_frames"],
                        r[metric],
                    )
                    for r in rows
                    if r["graph_type"] == graph_type
                    and r["model"] == model
                    and r[metric] is not None
                )

                if not points:
                    raise ValueError(
                        f"Données absentes : {graph_type}, "
                        f"{metric}, {model}"
                    )

                x, y = zip(*points)
                label, marker = MODELS[model]

                ax.plot(
                    x, y,
                    marker=marker,
                    linewidth=2,
                    markersize=6,
                    label=label,
                )

            name = (
                "graphe spatial non orienté"
                if graph_type == "spatial"
                else "graphe de visibilité orienté"
            )

            ax.set_title(f"{title}\n{name}")
            ax.set_xlabel("Horizon de prédiction (frames)")
            ax.set_ylabel(ylabel)
            ax.set_ylim(0, 1.02)
            ax.grid(alpha=0.25)
            ax.legend()

            fig.text(
                0.5, 0.02,
                "184 poissons suivis | R = 100 | "
                "Angle mort arrière = 25° pour la visibilité",
                ha="center",
                fontsize=9,
            )

            fig.tight_layout(rect=(0, 0.05, 1, 1))

            prefix = output_dir / (
                f"boids_{graph_type}_{metric}"
            )

            for extension in ("png", "svg"):
                path = prefix.with_suffix(
                    "." + extension
                )
                fig.savefig(
                    path,
                    dpi=200 if extension == "png" else None,
                    bbox_inches="tight",
                )
                if extension == "svg":
                    svg = path.read_text(encoding="utf-8")
                    svg = "\n".join(
                        line.rstrip() for line in svg.splitlines()
                    ) + "\n"
                    path.write_text(svg, encoding="utf-8")
                generated.append(path)

            plt.close(fig)

            print(
                f"[OK] {graph_type} | {metric}",
                flush=True,
            )

    print(
        f"[TERMINÉ] {len(generated)} fichiers : "
        f"{output_dir}",
        flush=True,
    )

    return generated


if __name__ == "__main__":
    generate_figures()
