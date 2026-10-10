#!/usr/bin/env python3.10
"""Interactive top-down visualiser for clear_target_provider.

Controls:
  - Drag any marker (ball / GK / T* / O*) to move it — easiest way to reposition
  - Radio buttons: what a click on empty grass places (Ball / GK / Teammate / Opponent)
  - Left click on empty field: place entity for the selected mode
  - Right click: delete nearest teammate/opponent
  - Keys: d=delete nearest, c=clear agents, r=reset scene
  - Checkbox: own free kick
  - Slider: GK heading (visual only — clear math uses ball + T + O positions)
"""
from __future__ import annotations

import importlib.util
import os
import sys
import time
from dataclasses import dataclass, field
from math import cos, pi, sin
from pathlib import Path

_SCRIPT = Path(__file__).resolve()
if sys.platform == "darwin" and "MPLBACKEND" not in os.environ:
    import matplotlib

    if importlib.util.find_spec("PyQt6") or importlib.util.find_spec("PySide6"):
        matplotlib.use("QtAgg")
    elif importlib.util.find_spec("PyQt5") or importlib.util.find_spec("PySide2"):
        matplotlib.use("Qt5Agg")

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.patches import Circle, FancyArrow, Rectangle, Wedge
    from matplotlib.widgets import Button, CheckButtons, RadioButtons, Slider
except ImportError as exc:
    print(
        "visualisation_target_provider needs matplotlib and numpy.\n"
        "On this machine, try:\n"
        f"  .test-venv/bin/python {_SCRIPT.relative_to(Path.cwd()) if _SCRIPT.is_relative_to(Path.cwd()) else _SCRIPT}\n"
        "Or install for your Python:\n"
        "  python3 -m pip install matplotlib numpy",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from clear_target_provider import (  # noqa: E402
    FIELD_LENGTH_M,
    FIELD_WIDTH_M,
    GOAL_AREA_HALF_WIDTH,
    GOALIE_GOAL_X,
    PENALTY_FRONT_X,
    ClearTargetInput,
    ClearTargetState,
    calc_best_clear,
    unit_from_angle,
    wrap_angle,
)

PENALTY_HALF_WIDTH = 2.0  # matches dimension.yaml penaltyAreaWidth / 2
_DRAG_REDRAW_INTERVAL_S = 1.0 / 30.0


@dataclass
class Scene:
    ball: tuple[float, float] = (-3.5, 0.0)
    gk: tuple[float, float] = (-4.0, 0.0)
    gk_yaw: float = 0.0
    teammates: list[tuple[float, float]] = field(default_factory=list)
    opponents: list[tuple[float, float]] = field(default_factory=list)
    own_free_kick: bool = False
    mode: str = "Ball"


class ClearTargetVisualiser:
    def __init__(self) -> None:
        self.scene = Scene(
            teammates=[(-2.0, 1.5)],
            opponents=[(-1.0, -0.5)],
        )
        self.hysteresis = ClearTargetState()
        self._info_text = None
        self._drag_target: str | None = None
        self._drag_index: int | None = None
        self._last_drag_redraw_s = 0.0
        self._widget_axes: set = set()

        self.fig, self.ax = plt.subplots(figsize=(11, 8))
        self.ax.set_aspect("equal", adjustable="box")
        plt.subplots_adjust(left=0.08, bottom=0.28, right=0.95, top=0.95)
        self._setup_widgets()
        self.fig.canvas.mpl_connect("button_press_event", self._on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self._on_release)
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.redraw()

    def _setup_widgets(self) -> None:
        mode_ax = self.fig.add_axes([0.08, 0.16, 0.18, 0.10])
        self._widget_axes.add(mode_ax)
        self.mode_radio = RadioButtons(
            mode_ax,
            ("Ball", "GK", "Teammate", "Opponent"),
            active=0,
        )
        self.mode_radio.on_clicked(self._on_mode)

        yaw_ax = self.fig.add_axes([0.32, 0.18, 0.30, 0.03])
        self._widget_axes.add(yaw_ax)
        self.yaw_slider = Slider(
            yaw_ax,
            "GK yaw",
            -pi,
            pi,
            valinit=self.scene.gk_yaw,
        )
        self.yaw_slider.on_changed(self._on_yaw)

        fk_ax = self.fig.add_axes([0.32, 0.12, 0.12, 0.04])
        self._widget_axes.add(fk_ax)
        self.free_kick_check = CheckButtons(fk_ax, ["Own free kick"], [False])
        self.free_kick_check.on_clicked(self._on_free_kick)

        reset_ax = self.fig.add_axes([0.70, 0.14, 0.10, 0.05])
        self._widget_axes.add(reset_ax)
        self.reset_button = Button(reset_ax, "Reset")
        self.reset_button.on_clicked(self._on_reset)

        clear_ax = self.fig.add_axes([0.82, 0.14, 0.10, 0.05])
        self._widget_axes.add(clear_ax)
        self.clear_button = Button(clear_ax, "Clear agents")
        self.clear_button.on_clicked(self._on_clear_agents)

    def _is_plot_event(self, event) -> bool:
        return (
            event.inaxes is self.ax
            and event.xdata is not None
            and event.ydata is not None
        )

    def _activate_window(self) -> None:
        manager = getattr(self.fig.canvas, "manager", None)
        if manager is None:
            return
        window = getattr(manager, "window", None)
        if window is None:
            return
        if hasattr(window, "raise_"):
            window.raise_()
        if hasattr(window, "activateWindow"):
            window.activateWindow()

    def _request_redraw(self, *, force: bool = False) -> None:
        if not force and self._drag_target is not None:
            now = time.monotonic()
            if now - self._last_drag_redraw_s < _DRAG_REDRAW_INTERVAL_S:
                return
            self._last_drag_redraw_s = now
        self.redraw()

    def _on_mode(self, label: str) -> None:
        self.scene.mode = label
        self.redraw()

    def _on_yaw(self, val: float) -> None:
        self.scene.gk_yaw = float(val)
        self.redraw()

    def _on_free_kick(self, _label: str) -> None:
        self.scene.own_free_kick = bool(self.free_kick_check.get_status()[0])
        self.redraw()

    def _on_reset(self, _event) -> None:
        self.scene = Scene(
            teammates=[(-2.0, 1.5)],
            opponents=[(-1.0, -0.5)],
        )
        self.hysteresis = ClearTargetState()
        self.yaw_slider.set_val(self.scene.gk_yaw)
        self.redraw()

    def _on_clear_agents(self, _event) -> None:
        self.scene.teammates.clear()
        self.scene.opponents.clear()
        self.redraw()

    def _on_key(self, event) -> None:
        if event.key == "d":
            self._delete_nearest(event.xdata, event.ydata)
        elif event.key == "c":
            self.scene.teammates.clear()
            self.scene.opponents.clear()
        elif event.key == "r":
            self._on_reset(None)
            return
        self.redraw()

    @staticmethod
    def _pick_radius(kind: str) -> float:
        return 0.35 if kind in {"ball", "gk"} else 0.45

    def _pick_entity(self, x: float, y: float) -> tuple[str, int | None] | None:
        click = np.array([x, y])
        candidates: list[tuple[float, str, int | None]] = []

        candidates.append(
            (float(np.linalg.norm(click - np.array(self.scene.ball))), "ball", None)
        )
        candidates.append(
            (float(np.linalg.norm(click - np.array(self.scene.gk))), "gk", None)
        )
        for i, teammate in enumerate(self.scene.teammates):
            candidates.append(
                (float(np.linalg.norm(click - np.array(teammate))), "teammate", i)
            )
        for i, opponent in enumerate(self.scene.opponents):
            candidates.append(
                (float(np.linalg.norm(click - np.array(opponent))), "opponent", i)
            )

        best_dist, best_kind, best_index = min(candidates, key=lambda item: item[0])
        if best_dist <= self._pick_radius(best_kind):
            return best_kind, best_index
        return None

    def _set_entity_xy(self, kind: str, index: int | None, x: float, y: float) -> None:
        if kind == "ball":
            self.scene.ball = (x, y)
        elif kind == "gk":
            self.scene.gk = (x, y)
        elif kind == "teammate" and index is not None:
            self.scene.teammates[index] = (x, y)
        elif kind == "opponent" and index is not None:
            self.scene.opponents[index] = (x, y)

    def _on_press(self, event) -> None:
        if event.inaxes in self._widget_axes:
            return
        if not self._is_plot_event(event):
            return

        x, y = float(event.xdata), float(event.ydata)

        if event.button == 3:
            self._delete_nearest(x, y)
            self.redraw()
            return

        if event.button != 1:
            return

        picked = self._pick_entity(x, y)
        if picked is not None:
            self._drag_target, self._drag_index = picked
            self._set_entity_xy(self._drag_target, self._drag_index, x, y)
            return

        mode = self.scene.mode
        if mode == "Ball":
            self.scene.ball = (x, y)
        elif mode == "GK":
            self.scene.gk = (x, y)
        elif mode == "Teammate":
            self.scene.teammates.append((x, y))
        elif mode == "Opponent":
            self.scene.opponents.append((x, y))
        self.redraw()

    def _on_motion(self, event) -> None:
        if self._drag_target is None:
            return
        if not self._is_plot_event(event):
            return
        self._set_entity_xy(
            self._drag_target,
            self._drag_index,
            float(event.xdata),
            float(event.ydata),
        )
        self._request_redraw()

    def _on_release(self, _event) -> None:
        if self._drag_target is not None:
            self._drag_target = None
            self._drag_index = None
            self._request_redraw(force=True)
            return
        self._drag_target = None
        self._drag_index = None

    def _delete_nearest(self, x: float | None, y: float | None) -> None:
        if x is None or y is None:
            return
        click = np.array([x, y])

        def nearest_index(items: list[tuple[float, float]]) -> int | None:
            if not items:
                return None
            dists = [float(np.linalg.norm(click - np.array(p))) for p in items]
            idx = int(np.argmin(dists))
            return idx if dists[idx] < 0.6 else None

        idx = nearest_index(self.scene.teammates)
        if idx is not None:
            self.scene.teammates.pop(idx)
            return
        idx = nearest_index(self.scene.opponents)
        if idx is not None:
            self.scene.opponents.pop(idx)

    def _draw_field(self) -> None:
        half_l = FIELD_LENGTH_M / 2.0
        half_w = FIELD_WIDTH_M / 2.0
        self.ax.add_patch(
            Rectangle(
                (-half_l, -half_w),
                FIELD_LENGTH_M,
                FIELD_WIDTH_M,
                facecolor="#2d6a2d",
                edgecolor="white",
                linewidth=2,
                zorder=0,
            )
        )
        self.ax.add_patch(
            Rectangle(
                (GOALIE_GOAL_X, -PENALTY_HALF_WIDTH),
                PENALTY_FRONT_X - GOALIE_GOAL_X,
                2.0 * PENALTY_HALF_WIDTH,
                fill=False,
                edgecolor="white",
                linewidth=1.2,
                linestyle="--",
                zorder=1,
            )
        )
        self.ax.add_patch(
            Rectangle(
                (GOALIE_GOAL_X, -GOAL_AREA_HALF_WIDTH),
                PENALTY_FRONT_X - GOALIE_GOAL_X,
                2.0 * GOAL_AREA_HALF_WIDTH,
                fill=False,
                edgecolor="yellow",
                linewidth=1.0,
                linestyle=":",
                zorder=1,
            )
        )
        self.ax.plot([0, 0], [-half_w, half_w], color="white", alpha=0.5, linewidth=1, zorder=1)
        self.ax.plot(
            [GOALIE_GOAL_X, GOALIE_GOAL_X],
            [-GOAL_AREA_HALF_WIDTH, GOAL_AREA_HALF_WIDTH],
            color="yellow",
            linewidth=2,
            zorder=1,
        )
        self.ax.plot(
            [-half_l, half_l],
            [-half_w + 0.3, -half_w + 0.3],
            color="gray",
            linewidth=0.8,
            alpha=0.5,
            zorder=1,
        )
        self.ax.plot(
            [-half_l, half_l],
            [half_w - 0.3, half_w - 0.3],
            color="gray",
            linewidth=0.8,
            alpha=0.5,
            zorder=1,
        )
        self.ax.set_xlim(-half_l - 0.8, half_l + 0.8)
        self.ax.set_ylim(-half_w - 0.8, half_w + 0.8)
        self.ax.set_xlabel("x (m)")
        self.ax.set_ylabel("y (m)")
        self.ax.set_title(
            "Clear target — drag markers to move; radio picks what new clicks create"
        )

    @staticmethod
    def _draw_robot_arrow(
        ax,
        x: float,
        y: float,
        yaw: float,
        *,
        color: str,
        label: str,
    ) -> None:
        dx = cos(yaw) * 0.35
        dy = sin(yaw) * 0.35
        ax.add_patch(
            FancyArrow(
                x,
                y,
                dx,
                dy,
                width=0.15,
                head_width=0.25,
                head_length=0.18,
                color=color,
                zorder=6,
            )
        )
        ax.text(x, y + 0.28, label, color=color, ha="center", fontsize=9, zorder=7)

    def _draw_forbidden_arc(
        self,
        ball: np.ndarray,
        left_tan: float,
        right_tan: float,
    ) -> None:
        left_deg = np.degrees(wrap_angle(left_tan))
        right_deg = np.degrees(wrap_angle(right_tan))
        span = wrap_angle(right_tan - left_tan)
        if span <= 0:
            span += 2.0 * pi
        theta1 = left_deg
        theta2 = left_deg + np.degrees(span)
        self.ax.add_patch(
            Wedge(
                (ball[0], ball[1]),
                2.5,
                theta1,
                theta2,
                width=2.5,
                facecolor="#ff4444",
                edgecolor="#aa0000",
                alpha=0.18,
                zorder=2,
            )
        )

    def _draw_blocked_sectors(self, ball: np.ndarray, sectors) -> None:
        colors = {"teammate": "#4488ff", "opponent": "#ff6666"}
        for sector in sectors:
            left_deg = np.degrees(wrap_angle(sector.min_angle))
            span = wrap_angle(sector.max_angle - sector.min_angle)
            if span <= 0:
                span += 2.0 * pi
            self.ax.add_patch(
                Wedge(
                    (ball[0], ball[1]),
                    2.0,
                    left_deg,
                    left_deg + np.degrees(span),
                    width=2.0,
                    facecolor=colors.get(sector.kind, "#888888"),
                    edgecolor="none",
                    alpha=0.12,
                    zorder=2,
                )
            )

    def redraw(self) -> None:
        for artist in list(self.ax.patches + self.ax.texts + self.ax.lines):
            artist.remove()
        if self._info_text is not None:
            self._info_text.remove()
            self._info_text = None

        self._draw_field()

        ball = np.array(self.scene.ball, dtype=float)
        inp = ClearTargetInput(
            ball_xy=self.scene.ball,
            teammates=list(self.scene.teammates),
            opponents=list(self.scene.opponents),
            own_free_kick=self.scene.own_free_kick,
        )
        result, debug = calc_best_clear(inp, self.hysteresis, collect_debug=True)

        if debug is not None:
            self._draw_forbidden_arc(ball, debug.forbidden_left_rad, debug.forbidden_right_rad)
            self._draw_blocked_sectors(ball, debug.blocked_sectors)

            if debug.candidate_angles and debug.candidate_ratings:
                max_rating = max((r for r in debug.candidate_ratings if r >= 0), default=1.0)
                for angle, rating in zip(debug.candidate_angles, debug.candidate_ratings):
                    if rating < 0:
                        continue
                    alpha = 0.15 + 0.45 * (rating / max(max_rating, 1e-6))
                    end = ball + 1.8 * unit_from_angle(angle)
                    self.ax.plot(
                        [ball[0], end[0]],
                        [ball[1], end[1]],
                        color="#88ff88",
                        alpha=alpha,
                        linewidth=1.0,
                        zorder=3,
                    )

        self.ax.add_patch(
            Circle(
                (ball[0], ball[1]),
                0.12,
                facecolor="#ffaa00",
                edgecolor="black",
                zorder=5,
            )
        )
        self.ax.text(ball[0], ball[1] - 0.28, "ball", ha="center", color="#ffaa00", fontsize=8)

        self._draw_robot_arrow(
            self.ax,
            self.scene.gk[0],
            self.scene.gk[1],
            self.scene.gk_yaw,
            color="#00cfff",
            label="GK",
        )

        for i, (tx, ty) in enumerate(self.scene.teammates, start=1):
            self.ax.add_patch(
                Circle((tx, ty), 0.18, facecolor="#3366ff", edgecolor="white", alpha=0.85, zorder=5)
            )
            self.ax.text(tx, ty + 0.25, f"T{i}", ha="center", color="#99bbff", fontsize=8)

        for i, (ox, oy) in enumerate(self.scene.opponents, start=1):
            self.ax.add_patch(
                Circle((ox, oy), 0.18, facecolor="#ff3333", edgecolor="white", alpha=0.85, zorder=5)
            )
            self.ax.text(ox, oy + 0.25, f"O{i}", ha="center", color="#ff9999", fontsize=8)

        if result.valid:
            landing = np.array(result.landing_xy)
            self.ax.add_patch(
                FancyArrow(
                    ball[0],
                    ball[1],
                    landing[0] - ball[0],
                    landing[1] - ball[1],
                    width=0.08,
                    head_width=0.22,
                    head_length=0.2,
                    color="#cc66ff",
                    zorder=8,
                )
            )
            self.ax.add_patch(
                Circle(
                    (landing[0], landing[1]),
                    0.1,
                    facecolor="#cc66ff",
                    edgecolor="white",
                    zorder=8,
                )
            )
            self.ax.text(
                landing[0],
                landing[1] + 0.25,
                "landing",
                ha="center",
                color="#cc66ff",
                fontsize=8,
            )

            stance = ball - unit_from_angle(result.angle_rad) * 0.4
            self._draw_robot_arrow(
                self.ax,
                float(stance[0]),
                float(stance[1]),
                result.angle_rad,
                color="#aa88ff",
                label="stance",
            )

        info_lines = [
            f"place mode: {self.scene.mode} (only for clicks on empty grass)",
            "drag ball / GK / T* / O* to reposition",
            f"ball: ({self.scene.ball[0]:.2f}, {self.scene.ball[1]:.2f})",
            f"GK: ({self.scene.gk[0]:.2f}, {self.scene.gk[1]:.2f})  yaw={np.degrees(self.scene.gk_yaw):.0f}° (GK not used in clear math)",
            f"teammates: {len(self.scene.teammates)}  opponents: {len(self.scene.opponents)}",
            f"own free kick: {self.scene.own_free_kick}",
        ]
        if result.valid:
            kind = "EMERGENCY CLEAR" if result.emergency else "VALID"
            info_lines.extend([
                f"{kind}  angle={np.degrees(result.angle_rad):.1f}°  "
                f"range={result.kick_range_m:.1f}m  kick={result.kick_name}",
                f"rating={result.rating:.3f}  power={result.kick_power:.1f}",
                f"landing=({result.landing_xy[0]:.2f}, {result.landing_xy[1]:.2f})",
            ])
        else:
            info_lines.append("NO VALID CLEAR (numOfKickTypes equivalent)")

        self._info_text = self.fig.text(
            0.99,
            0.97,
            "\n".join(info_lines),
            transform=self.fig.transFigure,
            va="top",
            ha="right",
            fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85),
        )

        self.fig.canvas.draw_idle()


def main() -> None:
    visualiser = ClearTargetVisualiser()
    visualiser._activate_window()
    plt.show()


if __name__ == "__main__":
    main()
