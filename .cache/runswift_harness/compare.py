"""Run Peter's blend or B-Human's K1 kick in a shared, CPU MuJoCo fixture."""

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import mujoco
import numpy as np
import onnxruntime as ort
from contracts import (
    ARM_POSE,
    BALLS,
    DEFAULT_ASSETS,
    LEG_DEFAULT,
    LEG_EFFORT,
    LEG_KD,
    LEG_KP,
    MODELS,
    REPOSITORIES,
    Case,
    bhuman_observation,
    cases,
    perturbation,
    protocol,
)
from metrics import StrikeMeasurement


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")


def session(path):
    options = ort.SessionOptions()
    options.intra_op_num_threads = options.inter_op_num_threads = 1
    options.add_session_config_entry("session.intra_op.allow_spinning", "0")
    return ort.InferenceSession(str(path), options, providers=["CPUExecutionProvider"])


def yaw_of(data):
    w, x, y, z = data.qpos[3:7]
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def body_xy(world, origin, yaw):
    x, y = np.asarray(world)[:2] - np.asarray(origin)[:2]
    return np.array(
        [math.cos(yaw) * x + math.sin(yaw) * y, -math.sin(yaw) * x + math.cos(yaw) * y]
    )


def upstream(root):
    path = root / "peter-runner/python-implementation"
    if not path.is_dir():
        raise ValueError(
            f"Missing pinned assets. Run prepare-assets.sh --assets {root}"
        )
    sys.path.insert(0, str(path))
    from policy_runner.policy.kick_loop_policy import KickLoopPolicy
    from policy_runner.policy.walk_policy_amp_v1 import Q_ABS_LIMITS
    from policy_runner.sim import mujoco_bridge
    from policy_runner.types import Action, JointCommand

    return mujoco_bridge, KickLoopPolicy, Q_ABS_LIMITS, Action, JointCommand


class Controller:
    def __init__(self, name, root):
        self.name = name
        bridge, kick, self.limits, self.Action, self.JointCommand = upstream(root)
        relative, expected = MODELS[name]
        path = root / relative
        import os as _os
        if name == "peter" and _os.environ.get("KC_ONNX"):
            path, expected = Path(_os.environ["KC_ONNX"]), digest(Path(_os.environ["KC_ONNX"]))
        if digest(path) != expected:
            raise ValueError(f"Pinned {name} model hash differs")
        if name == "peter":
            import os as _os
            _caps = _os.environ.get("KC_CAPS")
            self.actor = kick(model_path=path, head_mode="track", **({"speed_limits": [float(x) for x in _caps.split(",")]} if _caps else {}))
            self.actor._session = session(path)
            self.default_q = self.actor.default_joint_pos
            self.kp, self.kd = self.actor.kp.copy(), self.actor.kd.copy()
            self.height = 0.5125
            self.effort = bridge.EFFORT_LIMIT.copy()
            import os as _os
            if _os.environ.get("KC_EFFORT"):
                self.effort[10:] = [float(x) for x in _os.environ["KC_EFFORT"].split(",")] * 2
        else:
            self.actor = session(path)
            if self.actor.get_inputs()[0].shape[-1] != 59:
                raise ValueError("B-Human input dimension is not 59")
            self.default_q = np.r_[np.zeros(2), ARM_POSE, LEG_DEFAULT]
            self.kp, self.kd = bridge.HOLD_KP.copy(), bridge.HOLD_KD.copy()
            self.kp[10:], self.kd[10:] = LEG_KP, LEG_KD
            self.height = 0.60
            self.effort = np.r_[bridge.EFFORT_LIMIT[:10], LEG_EFFORT]
        self.reset(Case("initial", 0.75, 0), 0)

    def reset(self, case, initial_yaw):
        self.case = case
        self.phase, self.previous = 0.0, np.zeros(13)
        self.previous_ball = None
        self.head = np.array([0, 0.4], dtype=float)
        if self.name == "peter":
            self.actor.reset()
            # Upstream reset keeps ball memory; independent trials must clear it.
            self.actor._mem_ball = None
            self.actor._mem_seen_time = -1.0
            self.actor._warned_no_ball = False
            self.actor._kick_heading = math.radians(case.heading_deg) - initial_yaw
            index = 0 if case.range_m < 4 else 1 if case.range_m < 8 else 2
            self.actor._range_one_hot = np.eye(3)[index]

    def action(self, bridge):
        state = bridge.latest_state()
        yaw = yaw_of(bridge.data)
        ball = body_xy(bridge.ball_world(), bridge.data.qpos[:3], yaw)
        if self.name == "peter":
            import os as _os
            if _os.environ.get("KC_BALL_FEET"):
                # Diagnostic (2026-10-09): training observes the ball from the
                # point between the soles, like B-Human here, not the pelvis.
                soles = [
                    bridge.data.xpos[bridge.model.body(n).id]
                    + bridge.data.xmat[bridge.model.body(n).id].reshape(3, 3) @ np.array([0, 0, -0.038])
                    for n in ("left_foot_link", "right_foot_link")
                ]
                ball = body_xy(bridge.ball_world(), np.mean(soles, axis=0), yaw)
            if not _os.environ.get("KC_VISION"):
                state.has_ball, state.ball_seen_time = True, state.time_s
                state.ball_rel_pos = [*ball, 0.0]
            observation = self.actor.build_observation(state, (0, 0, 0))
            action = self.actor.infer(observation)
            return action, np.array(observation.data), np.array(self.actor._last_action)
        origins = []
        for name in ("left_foot_link", "right_foot_link"):
            foot = bridge.model.body(name).id
            origins.append(
                bridge.data.xpos[foot]
                + bridge.data.xmat[foot].reshape(3, 3) @ np.array([0, 0, -0.038])
            )
        between_soles = np.mean(origins, axis=0)
        ball = body_xy(bridge.ball_world(), between_soles, yaw)
        velocity = body_xy(bridge.data.qvel[28:30], (0, 0), yaw)
        if self.previous_ball is None:
            self.previous_ball = ball.copy()
        observation = bhuman_observation(
            state.projected_gravity,
            state.imu.gyro,
            ball,
            velocity,
            math.radians(self.case.heading_deg) - yaw,
            self.phase,
            state.q[10:],
            state.dq[10:],
            self.previous,
            self.previous_ball,
            self.case.range_m,
        )
        raw = self.actor.run(
            None, {self.actor.get_inputs()[0].name: observation[None]}
        )[0].reshape(-1)
        if raw.shape != (13,) or not np.isfinite(raw).all():
            raise ValueError("Invalid B-Human output")
        target = self.default_q.copy()
        target[10:] = np.clip(
            LEG_DEFAULT + np.clip(raw[:12], -2, 2),
            self.limits[10:, 0],
            self.limits[10:, 1],
        )
        from policy_runner.policy.kick_loop_policy import head_track_angles

        goal = head_track_angles(
            [*body_xy(bridge.ball_world(), bridge.data.qpos[:3], yaw), 0]
        )
        self.head += np.clip(0.3 * (goal - self.head), -0.06, 0.06)
        target[:2] = self.head
        # Published competition code clips the frequency action to +/-0.5,
        # including its history slot, and advances the next phase with it.
        self.previous[:12] = target[10:] - LEG_DEFAULT
        self.previous[12] = np.clip(raw[12], -0.5, 0.5)
        self.phase = (self.phase + 0.02 * (1.5 + self.previous[12])) % 1
        self.previous_ball = ball.copy()
        action = self.Action(
            joint_cmds=[
                self.JointCommand(
                    index=i,
                    q=float(target[i]),
                    kp=float(self.kp[i]),
                    kd=float(self.kd[i]),
                )
                for i in range(22)
            ]
        )
        return action, observation, raw


def contacts(bridge, ball_geom, foot_bodies):
    any_robot = foot = False
    force = np.zeros(6)
    for contact_id in range(bridge.data.ncon):
        c = bridge.data.contact[contact_id]
        if ball_geom not in (c.geom1, c.geom2):
            continue
        other = c.geom2 if c.geom1 == ball_geom else c.geom1
        body = int(bridge.model.geom_bodyid[other])
        if body == 0 or body == bridge.model.geom_bodyid[ball_geom]:
            continue
        mujoco.mj_contactForce(bridge.model, bridge.data, contact_id, force)
        if force[0] >= 0.2:
            any_robot = True
            foot |= body in foot_bodies
    return any_robot, foot


def physics_step(bridge, effort):
    q, dq = bridge.data.qpos[7:29], bridge.data.qvel[6:28]
    torque = np.clip(
        bridge._kp * (bridge._q_target - q) - bridge._kd * dq, -effort, effort
    )
    bridge._last_tau[:] = torque
    bridge.data.qfrc_applied[:] = 0
    bridge.data.qfrc_applied[6:28] = torque
    mujoco.mj_step(bridge.model, bridge.data)


def run_trial(
    controller, bridge, case, repeat, radius, duration, destination, viewer=None
):
    yaw, noise = perturbation(repeat)
    bridge.reset(
        init_pos=(0, 0, controller.height),
        init_quat_wxyz=(math.cos(yaw / 2), 0, 0, math.sin(yaw / 2)),
    )
    bridge.data.qpos[7:29] = np.clip(
        controller.default_q + noise, controller.limits[:, 0], controller.limits[:, 1]
    )
    bridge._kp[:], bridge._kd[:] = controller.kp, controller.kd
    mujoco.mj_forward(bridge.model, bridge.data)
    for _ in range(200):
        physics_step(bridge, controller.effort)
    bridge.data.qpos[29:36] = [case.ball_x, case.ball_y, radius, 1, 0, 0, 0]
    bridge.data.qvel[28:34] = [case.ball_vx, case.ball_vy, 0, 0, 0, 0]
    mujoco.mj_forward(bridge.model, bridge.data)
    controller.reset(case, yaw_of(bridge.data))
    start = float(bridge.data.time)
    initial = {
        "root_xyz": bridge.data.qpos[:3].tolist(),
        "yaw_rad": yaw_of(bridge.data),
        "joint_q": bridge.data.qpos[7:29].tolist(),
        "repeat": repeat,
        "nominal_yaw_perturbation_rad": yaw,
        "joint_perturbation_rad": noise.tolist(),
    }
    ball_geom = bridge.model.geom("ball").id
    foot_bodies = {
        bridge.model.body(n).id for n in ("left_foot_link", "right_foot_link")
    }
    trunk = bridge.model.body("Trunk").id
    measurement = StrikeMeasurement(math.radians(case.heading_deg))
    times, positions, velocities, contact_flags = [], [], [], []
    observation_history, action_history, targets = [], [], []
    survived, reason = True, "completed"
    for _ in range(round(duration / 0.02)):
        wall = time.monotonic()
        action, obs, raw = controller.action(bridge)
        if not np.isfinite(raw).all():
            raise ValueError("Non-finite policy output")
        bridge.publish_action(action)
        observation_history.append(obs.astype(np.float32))
        action_history.append(raw.astype(np.float32))
        targets.append(bridge.q_target.astype(np.float32))
        for _ in range(10):
            physics_step(bridge, controller.effort)
            if not np.isfinite(bridge.data.qpos).all():
                raise ValueError("Non-finite physics state")
            t = float(bridge.data.time) - start
            contact, foot = contacts(bridge, ball_geom, foot_bodies)
            measurement.update(
                t, bridge.ball_world(), bridge.data.qvel[28:30], contact, foot
            )
            times.append(t)
            positions.append(bridge.data.qpos.astype(np.float32).copy())
            velocities.append(bridge.data.qvel.astype(np.float32).copy())
            contact_flags.append((contact, foot))
            if (
                bridge.data.qpos[2] < 0.25
                or bridge.data.xmat[trunk].reshape(3, 3)[2, 2] < 0.5
            ):
                survived, reason = False, "fall"
                break
        if viewer is not None:
            if not viewer.is_running():
                reason = "viewer_closed"
                break
            viewer.sync()
            time.sleep(max(0, 0.02 - (time.monotonic() - wall)))
        if not survived:
            break
    trace = destination / f"{case.name}-r{repeat + 1}.npz"
    np.savez_compressed(
        trace,
        time_s=np.asarray(times),
        qpos=np.asarray(positions),
        qvel=np.asarray(velocities),
        contact_flags=np.asarray(contact_flags),
        observation=np.asarray(observation_history),
        action=np.asarray(action_history),
        joint_target=np.asarray(targets),
    )
    return {
        "case": asdict(case),
        "repeat": repeat + 1,
        "initial_state": initial,
        "survived": survived,
        "reason": reason,
        "execution_error": None,
        "elapsed_sim_s": float(bridge.data.time) - start,
        "trace": str(trace),
        "trace_sha256": digest(trace),
        **measurement.result(survived),
    }


def worker(
    name, profile, root, output, selected_cases, repeats, duration, viewer=False
):
    root, output = Path(root), Path(output)
    destination = output / name / profile
    destination.mkdir(parents=True)
    controller = Controller(name, root)
    module = upstream(root)[0]
    ball = BALLS[profile]
    module.BALL_RADIUS, module.BALL_MASS = ball["radius_m"], ball["mass_kg"]
    bridge = module.MujocoBridge(
        mjcf_path=str(root / "peter-runner/assets/k1_22dof_scene.xml"),
        default_q=controller.default_q,
        init_pos=(0, 0, controller.height),
        ball_xy=(0.75, 0),
        control_dt=0.02,
        physics_dt=0.002,
    )
    import os as _os
    if _os.environ.get("KC_MODEL"):
        import mujoco as _mj
        bridge.model = _mj.MjModel.from_binary_path(_os.environ["KC_MODEL"])
        bridge.model.opt.timestep = 0.002
        bridge.data = _mj.MjData(bridge.model)
        bridge._trunk_body_id = _mj.mj_name2id(bridge.model, _mj.mjtObj.mjOBJ_BODY, "Trunk")
        bridge._head_body_id = _mj.mj_name2id(bridge.model, _mj.mjtObj.mjOBJ_BODY, "Head_2")
        bridge.reset(init_pos=(0, 0, controller.height))
    write(
        destination / "controller.json",
        {
            "default_q": controller.default_q.tolist(),
            "kp": controller.kp.tolist(),
            "kd": controller.kd.tolist(),
            "effort_limit_nm": controller.effort.tolist(),
            "initial_height_m": controller.height,
            "ball": ball,
            "model_sha256": MODELS[name][1],
            "model_dimensions": ([83, 22] if name == "peter" else [59, 13]),
        },
    )
    rows = []
    view = None
    if viewer:
        import mujoco.viewer

        view = mujoco.viewer.launch_passive(bridge.model, bridge.data)
    try:
        for case_dict in selected_cases:
            case = Case(**case_dict)
            for repeat in range(repeats):
                try:
                    row = run_trial(
                        controller,
                        bridge,
                        case,
                        repeat,
                        ball["radius_m"],
                        duration,
                        destination,
                        view,
                    )
                except Exception as error:  # noqa: BLE001 -- retain failed trials in the denominator
                    row = {
                        "case": asdict(case),
                        "repeat": repeat + 1,
                        "survived": False,
                        "reason": "execution_error",
                        "execution_error": f"{type(error).__name__}: {error}",
                    }
                rows.append(row)
                write(
                    destination / "results.json",
                    {"planned": len(selected_cases) * repeats, "trials": rows},
                )
                if len(rows) % 12 == 0:
                    print(
                        f"{name}/{profile}: {len(rows)}/{len(selected_cases) * repeats}",
                        flush=True,
                    )
    finally:
        if view is not None:
            view.close()
    return name, profile, rows


def summary(name, profile, rows):
    launches = [r for r in rows if r.get("foot_launch")]
    strongest = [r for r in rows if r.get("strongest_foot_linked_time_s") is not None]

    def median(key):
        values = [r[key] for r in launches if r.get(key) is not None]
        return float(np.median(values)) if values else None

    return {
        "policy": name,
        "ball_profile": profile,
        "planned": len(rows),
        "survived": sum(r["survived"] for r in rows),
        "execution_errors": sum(r["execution_error"] is not None for r in rows),
        "robot_contact": sum(r.get("first_contact_s") is not None for r in rows),
        "foot_launch": len(launches),
        "on_direction_launch": sum(r.get("on_direction_launch", False) for r in rows),
        "successful_trial": sum(r.get("successful_trial", False) for r in rows),
        "target_plane_hit": sum(r.get("target_plane_hit", False) for r in rows),
        "median_launch_speed_m_s": median("peak_launch_speed_m_s"),
        "median_launch_s": median("launch_s"),
        "median_absolute_heading_error_deg": (
            float(np.median([abs(r["launch_heading_error_deg"]) for r in launches]))
            if launches
            else None
        ),
        "median_first_strike_forward_m": median("first_strike_forward_m"),
        "recontact_after_launch": sum(
            r.get("first_strike_ended_by_recontact_s") is not None for r in rows
        ),
        "foot_launch_2mps": sum(
            r.get("first_2mps_foot_launch_s") is not None for r in rows
        ),
        "median_strongest_foot_linked_speed_m_s": (
            float(np.median([r["strongest_foot_linked_speed_m_s"] for r in strongest]))
            if strongest
            else None
        ),
        "median_strongest_absolute_heading_error_deg": (
            float(
                np.median(
                    [
                        abs(r["strongest_foot_linked_heading_error_deg"])
                        for r in strongest
                        if r.get("strongest_foot_linked_heading_error_deg") is not None
                    ]
                )
            )
            if strongest
            else None
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", choices=("peter", "bhuman", "both"), default="both")
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--suite", choices=("demo", "smoke", "full"), default="demo")
    parser.add_argument(
        "--ball-profile", choices=(*BALLS, "both"), default="light-small"
    )
    parser.add_argument("--repeats", type=int)
    parser.add_argument("--duration", type=float, default=12)
    parser.add_argument("--workers", type=int, default=2)
    parser.add_argument("--viewer", action="store_true")
    parser.add_argument("--ball-xy", type=float, nargs=2, default=(0.75, 0.0))
    parser.add_argument("--heading-deg", type=float, default=0)
    parser.add_argument("--range-m", type=float, default=3)
    args = parser.parse_args()
    root = args.assets.expanduser().resolve()
    now = datetime.now(ZoneInfo("Australia/Sydney"))
    output = (
        args.output
        or Path("benchmarks/results")
        / now.strftime("%Y-%m-%d")
        / "kick-policy-comparison/runs"
        / now.strftime("%H%M%S-%f")
    ).resolve()
    output.mkdir(parents=True, exist_ok=False)
    if args.duration <= 0 or args.workers < 1:
        parser.error("Duration and workers must be positive")
    repeats = (
        args.repeats if args.repeats is not None else (3 if args.suite == "full" else 1)
    )
    if repeats < 1:
        parser.error("Repeats must be positive")
    names = ("peter", "bhuman") if args.policy == "both" else (args.policy,)
    profiles = tuple(BALLS) if args.ball_profile == "both" else (args.ball_profile,)
    if args.viewer and (args.suite != "demo" or len(names) * len(profiles) != 1):
        parser.error("The viewer runs one policy and ball profile in the demo suite")
    selected = (
        [Case("demo", *args.ball_xy, args.heading_deg, args.range_m)]
        if args.suite == "demo"
        else cases(args.suite)
    )
    plan = protocol(args.suite, repeats, args.duration)
    plan.update(
        {
            "cases": [asdict(c) for c in selected],
            "policies": names,
            "selected_ball_profiles": profiles,
            "repositories": REPOSITORIES,
            "models": MODELS,
            "asset_root": str(root),
            "python": platform.python_version(),
            "mujoco": mujoco.__version__,
            "onnxruntime": ort.__version__,
            "numpy": np.__version__,
            "source_hashes": {
                p.name: digest(p) for p in Path(__file__).parent.glob("*.py")
            },
            "upstream_source_hashes": {
                str(p.relative_to(root)): digest(p)
                for p in (
                    root / "peter-runner/python-implementation/policy_runner"
                ).rglob("*.py")
            },
            "scene_asset_hashes": {
                str(p.relative_to(root)): digest(p)
                for p in (root / "peter-runner/assets").rglob("*")
                if p.is_file()
            },
            "scene_sha256": digest(root / "peter-runner/assets/k1_22dof_scene.xml"),
        }
    )
    write(output / "plan.json", plan)
    jobs = [
        (
            name,
            profile,
            root,
            output,
            plan["cases"],
            repeats,
            args.duration,
            args.viewer,
        )
        for name in names
        for profile in profiles
    ]
    collected = []
    if len(jobs) == 1 or args.viewer:
        collected = [worker(*job) for job in jobs]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(worker, *job) for job in jobs]
            collected = [f.result() for f in futures]
    rows = [summary(name, profile, trials) for name, profile, trials in collected]
    write(output / "summary.json", {"complete": True, "rows": rows})
    print(json.dumps(rows, indent=2), flush=True)
    print(f"Results: {output}", flush=True)
    return int(any(row["execution_errors"] for row in rows))


if __name__ == "__main__":
    raise SystemExit(main())
