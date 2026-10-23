"""Build the static comparison figure and compact tables from completed results."""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def build(root):
    rows = json.loads((root / "data/summary.json").read_text())["rows"]
    with (root / "data/summary.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys(), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
        }
    )
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    profiles = ("light-small", "heavy-large")
    policies = (("peter", "Peter", "#187a9d"), ("bhuman", "B-Human", "#db7829"))
    metrics = (
        ("successful_trial", "First strike within 15° and upright", "Trials (%)", True),
        (
            "foot_launch_2mps",
            "Foot-linked ball speed ≥ 2 m/s at any time",
            "Trials (%)",
            True,
        ),
        (
            "median_strongest_foot_linked_speed_m_s",
            "Strongest foot-linked ball speed",
            "Median speed (m/s)",
            False,
        ),
        (
            "median_strongest_absolute_heading_error_deg",
            "Direction of strongest foot-linked event",
            "Median absolute error (degrees)",
            False,
        ),
    )
    for ax, (key, title, label, percentage) in zip(axes.flat, metrics, strict=True):
        for index, (policy, name, colour) in enumerate(policies):
            selected = [
                next(
                    r for r in rows if r["policy"] == policy and r["ball_profile"] == p
                )
                for p in profiles
            ]
            values = [
                r[key] * 100 / r["planned"] if percentage else r[key] for r in selected
            ]
            bars = ax.bar(
                np.arange(2) + (index - 0.5) * 0.34,
                values,
                width=0.34,
                color=colour,
                label=name,
            )
            ax.bar_label(
                bars,
                labels=[f"{v:.0f}%" if percentage else f"{v:.2f}" for v in values],
                padding=4,
                fontsize=10,
            )
        ax.set_title(title, loc="left", fontsize=12, pad=14)
        ax.set_xticks([0, 1], ["0.10 kg · radius 8 cm", "0.29 kg · radius 9.5 cm"])
        ax.set_ylabel(label)
        ax.set_axisbelow(True)
        ax.grid(axis="y", alpha=0.18)
        ax.set_ylim(0, 115 if percentage else ax.get_ylim()[1] * 1.18)
    axes[0, 0].legend(frameon=False, ncol=2, loc="upper left")
    fig.suptitle(
        "K1 kick comparison · 432 MuJoCo trials",
        fontsize=19,
        x=0.075,
        ha="left",
        y=0.98,
    )
    fig.text(
        0.075,
        0.935,
        "108 trials per policy and ball profile · 36 tasks × 3 paired starting conditions · 12 seconds per trial",
        fontsize=11,
    )
    fig.text(
        0.075,
        0.025,
        "Ideal ball observations; policy-native poses and joint controllers. First-strike and whole-episode measures differ.\nSpeed and direction medians include trials with a qualifying foot-linked event; misses remain in trial-rate denominators.",
        fontsize=10,
        color="#444444",
    )
    fig.subplots_adjust(
        left=0.075, right=0.97, bottom=0.14, top=0.865, hspace=0.48, wspace=0.25
    )
    fig.savefig(root / "comparison.png", dpi=180, facecolor="white")
    fig.savefig(root / "comparison.svg", facecolor="white")
    svg = root / "comparison.svg"
    svg.write_text(
        "\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n"
    )
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    build(parser.parse_args().report.resolve())
