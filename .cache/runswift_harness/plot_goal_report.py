"""Static per-approach results for the shared 90-case goal grid."""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch


def build(root):
    rows = json.loads((root / "data/summary.json").read_text())["rows"]
    flat = [{k: v for k, v in row.items() if k != "outcomes"} for row in rows]
    with (root / "data/summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=flat[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(flat)
    plt.rcParams.update({"font.size": 10, "svg.fonttype": "none"})
    fig, axes = plt.subplots(2, 2, figsize=(13, 11))
    starts = ("west-away", "east-away", "north-away", "south-away", "central-oblique")
    positions = [f"x{x}-y{y}" for x in (1, 2, 3) for y in (1, 2, 3)]
    colours = ("#188c78", "#71b8a6", "#c94747", "#e4a044", "#bec7d1")
    labels = (
        "Goal before fall",
        "Goal after fall",
        "Fell during attempt; no goal",
        "Out / own goal",
        "No goal by budget",
    )
    for ax, row in zip(
        axes.flat,
        sorted(
            rows,
            key=lambda r: (r["ball_profile"] == "heavy-large", r["policy"] == "bhuman"),
        ),
        strict=True,
    ):
        trials = json.loads(
            (
                root / "data" / row["policy"] / row["ball_profile"] / "results.json"
            ).read_text()
        )["trials"]
        cells = np.full((9, 10), 4)
        for trial in trials:
            case = trial["case"]
            y = positions.index(case["ball_id"])
            x = starts.index(case["start_id"]) * 2 + (case["direction"] == -1)
            if trial.get("scored_before_fall"):
                value = 0
            elif trial.get("evaluation", {}).get("goal") is True:
                value = 1
            elif trial.get("fell_during_attempt"):
                value = 2
            elif trial.get("evaluation", {}).get("outcome") in ("out", "own_goal"):
                value = 3
            else:
                value = 4
            cells[y, x] = value
        ax.imshow(
            cells,
            cmap=ListedColormap(colours),
            vmin=0,
            vmax=4,
            aspect="auto",
            interpolation="nearest",
        )
        name = (
            "Peter kick loop" if row["policy"] == "peter" else "B-Human motion adapter"
        )
        ball = (
            "0.10 kg / 8 cm radius"
            if row["ball_profile"] == "light-small"
            else "0.29 kg / 9.5 cm radius"
        )
        ax.set_title(
            f"{name} · {ball}\n{row['goals']}/90 goals · {row['falls_during_attempt']}/90 active falls",
            loc="left",
            pad=12,
        )
        ax.set_xticks(
            np.arange(10),
            [
                f"{start.split('-')[0]} {'+' if direction == 0 else '−'}"
                for start in starts
                for direction in (0, 1)
            ],
            rotation=45,
            ha="right",
        )
        ax.set_yticks(np.arange(9), positions)
        ax.set_xticks(np.arange(-0.5, 10, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 9, 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=2)
        ax.tick_params(which="minor", bottom=False, left=False)
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle(
        "K1 goal scoring · the same 90 approaches",
        x=0.07,
        ha="left",
        fontsize=20,
        y=0.98,
    )
    fig.text(
        0.07,
        0.942,
        "Nine ball positions × five starts × both goals · two ball profiles · 360 trials",
        fontsize=12,
    )
    fig.legend(
        [Patch(facecolor=c) for c in colours],
        labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.055),
        ncol=3,
        frameon=False,
    )
    fig.text(
        0.07,
        0.015,
        "+ / − selects the goal at X = +7 / −7 m. Falls during passive observation are excluded from active falls.\nShared flat-floor simulation and ideal ball observations; virtual goal boundaries. B-Human uses a port of its motion logic with benchmark navigation.",
        fontsize=9,
        color="#444444",
    )
    fig.subplots_adjust(
        left=0.07, right=0.98, bottom=0.18, top=0.86, hspace=0.62, wspace=0.22
    )
    fig.savefig(root / "goal-grid.png", dpi=180, facecolor="white")
    svg = root / "goal-grid.svg"
    fig.savefig(svg, facecolor="white")
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n"
    )
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    build(parser.parse_args().report.resolve())
