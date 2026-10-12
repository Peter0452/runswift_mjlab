"""Render recorded MuJoCo states, with measured decisions/outcomes; never simulate motion."""

import argparse
import bisect
import hashlib
import json
import math
import os
import subprocess
import sys
from itertools import pairwise
from pathlib import Path

os.environ.setdefault("MUJOCO_GL", "egl")
from score_evaluator import GoalSpec, case_summary
from world_model.adapters.booster import K1_MODEL_PATH, K1_MODEL_REVISION


def load_model(source):
    """Verify scene assets and scoring geometry before replaying recorded qpos."""
    import mujoco

    sys.path.insert(0, str(source.resolve()))
    from core.model_colors import apply_color_markers
    from core.visual_scene import (
        build_visual_scene_snapshot,
        read_visual_scene_extensions,
    )

    path = source / K1_MODEL_PATH
    model = mujoco.MjModel.from_xml_path(str(path))
    apply_color_markers(model)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    scene = build_visual_scene_snapshot(
        model,
        data,
        model_source=K1_MODEL_PATH,
        visual_scene_extensions=read_visual_scene_extensions(str(path)),
    )
    if scene.manifest["revision"] != K1_MODEL_REVISION:
        raise ValueError("Render assets differ from the recorded physics scene")
    g = GoalSpec()
    if not math.isclose(float(model.geom("ball").size[0]), g.ball_radius):
        raise ValueError("Ball radius differs from evaluator geometry")
    for side, sign in [("right", 1), ("left", -1)]:
        post = model.geom(f"goal-{side}-front-right-post")
        crossbar = model.geom(f"goal-{side}-front-crossbar")
        if not (
            math.isclose(data.geom_xpos[post.id][0], sign * g.line_x)
            and math.isclose(
                abs(data.geom_xpos[post.id][1]) - post.size[0], g.half_width
            )
            and math.isclose(
                data.geom_xpos[crossbar.id][2] - crossbar.size[0], g.height
            )
        ):
            raise ValueError("Goal opening differs from evaluator geometry")
    return model


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def label(image, text, xy, *, scale=0.65, colour=(240, 240, 240), thickness=1):
    import cv2

    cv2.putText(
        image, text, xy, cv2.FONT_HERSHEY_SIMPLEX, scale, colour, thickness, cv2.LINE_AA
    )


def encoder_command(path, *, width, height, fps):
    """Use identical stream settings for recorded clips and explicit missing-video cards."""
    return [
        "ffmpeg",
        "-v",
        "error",
        "-nostdin",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{width}x{height}",
        "-r",
        str(fps),
        "-i",
        "pipe:0",
        "-an",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(path),
    ]


def render_trial(model, directory, output, *, fps=20, width=1280, height=720):
    """Resample recorded captures by simulation time; overlays use original wall receipts."""
    import cv2
    import mujoco
    import numpy as np

    summary = json.loads((directory / "summary.json").read_text())
    case = summary["case"]
    start, end = summary["start_wall_ns"], summary["end_wall_ns"]
    if start is None or end is None:
        raise ValueError("Trial has no released-robot interval to render")
    physics = [
        r
        for r in read_rows(directory / "physics.jsonl")
        if start <= r["wall_ns"] <= end
    ]
    decisions = read_rows(directory / "controller.jsonl")
    if len(physics) < 2 or not decisions:
        raise ValueError("Incomplete video source")
    times = [r["data"]["time"] for r in physics]
    if any(b <= a for a, b in pairwise(times)):
        raise ValueError("Render time did not progress")
    walls = [r["wall_ns"] for r in decisions]
    data = mujoco.MjData(model)
    camera = mujoco.MjvCamera()
    camera.type = mujoco.mjtCamera.mjCAMERA_FREE
    # One fixed physical view for both goals, including the whole pitch and starts.
    # Leave vertical space for overlays; no dependence on intended or future motion.
    camera.lookat[:] = [0, 0, 0]
    camera.distance = 22
    camera.azimuth = 90
    camera.elevation = -65
    count = math.ceil((times[-1] - times[0]) * fps) + 1
    output.mkdir(parents=True, exist_ok=True)
    path = output / (case["name"] + ".mp4")
    if path.exists():
        raise FileExistsError(path)
    command = encoder_command(path, width=width, height=height, fps=fps)
    video = subprocess.Popen(command, stdin=subprocess.PIPE)
    last_index = -1
    max_gap = 0
    preview_written = False
    model.vis.global_.offwidth = width
    model.vis.global_.offheight = height
    try:
        with mujoco.Renderer(model, height=height, width=width) as renderer:
            for i in range(count):
                t = min(times[-1], times[0] + i / fps)
                index = max(0, bisect.bisect_right(times, t) - 1)
                row = physics[index]
                state = row["data"]
                if index != last_index:
                    for name in ("qpos", "qvel", "ctrl"):
                        values = np.asarray(state[name], dtype=float)
                        target = getattr(data, name)
                        if (
                            values.shape != target.shape
                            or not np.isfinite(values).all()
                        ):
                            raise ValueError(
                                "Recorded physics shape is incompatible with scene"
                            )
                        target[:] = values
                    data.time = state["time"]
                    mujoco.mj_forward(model, data)
                    renderer.update_scene(data, camera=camera)
                    frame = renderer.render().copy()
                    last_index = index
                image = frame.copy()
                decision = decisions[
                    max(0, bisect.bisect_right(walls, row["wall_ns"]) - 1)
                ]
                result = decision["result"]
                receipt = decision.get("motion")
                motion = receipt.get("kick_status", "-") if receipt else "-"
                cv2.rectangle(image, (0, 0), (width, 90), (14, 20, 29), -1)
                cv2.rectangle(
                    image, (0, height - 100), (width, height), (14, 20, 29), -1
                )
                label(
                    image,
                    "K1  /  APPROACH - KICK - SCORE",
                    (28, 32),
                    scale=0.85,
                    thickness=2,
                )
                label(
                    image,
                    f"{case['name']}  |  goal {'+X' if case['direction'] > 0 else '-X'}  |  power {case['power']:.1f}  |  t = {t - times[0]:.2f}s",
                    (28, 64),
                )
                label(
                    image,
                    f"Behaviour: {result['state']}  /  {result['reason']}",
                    (28, height - 67),
                )
                aim = decision.get("aim_team_field")
                aim_text = (
                    "-"
                    if aim is None
                    else f"({case['direction'] * aim[0]:.2f}, {case['direction'] * aim[1]:.2f}) m"
                )
                label(
                    image,
                    f"SDK: {motion}   |   Physical aim: {aim_text}",
                    (28, height - 39),
                )
                label(
                    image,
                    "Ground-truth input; recorded physics replay; normal simulation speed",
                    (28, height - 13),
                    scale=0.5,
                    colour=(169, 187, 206),
                )
                evaluation = summary["evaluation"]
                crossing = evaluation.get("first_boundary_crossing")
                message = None
                if crossing and t >= crossing["time"]:
                    message = evaluation["outcome"].upper()
                if i >= count - 2 * fps:
                    message = (
                        "SCORED"
                        if summary["benchmark_success"]
                        else evaluation["outcome"].upper()
                    ) + (" / COMPLETE" if summary["valid_trial"] else " / INCOMPLETE")
                if message:
                    cv2.rectangle(
                        image, (width - 480, 105), (width - 22, 157), (14, 20, 29), -1
                    )
                    label(
                        image,
                        message,
                        (width - 462, 139),
                        scale=0.75,
                        colour=(101, 225, 154)
                        if summary["benchmark_success"]
                        else (255, 193, 105),
                        thickness=2,
                    )
                gap = t - state["time"]
                max_gap = max(max_gap, gap)
                if gap > 0.15:
                    label(
                        image,
                        "RECORDING GAP - HOLDING LAST CAPTURE",
                        (28, 124),
                        colour=(255, 120, 110),
                    )
                if not preview_written and (
                    result["state"] == "kick" or i == count // 2
                ):
                    cv2.imwrite(
                        str(output / (case["name"] + ".png")),
                        cv2.cvtColor(image, cv2.COLOR_RGB2BGR),
                    )
                    preview_written = True
                video.stdin.write(image.tobytes())
    finally:
        video.stdin.close()
        code = video.wait(timeout=60)
    if code:
        raise RuntimeError(f"Video encoder failed: {code}")
    probe = json.loads(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "stream=width,height,nb_frames:format=duration",
                "-of",
                "json",
                str(path),
            ]
        )
    )
    if int(probe["streams"][0]["nb_frames"]) != count:
        raise ValueError("Encoded frame count differs from requested replay")
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "frames": count,
        "fps": fps,
        "duration_s": float(probe["format"]["duration"]),
        "max_frame_hold_s": max_gap,
        "renderer": "MuJoCo " + mujoco.__version__,
        "source_physics_sha256": hashlib.sha256(
            (directory / "physics.jsonl").read_bytes()
        ).hexdigest(),
    }


def render_unavailable(case, output, reason, *, fps=20, width=1280, height=720):
    """Represent missing evidence explicitly without inventing robot motion."""
    import cv2
    import numpy as np

    path = output / (case["name"] + "-unavailable.mp4")
    image = np.full((height, width, 3), (14, 20, 29), dtype=np.uint8)
    label(image, "K1 / BENCHMARK CASE - NO REPLAY AVAILABLE", (40, 190), scale=0.9)
    label(image, case["name"], (40, 260), scale=0.7)
    for index, offset in enumerate(range(0, min(len(reason), 300), 100)):
        label(image, reason[offset : offset + 100], (40, 330 + 34 * index), scale=0.6)
    label(image, "This card is not a simulation or a scored miss.", (40, 510))
    with subprocess.Popen(
        encoder_command(path, width=width, height=height, fps=fps),
        stdin=subprocess.PIPE,
    ) as video:
        try:
            for _ in range(3 * fps):
                video.stdin.write(image.tobytes())
        finally:
            video.stdin.close()
        if video.wait(timeout=60):
            raise RuntimeError("Could not encode missing-video card")
    cv2.imwrite(str(path.with_suffix(".png")), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
    return {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "frames": 3 * fps,
        "fps": fps,
        "duration_s": 3,
        "kind": "unavailable_card",
        "reason": reason,
    }


def render_cases(
    model,
    directory,
    output,
    *,
    render_clip=render_trial,
    render_card=render_unavailable,
):
    """Keep manifest order and continue after case-local recording failures."""
    manifest = json.loads((directory / "manifest.json").read_text())
    results = []
    for case in manifest["cases"]:
        try:
            summary = case_summary(directory, case)
            if summary["start_wall_ns"] is None or summary["end_wall_ns"] is None:
                raise ValueError(summary["execution_reason"])
            result = render_clip(model, directory / case["name"], output)
            result["kind"] = "recorded_physics"
        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
            RuntimeError,
        ) as exc:
            result = render_card(case, output, str(exc))
        result["case"] = case["name"]
        results.append(result)
        print(json.dumps(result), flush=True)
        (output / "videos.json").write_text(json.dumps(results, indent=2) + "\n")
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simulator-source", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    model = load_model(args.simulator_source)
    results = render_cases(model, args.run, args.output)
    listing = args.output / "concat.txt"
    listing.write_text("".join(f"file '{r['file']}'\n" for r in results))
    combined = args.output / "benchmark.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-nostdin",
            "-f",
            "concat",
            "-safe",
            "1",
            "-i",
            str(listing),
            "-c",
            "copy",
            "-movflags",
            "+faststart",
            str(combined),
        ],
        check=True,
        timeout=60,
    )
    (args.output / "combined.json").write_text(
        json.dumps(
            {
                "file": combined.name,
                "sha256": hashlib.sha256(combined.read_bytes()).hexdigest(),
                "cases": [r["file"] for r in results],
                "note": "All planned cases in manifest order; missing footage uses labelled three-second cards. Recorded clips use normal simulation time.",
            },
            indent=2,
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
