"""Bounded native-SDK driver for the reviewed K1 visual-kick V2 simulator profile.

No ROS or world-model objects cross this boundary. Construct in the independent
actuator process, not the behaviour loop. SDK callbacks provide measured state.
"""

from math import cos, isfinite, sin
from threading import Lock
from time import monotonic_ns, sleep, time_ns

from action.match_actuator import MotionSample


class BoosterMatchDriver:
    """Use named SDK channels and bounded RPCs; never fall back to an unnamed robot."""

    def __init__(self, robot, *, clock=monotonic_ns, sdk=None):
        if robot not in {"robot1", "robot2", "robot3", "robot4"}:
            raise ValueError("Choose a named simulated robot")
        if sdk is None:
            import booster_robotics_sdk_python as sdk
        self.sdk, self.clock = sdk, clock
        sdk.ChannelFactory.Instance().Init(0)
        self.client = sdk.B1LocoClient()
        self.client.InitWithName(robot)
        self.publisher = sdk.B1VisualKickReferencePublisher()
        self.publisher.InitChannelWithName(robot)
        self._lock = Lock()
        self._low = self._fall = self._state = None
        self._phase = (0, 0)
        self._armed = False
        self._mode_request = None
        self.subscriptions = []
        for cls, handler in (
            (sdk.B1LowStateSubscriber, self._on_low),
            (sdk.B1FallDownStateSubscriber, self._on_fall),
            (sdk.B1RobotStatesSubscriber, self._on_state),
            (sdk.B1RobocupBehaviorStatusSubscriber, self._on_phase),
        ):
            sub = cls(handler)
            sub.InitChannelWithName(robot)
            self.subscriptions.append(sub)

    def _on_low(self, message):
        if len(message.motor_state_serial) >= 2:
            with self._lock:
                tilt = tuple(message.imu_state.rpy[:2])
                self._low = (
                    self.clock(),
                    (message.motor_state_serial[1].q, message.motor_state_serial[0].q),
                    len(tilt) == 2 and all(isfinite(q) and abs(q) < 0.7 for q in tilt),
                )

    def _on_fall(self, message):
        with self._lock:
            self._fall = (
                self.clock(),
                message.fall_down_state == self.sdk.FallDownStateType.IS_READY,
            )

    def _on_state(self, message):
        with self._lock:
            self._state = (
                self.clock(),
                int(message.current_mode),
                int(message.current_body_control),
            )

    def _on_phase(self, message):
        with self._lock:
            self._phase = (int(message.status), self.clock())

    def sample(self):
        """Preserve fast joint/IMU and slower mode/fall receipts separately."""
        with self._lock:
            if any(v is None for v in (self._low, self._fall, self._state)):
                return None
            low, fall, state, phase = self._low, self._fall, self._state, self._phase
        mode, body = state[1:]
        # Pinned K1 simulator firmware reports 10 for soccer gait and 14 for
        # visual kick V2. The Python enum labels collide with older firmware;
        # do not generalise these values to another robot/firmware profile.
        return MotionSample(
            low[0],
            fall[1] and low[2],
            (mode == 4 and body in {10, 14}) or (mode == 2 and body == 12),
            mode == 4 and (body == 14 or phase[0] in {1, 2}),
            low[1],
            phase[0],
            phase[1],
            mode,
            body,
            min(fall[0], state[0]),
        )

    def _rpc(self, name, parameter):
        code = self.client.SendApiRequest(
            getattr(self.sdk.LocoApiId, name), parameter.to_json_str(), 20
        )
        if code != 0:
            raise RuntimeError(f"{name} rejected: {code}")

    def prepare(self):
        """Prepare modes before arming; feedback, not acknowledgements, confirms readiness."""
        if not self.client.WaitForService(5000):
            raise RuntimeError("Named simulator motion service unavailable")
        s = self.sdk
        self._rpc("kChangeMode", s.ChangeModeParameter(s.RobotMode.kPrepare))
        sleep(2)
        self._rpc("kChangeMode", s.ChangeModeParameter(s.RobotMode.kWalking))
        deadline = self.clock() + 5_000_000_000
        while self.clock() < deadline:
            sample = self.sample()
            if (
                sample
                and sample.ready
                and sample.mode == 2
                and sample.upright
                and self.clock() - sample.observed_ns < 150_000_000
                and self.clock() - sample.status_ns < 1_200_000_000
            ):
                self.disable_kick()
                self.move((0.0, 0.0, 0.0))
                return
            sleep(0.02)
        raise RuntimeError("SDK feedback did not confirm walking readiness")

    def ensure_mode(self, kick):
        """Request once and poll measured mode without blocking the lease watchdog."""
        target = 4 if kick else 2
        sample = self.sample()
        if sample and sample.mode == target:
            self._mode_request = None
            return True
        if self._mode_request is None or self._mode_request[0] != target:
            self.move((0.0, 0.0, 0.0))
            mode = self.sdk.RobotMode.kSoccer if kick else self.sdk.RobotMode.kWalking
            self._rpc("kChangeMode", self.sdk.ChangeModeParameter(mode))
            self._mode_request = (target, self.clock())
        elif self.clock() - self._mode_request[1] > 3_000_000_000:
            raise RuntimeError("SDK mode transition not confirmed")
        return False

    def move(self, velocity):
        self._rpc("kMove", self.sdk.MoveParameter(*velocity))

    def stop_body(self):
        """Zero motion and leave Soccer through the bounded Walking transition.

        Cancelling visual kicking alone can leave the Soccer controller settling
        after its inactive status. A stop uses the same zero-velocity Walking
        mode as a normal stand intent, including after the sender has expired.
        Never request a mode transition using stale or fallen feedback.
        """
        self.move((0.0, 0.0, 0.0))
        sample, now = self.sample(), self.clock()
        if (
            sample is not None
            and sample.upright
            and 0 <= now - sample.observed_ns <= 150_000_000
            and 0 <= now - sample.status_ns <= 1_200_000_000
        ):
            self.ensure_mode(False)

    def head(self, angles):
        self._rpc("kRotateHead", self.sdk.RotateHeadParameter(*angles))

    def enable_kick(self):
        # Mark the request as potentially active even if its response times out.
        self._armed = True
        self._rpc(
            "kVisualKick",
            self.sdk.VisualKickParameter(True, self.sdk.VisualKickVersion.kV2),
        )

    def disable_kick(self):
        sample = self.sample()
        if self._armed or (sample is not None and sample.kick_active):
            self._rpc(
                "kVisualKick",
                self.sdk.VisualKickParameter(False, self.sdk.VisualKickVersion.kV2),
            )
            self._armed = False

    def reference(self, kick):
        """Map the already-current body ball/aim to SDK Kick without reading odometry.

        The SDK requires a goal point as well as a bearing. Use its documented
        virtual-goal convention (8 m), refreshed from this intent's body aim.
        No ball coordinate is reprojected using a second, asynchronous pose.
        """
        direction, power, x, y = kick
        msg = self.sdk.Kick()
        stamp = self.sdk.Time()
        stamp.sec, stamp.nanosec = divmod(time_ns(), 1_000_000_000)
        header = self.sdk.Header()
        header.stamp = stamp
        msg.header = header
        # This is command publication time, not the ball's capture time. Its
        # input and command ages are bounded independently by the intent lease.
        msg.x, msg.y, msg.dir, msg.power = x, y, 0.0, power
        msg.goal_x, msg.goal_y = x + 8 * cos(direction), y + 8 * sin(direction)
        msg.robot_theta_to_field = -direction
        if not self.publisher.Write(msg):
            raise RuntimeError("Visual-kick reference publication failed")

    def close(self):
        try:
            self.disable_kick()
        finally:
            try:
                self.move((0.0, 0.0, 0.0))
            finally:
                for subscription in self.subscriptions:
                    subscription.CloseChannel()
                self.publisher.CloseChannel()
