"""Match tactics over one frozen world view; no ROS, SDK or model owner."""

from dataclasses import dataclass, replace
from math import atan2, cos, hypot, isfinite, sin
from uuid import uuid4

from action.types import MotionCommand
from match_tactics import (
    DefaultFormation,
    LocalisationHint,
    RestartTracker,
    RoleCoordinator,
    TacticsPolicy,
    angle,
    blocking_target,
    clamp,
    fresh_peers,
    select_target,
    team_broadcast,
)
from skills.base import SkillProgress, SkillStatus
from skills.single_shot import SingleShot, SingleShotGoal
from skills.uncertainty import UnusableEstimate, ball_spread, check_quality
from skills.world import (
    KickPolicy,
    NavigateToPose,
    NavigateToPoseGoal,
    WorldSkill,
)

from world_model import TickContext
from world_model import types as wm


@dataclass(frozen=True)
class MatchGoal:
    """Tactical intention only; roles are assigned by behaviour/coordination."""

    role: str = "striker"
    kick_power: float = 1.0
    kick_duration_sec: float = 8.0
    play_style: str = "auto"  # auto, kick, dribble or walk_through
    target: wm.FramedPose2 | None = None  # Optional manual navigation intention.

    def __post_init__(self):
        if self.role not in {"striker", "assist", "goalkeeper", "auto"}:
            raise ValueError("Choose striker, assist, goalkeeper or auto")
        if self.play_style not in {"auto", "kick", "dribble", "walk_through"}:
            raise ValueError("Unknown play style")
        if any(
            not isfinite(v) or v <= 0 for v in (self.kick_power, self.kick_duration_sec)
        ):
            raise ValueError("Kick power and duration must be positive and finite")


@dataclass(frozen=True)
class MotionFeedback:
    """Motion-layer facts sampled in the decision clock, separate from world facts.

    Readiness means the motion layer has already prepared the required mode.
    Kick outcomes must name the runner's attempt; an old completion is ignored.
    """

    at: wm.TimePoint
    upright: bool
    walk_ready: bool
    kick_ready: bool
    kick_attempt_id: str | None = None
    kick_status: str = "idle"
    recovery_available: bool = False
    recovery_attempt_id: str | None = None
    recovery_status: str = "idle"

    def __post_init__(self):
        if any(
            type(v) is not bool
            for v in (self.upright, self.walk_ready, self.kick_ready)
        ):
            raise ValueError("Motion readiness must be explicit booleans")
        if type(self.recovery_available) is not bool:
            raise ValueError("Recovery capability must be explicit")
        if self.recovery_status not in {"idle", "running", "completed", "failed"}:
            raise ValueError("Unknown recovery status")
        if self.recovery_status != "idle" and not self.recovery_attempt_id:
            raise ValueError("Recovery feedback must identify an attempt")
        if self.kick_status not in {
            "idle",
            "running",
            "stopping",
            "stopped",
            "completed",
            "failed",
        }:
            raise ValueError("Unknown kick status")
        if self.kick_status != "idle" and not self.kick_attempt_id:
            raise ValueError("Kick feedback must identify an attempt")


@dataclass(frozen=True)
class MatchPolicy:
    """Evidence/precision limits; restart and team choices live in TacticsPolicy."""

    official_age_ns: int = 500_000_000
    motion_age_ns: int = 150_000_000
    approach_distance_m: float = 0.65
    retarget_distance_m: float = 0.15
    kick_distance_m: float = 0.85
    kick_bearing_rad: float = 0.35
    kick_heading_rad: float = 0.25
    rearm_distance_m: float = 0.4
    max_field_ball_std_m: float = 0.25
    max_speed_mps: float = 0.2
    max_turn_rps: float = 0.8

    def __post_init__(self):
        for name, value in vars(self).items():
            if isinstance(value, bool) or not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite")
        if any(type(v) is not int for v in (self.official_age_ns, self.motion_age_ns)):
            raise ValueError("Age limits must be integer nanoseconds")
        if self.approach_distance_m >= self.kick_distance_m:
            raise ValueError("Approach must finish inside the kick distance")

    def stop_reason(self, context, goal):
        """Grant this narrow open-play policy from checked official evidence only."""
        match = context.world.match
        report, meta = match.official, match.official_meta
        if report is None or meta is None or match.connection != "current":
            return "official_state_unavailable"
        if (
            meta.time_quality != "synchronised"
            or meta.event_at.clock_epoch != context.now.clock_epoch
            or not 0 <= context.now.ns - meta.event_at.ns < self.official_age_ns
            or match.effective.authority != "official"
            or any(
                h.component == meta.id.source and h.status != "ready"
                for h in context.world.health
            )
        ):
            return "official_state_stale_or_untrusted"
        identity = context.world.snapshot.identity
        players = [
            p
            for team in report.teams
            if team.team_number == identity.team_number
            for p in team.players
            if p.player_number == identity.player_number
        ]
        if len(players) != 1:
            return "our_penalty_unknown"
        if players[0].penalty != "none":
            return "penalised"
        if report.stopped:
            return "official_stop"
        if report.game_phase not in {"normal", "extra_time"}:
            return "unsupported_game_phase"
        if report.state not in {"ready", "set", "playing"}:
            return "match_" + report.state
        if match.restrictions.walk not in {"unknown", "allowed"}:
            return "world_restriction"
        return None


class MatchRunner(WorldSkill):
    """Select referee, team, goalkeeper and ball tactics from one immutable tick."""

    def __init__(
        self,
        *,
        policy=None,
        navigation=None,
        kick_policy=None,
        tactics=None,
        formation=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.policy = MatchPolicy() if policy is None else policy
        self.navigation = (
            NavigateToPose(limits=self.limits) if navigation is None else navigation
        )
        self.tactics = TacticsPolicy() if tactics is None else tactics
        self.formation = (
            DefaultFormation(self.tactics) if formation is None else formation
        )
        self.safety = NavigateToPose(
            limits=self.limits,
            policy=self.navigation.policy,
            navigation_policy=self.navigation.navigation_policy,
        )
        self.kick_policy = KickPolicy() if kick_policy is None else kick_policy
        self.kick = SingleShot(policy=self.kick_policy, limits=self.limits)
        self._attempt_sequence = 0
        self._attempt_session = uuid4().hex
        self.on_exit()

    def on_exit(self):
        super().on_exit()
        self.navigation.on_exit()
        self.kick.on_exit()
        self.safety.on_exit()
        self.state = "stand"
        self.attempt_id = None
        self._basis = self._approach_goal = self._anchor = self._attempted_ball = None
        self._search_since = None
        self.restart = RestartTracker()
        self.coordination = RoleCoordinator()
        self.role = None
        self.broadcast = None
        self.localisation_hint = None
        self._clearing = False
        self._needs_localisation = False
        self._locked_target = None
        self._recovery_id = self._recovery_since = None
        self._recovery_finished = False
        self._tactic_key = None

    def tick(
        self,
        context: TickContext,
        goal: MatchGoal,
        command: MotionCommand,
        *,
        motion: MotionFeedback | None = None,
    ):
        """Use the exact context for permissions and every skill; overwrite old intents."""
        # This is an input to this call, not retained skill progress. on_enter
        # may reset progress inside WorldSkill.tick without discarding this input.
        self._tick_feedback = motion
        self.localisation_hint = None
        command.set_head(0.45, 0.0)
        result = super().tick(context, goal, command)
        # Navigation limits each axis; the live K1 port limits total translation.
        # Scaling down keeps the command inside its already checked swept area.
        speed = hypot(command.x, command.y)
        if speed > self.policy.max_speed_mps:
            scale = self.policy.max_speed_mps / speed
            command.x *= scale
            command.y *= scale
        self.broadcast = None
        if result.status != SkillStatus.FAILED:
            frame = context.world.snapshot.field.frame
            pose = self._optional(lambda: self._pose(context, frame))
            ball = self._optional(lambda: self._field_ball(context))
            self.broadcast = team_broadcast(
                context,
                self.role,
                self.state
                in {"approach", "kick", "dribble", "dribble_clear", "walk_through"},
                pose,
                ball,
            )
        return result

    def _hold(self, command, reason):
        if self.state == "recovery" and self._recovery_id is not None:
            self._recovery_finished = True
        self.navigation.cancel(command)
        self.kick.cancel(command)
        self._approach_goal = self._anchor = self._locked_target = None
        self.state = "stand"
        command.set_head(0.45, 0.0)
        return SkillProgress(SkillStatus.RUNNING, reason=reason)

    def _check_basis(self, context):
        snapshot = context.world.snapshot
        basis = (
            snapshot.configuration_id,
            snapshot.identity,
            snapshot.field,
            context.world.self.localisation_epoch,
            tuple(
                (s.source, s.target, s.model_id, s.calibration_id)
                for s in snapshot.transforms
                if isinstance(s, wm.KinematicTransformSample)
                and s.source.name in {"robot_base", "odom"}
            ),
        )
        if self._basis is not None and self._basis != basis:
            raise UnusableEstimate("match_frame_or_localisation_changed")
        self._basis = basis

    def _search(self, context, command, reason):
        if self.state not in {"search", "pre_enter_field"}:
            self._search_since = context.now.ns
        self.navigation.cancel(command)
        self.kick.cancel(command)
        self._approach_goal = self._anchor = None
        self.state = "search"
        if reason != "awaiting_localisation":
            peers = fresh_peers(context, self.tactics, self._estimate)
            pose = self._optional(
                lambda: self._pose(context, context.world.snapshot.field.frame)
            )
            for peer in sorted(peers, key=lambda p: p.report.event_at.ns, reverse=True):
                report = self._optional(
                    lambda peer=peer: self._estimate(context, peer.ball)
                )
                if report is None or pose is None:
                    continue
                spread = self._optional(lambda report=report: ball_spread(report))
                if (
                    spread is None
                    or report.value.frame != context.world.snapshot.field.frame
                    or report.meta.quality not in {"nominal", "degraded"}
                    or spread.position_std_m > self.policy.max_field_ball_std_m
                ):
                    continue
                p, robot = report.value.position, pose.value.pose
                heading = atan2(p.y - robot.y, p.x - robot.x)
                target = wm.Pose2(p.x - cos(heading), p.y - sin(heading), heading)
                result = self._navigate(context, target, command, "search_team")
                command.set_head(
                    0.45, 0.8 * sin((context.now.ns - self._started_ns) / 1e9)
                )
                return result
        seconds = (context.now.ns - self._search_since) / 1e9
        command.set_head(0.45, 0.8 * sin(seconds))
        if (
            seconds * 1e9 >= self.tactics.search_turn_after_ns
            and reason != "awaiting_localisation"
        ):
            frame = context.world.snapshot.field.frame
            pose = self._optional(lambda: self._pose(context, frame))
            if pose is not None:
                # A checked on-the-spot turn broadens the scan after a head sweep.
                scene = self._scene(context, pose)
                sign = 1 if context.world.snapshot.identity.player_number % 2 else -1
                velocity, blocked = scene.limit_command(
                    pose.value.pose, (0, 0, sign * min(0.35, self.policy.max_turn_rps))
                )
                if velocity is not None:
                    command.set_body(*velocity)
                    command.avoidance_applied = True
                else:
                    reason += ":" + blocked
        return SkillProgress(SkillStatus.RUNNING, reason="search:" + reason)

    def _nav_goal(self, frame, pose, *, ball_distance=0.0):
        return NavigateToPoseGoal(
            wm.FramedPose2(frame, pose),
            ball_keep_out_m=ball_distance,
            distance_tolerance=0.1,
            theta_tolerance=0.15,
            max_vx=self.policy.max_speed_mps,
            max_vy=self.policy.max_speed_mps,
            max_vtheta=self.policy.max_turn_rps,
        )

    def _estimate(self, context, estimate):
        estimate = super()._estimate(context, estimate)
        sources = {item.source for item in estimate.meta.contributors}
        if any(
            h.component in sources and h.status != "ready" for h in context.world.health
        ):
            raise UnusableEstimate("match_source_unavailable")
        return estimate

    @staticmethod
    def _optional(read):
        try:
            return read()
        except UnusableEstimate:
            return None

    def _field_ball(self, context):
        ball = self._ball(context, context.world.snapshot.field.frame)
        check_quality(ball, self.kick_policy.allowed_qualities, "ball")
        if ball_spread(ball).position_std_m > self.policy.max_field_ball_std_m:
            raise UnusableEstimate("field_ball_position_uncertain")
        return ball

    def _track_head(self, context, command):
        local = self._optional(lambda: self._local_ball(context))
        if local is not None:
            try:
                self.kick_policy.assess_ball(local)
            except UnusableEstimate:
                return
            p = local.value.position
            command.set_head(
                clamp(
                    atan2(self.tactics.head_height_m, max(0.05, hypot(p.x, p.y))),
                    -0.3,
                    0.7,
                ),
                clamp(atan2(p.y, p.x), -0.8, 0.8),
            )

    def _navigate(self, context, target, command, state, *, ball_distance=0.0):
        self.kick.cancel(command)
        self.state = state
        result = self.navigation.tick(
            context,
            self._nav_goal(
                context.world.snapshot.field.frame, target, ball_distance=ball_distance
            ),
            command,
        )
        if result.status == SkillStatus.FAILED:
            raise UnusableEstimate(result.reason)
        self._track_head(context, command)
        return SkillProgress(
            SkillStatus.RUNNING,
            reason=state
            + (":arrived" if result.status == SkillStatus.SUCCEEDED else ""),
        )

    def _scene(self, context, pose):
        checked = self.safety.tick(
            context,
            self._nav_goal(context.world.snapshot.field.frame, pose.value.pose),
            MotionCommand(),
        )
        if checked.status == SkillStatus.FAILED:
            raise UnusableEstimate(checked.reason)
        return self.safety.evidence.scene

    def _recover(self, context, motion, command):
        self.navigation.cancel(command)
        self.kick.cancel(command)
        self.state = "recovery"
        if context.world.match.restrictions.recovery not in {"unknown", "allowed"}:
            return self._hold(command, "recovery_restricted")
        if not motion.recovery_available:
            return self._hold(command, "recovery_unavailable")
        if self._recovery_id is None:
            self._attempt_sequence += 1
            self._recovery_id = (
                f"{self._attempt_session}:recovery:{self._attempt_sequence}"
            )
            self._recovery_since = context.now.ns
        if (
            motion.recovery_attempt_id == self._recovery_id
            and motion.recovery_status in {"completed", "failed"}
        ):
            self._recovery_finished = True
            return self._hold(command, "recovery_reported_" + motion.recovery_status)
        if self._recovery_finished:
            return self._hold(command, "recovery_requires_restart")
        if context.now.ns - self._recovery_since >= self.tactics.recovery_timeout_ns:
            self._recovery_finished = True
            return self._hold(command, "recovery_timeout")
        command.recovery_attempt_id = self._recovery_id
        return SkillProgress(SkillStatus.RUNNING, reason="recovering")

    def _tick(self, context, goal, command):
        reason = self.policy.stop_reason(context, goal)
        if reason:
            if reason in {"match_initial", "penalised"}:
                self._needs_localisation = True
            self._clearing = False
            self.restart = RestartTracker()
            if self._recovery_id is not None:
                self._recovery_finished = True
            return self._hold(command, reason)
        self._check_basis(context)
        field = context.world.snapshot.field
        if field.own_goal.centre.x >= field.opponent_goal.centre.x:
            raise UnusableEstimate("match_requires_team_field_orientation")
        report = context.world.match.official
        ball = self._optional(lambda: self._field_ball(context))
        released = self.restart.update(
            context, ball, self.kick_policy.margin_sigma, self.tactics
        )
        if report.state == "set":
            result = self._hold(command, "match_set")
            self._track_head(context, command)
            return result
        motion = self._tick_feedback
        if motion is None:
            return self._hold(command, "motion_feedback_unavailable")
        if (
            motion.at.clock_epoch != context.now.clock_epoch
            or not 0 <= context.now.ns - motion.at.ns <= self.policy.motion_age_ns
        ):
            return self._hold(command, "motion_feedback_stale")
        if not motion.upright:
            return self._recover(context, motion, command)
        if self._recovery_id is not None:
            # Upright is measured, not inferred from elapsed time or an RPC ack.
            if not motion.walk_ready:
                return self._hold(command, "recovery_awaiting_walk_ready")
            self._recovery_id = self._recovery_since = None
            self._recovery_finished = False
            self._needs_localisation = True
        if self.state == "kick" and self.kick.phase in {"stopping", "complete"}:
            return self._shot_tick(context, goal, command, motion)
        if not motion.walk_ready:
            return self._hold(command, "motion_not_ready")
        pose = self._optional(lambda: self._pose(context, field.frame))
        if self._needs_localisation and pose is None:
            self.localisation_hint = LocalisationHint(
                context.now, context.world.snapshot.id
            )
            result = self._search(context, command, "awaiting_localisation")
            self.state = "pre_enter_field"
            return result
        self._needs_localisation = False
        peers = fresh_peers(context, self.tactics, self._estimate)
        self.role = goal.role
        if self.role == "auto":
            if (
                context.world.snapshot.identity.player_number
                == self.tactics.goalkeeper_number
            ):
                self.role = "goalkeeper"
            elif pose is not None and ball is not None:
                self.role = self.coordination.choose(
                    context, pose, ball, peers, self.tactics
                )
            else:
                self.role = "assist"  # Missing team evidence never claims a chase.
        if report.state == "ready":
            target = self.formation.target(context, self.role, None, ready=True)
            if target is None:
                return self._hold(command, "ready_target_unavailable")
            # READY targets stay on our half, outside the centre circle for opponents.
            if target.x >= -0.1:
                return self._hold(command, "ready_target_outside_own_half")
            if (
                report.kicking_team != context.world.snapshot.identity.team_number
                and hypot(target.x, target.y) <= field.centre_circle_radius + 0.4
            ):
                return self._hold(command, "ready_target_inside_centre_circle")
            return self._navigate(context, target, command, "ready")
        active_restart = (
            report.set_play != "none" or report.secondary_seconds > 0
        ) and not released
        ours = report.kicking_team == context.world.snapshot.identity.team_number
        known_restart = report.set_play in {
            "none",
            "goal_kick",
            "pushing_free_kick",
            "corner_kick",
            "kick_in",
            "throw_in",
            "penalty_kick",
            "direct_free_kick",
            "indirect_free_kick",
        }
        if report.secondary_seconds < 0:
            return self._hold(command, "restart_time_unknown")
        if not known_restart:
            return self._hold(command, "unknown_restart")
        if active_restart and not ours:
            # Kickoff/penalty: stand. Other restarts: position outside the exclusion disc.
            if report.set_play in {"none", "penalty_kick"} or ball is None:
                return self._hold(command, "opponent_restart_wait")
            if pose is None:
                return self._hold(command, "restart_localisation_unavailable")
            if (
                hypot(
                    pose.value.pose.x - ball.value.position.x,
                    pose.value.pose.y - ball.value.position.y,
                )
                <= self.tactics.restart_distance_m + 0.2
            ):
                return self._hold(command, "restart_exclusion_zone")
            return self._support(context, ball, command, defending=True)
        tactic_key = (
            self.role,
            report.state,
            report.set_play,
            report.kicking_team,
            active_restart,
        )
        if self._tactic_key is not None and self._tactic_key != tactic_key:
            self._hold(command, "tactic_changed")
        self._tactic_key = tactic_key
        if goal.target is not None:
            if active_restart:
                return self._hold(command, "manual_target_during_restart")
            if goal.target.frame != field.frame or goal.target.reference_at is not None:
                raise UnusableEstimate("manual_target_frame_mismatch")
            return self._navigate(context, goal.target.pose, command, "walk_to_point")
        if self.role == "assist":
            return self._support(context, ball, command)
        if self.role == "goalkeeper":
            if ball is None:
                self._clearing = False
                return self._support(context, None, command)
            p = ball.value.position
            error = self.kick_policy.margin_sigma * ball_spread(ball).position_std_m
            depth = p.x - field.own_goal.centre.x
            threshold = (
                self.tactics.clear_exit_m
                if self._clearing
                else self.tactics.clear_enter_m
            )
            self._clearing = (
                depth > error
                and depth + error < threshold
                and abs(p.y - field.own_goal.centre.y) + error < field.own_goal.width
            )
            if not self._clearing:
                return self._support(context, ball, command)
        self._track_head(context, command)
        return self._play_ball(
            context,
            goal,
            command,
            motion,
            restart=active_restart,
            clearing=self._clearing,
        )

    def _support(self, context, ball, command, *, defending=False):
        if self.role == "goalkeeper":
            target, reason = blocking_target(
                context, ball, self.tactics, self.kick_policy.margin_sigma
            )
            result = self._navigate(
                context,
                target,
                command,
                "blocking",
                ball_distance=self.tactics.restart_distance_m if defending else 0,
            )
            if ball is None:
                command.set_head(
                    0.45, 0.8 * sin((context.now.ns - self._started_ns) / 1e9)
                )
            return replace(result, reason=reason)
        if ball is None:
            return self._search(context, command, "support_ball_unavailable")
        target = self.formation.target(context, "assist", ball, ready=False)
        if target is None:
            return self._hold(command, "support_target_unavailable")
        return self._navigate(
            context,
            target,
            command,
            "assist",
            ball_distance=self.tactics.restart_distance_m if defending else 0,
        )

    def _dribble(self, context, goal, command, pose, ball, local, target, *, clearing):
        p, q = pose.value.pose, local.value.position
        heading = atan2(
            target.y - ball.value.position.y, target.x - ball.value.position.x
        )
        bearing = atan2(q.y, q.x)
        speed = self.policy.max_speed_mps * max(0, cos(bearing))
        if abs(bearing) > 0.35:
            speed = 0.0
        turn = clamp(
            0.7 * bearing + 0.3 * angle(heading - p.theta),
            -self.policy.max_turn_rps,
            self.policy.max_turn_rps,
        )
        scene = self._scene(context, pose)
        velocity, reason = scene.limit_command(p, (speed, 0.0, turn))
        self.navigation.cancel(command)
        self.kick.cancel(command)
        if velocity is None:
            raise UnusableEstimate(reason)
        command.set_body(*velocity)
        command.avoidance_applied = True
        self._track_head(context, command)
        self.state = (
            "dribble_clear"
            if clearing
            else ("walk_through" if goal.play_style == "walk_through" else "dribble")
        )
        return SkillProgress(SkillStatus.RUNNING, reason=reason or self.state)

    def _shot_tick(self, context, goal, command, motion):
        result = self.kick.tick(
            context,
            SingleShotGoal(
                goal.kick_power,
                target=wm.FramedPoint2(
                    context.world.snapshot.field.frame, self._locked_target
                ),
                duration_sec=goal.kick_duration_sec,
                attempt_id=self.attempt_id,
            ),
            command,
            motion=motion,
        )
        if result.status == SkillStatus.FAILED:
            if result.reason == "shot_activation_timeout":
                return self._hold(command, "kick_window_elapsed")
            raise UnusableEstimate(result.reason)
        if result.status == SkillStatus.SUCCEEDED:
            ball = self._optional(
                lambda: self._ball(context, context.world.snapshot.field.frame)
            )
            if ball is not None:
                self._attempted_ball = (
                    ball.value.position,
                    ball_spread(ball).position_std_m,
                )
            return self._hold(command, result.reason)
        return (
            replace(result, reason="kicking")
            if result.reason == "shot_active"
            else result
        )

    def _play_ball(self, context, goal, command, motion, *, restart, clearing):
        if context.world.match.restrictions.kick not in {"unknown", "allowed"}:
            return self._hold(command, "kick_restricted")
        try:
            local = self._local_ball(context)
        except UnusableEstimate as error:
            return self._search(context, command, str(error))
        spread = self.kick_policy.assess_ball(local)
        frame = context.world.snapshot.field.frame
        pose, ball = self._pose(context, frame), self._ball(context, frame)
        check_quality(ball, self.kick_policy.allowed_qualities, "ball")
        field_spread = ball_spread(ball).position_std_m
        if field_spread > self.policy.max_field_ball_std_m:
            raise UnusableEstimate("field_ball_position_uncertain")
        position = ball.value.position
        if self._attempted_ball is not None and self.state != "kick":
            # Timer expiry is not a successful kick. Demand new ball evidence
            # showing displacement before automatically arming another attempt.
            previous, previous_spread = self._attempted_ball
            change = hypot(position.x - previous.x, position.y - previous.y)
            if (
                change
                <= self.policy.rearm_distance_m
                + self.kick_policy.margin_sigma * (field_spread + previous_spread)
            ):
                return self._hold(command, "awaiting_ball_change")
            self._attempted_ball = None
        scene = self._scene(context, pose)
        if self.state == "kick":
            target = select_target(
                context.world.snapshot.field,
                ball,
                scene,
                self.tactics,
                clearing=clearing,
                locked=self._locked_target,
            )
            if target != self._locked_target:
                return self._hold(command, "kick_lane_changed")
            result = self._shot_tick(context, goal, command, motion)
            if command.kick_active:
                robot = pose.value.pose
                reason = scene.segment_reason(
                    (robot.x, robot.y), (position.x, position.y)
                )
                if reason:
                    raise UnusableEstimate(reason)
            return result
        target = select_target(
            context.world.snapshot.field,
            ball,
            scene,
            self.tactics,
            clearing=clearing,
            restart=restart
            and context.world.match.official.set_play
            in {"throw_in", "kick_in", "corner_kick"},
            locked=self._locked_target,
        )
        if self.state == "kick" and self._locked_target != target:
            return self._hold(command, "kick_lane_changed")
        if self._locked_target != target:
            self._approach_goal = self._anchor = None
        self._locked_target = target
        heading = atan2(target.y - position.y, target.x - position.x)
        local_point = local.value.position
        margin = self.kick_policy.margin_sigma * spread.position_std_m
        distance = hypot(local_point.x, local_point.y)
        bearing = abs(atan2(local_point.y, local_point.x))
        heading_error = abs(
            atan2(
                sin(heading - pose.value.pose.theta),
                cos(heading - pose.value.pose.theta),
            )
        )
        ready = (
            local_point.x > margin
            and distance + margin <= self.policy.kick_distance_m
            and bearing + atan2(margin, max(1e-9, distance - margin))
            <= self.policy.kick_bearing_rad
            and heading_error <= self.policy.kick_heading_rad
        )
        threatened = any(
            hypot(o.centre[0] - position.x, o.centre[1] - position.y) < 1.6 + o.radius_m
            for o in scene.obstacles
        )
        dribble = goal.play_style in {"dribble", "walk_through"} or (
            goal.play_style == "auto" and threatened
        )
        if (
            dribble
            and not restart
            and self.state != "kick"
            and local_point.x > margin
            and distance + margin < self.tactics.dribble_distance_m
            and abs(heading_error) < 1.0
            and (
                goal.play_style == "walk_through"
                or clearing
                or position.x
                < context.world.snapshot.field.length
                * self.tactics.dribble_kick_x_fraction
            )
        ):
            return self._dribble(
                context, goal, command, pose, ball, local, target, clearing=clearing
            )
        if self.state == "kick" or ready:
            if not motion.kick_ready:
                return self._hold(command, "kick_not_ready")
            aim_margin = self.kick_policy.assess_aim(pose, ball, target)
            if heading_error + aim_margin > self.policy.kick_heading_rad:
                return self._hold(command, "kick_alignment_uncertain")
            # Visual kicking may walk towards the ball. Check the whole approach
            # corridor with the same footprint, uncertainty and coverage policy.
            checked = self.navigation.tick(
                context, self._nav_goal(frame, pose.value.pose), command
            )
            if checked.status == SkillStatus.FAILED:
                raise UnusableEstimate(checked.reason)
            robot = pose.value.pose
            reason = self.navigation.evidence.scene.segment_reason(
                (robot.x, robot.y), (position.x, position.y)
            )
            if reason:
                raise UnusableEstimate(reason)
            if not ready:
                return self._hold(command, "kick_ball_left_window")
            if self.state != "kick":
                self.kick.on_exit()
                self._attempt_sequence += 1
                self.attempt_id = (
                    f"{context.world.snapshot.id.world_epoch}:"
                    f"{self._attempt_session}:{self._attempt_sequence}"
                )
                self._attempted_ball = (position, field_spread)
                self.state = "kick"
            return self._shot_tick(context, goal, command, motion)
        self.kick.cancel(command)
        self.state = "approach"
        if (
            self._anchor is None
            or hypot(position.x - self._anchor.x, position.y - self._anchor.y)
            > self.policy.retarget_distance_m
        ):
            self._anchor = position
            self._approach_goal = self._nav_goal(
                frame,
                wm.Pose2(
                    position.x - self.policy.approach_distance_m * cos(heading),
                    position.y - self.policy.approach_distance_m * sin(heading),
                    heading,
                ),
                ball_distance=0.35 if distance > 0.5 + margin else 0.0,
            )
        result = self.navigation.tick(context, self._approach_goal, command)
        if result.status == SkillStatus.FAILED:
            raise UnusableEstimate(result.reason)
        return SkillProgress(
            SkillStatus.RUNNING,
            reason="approaching"
            if result.status == SkillStatus.RUNNING
            else "awaiting_kick_alignment",
        )
